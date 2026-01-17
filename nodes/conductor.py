import sys
import os
import json
import time
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.memory import MemoryManager
from shared.history_logger import HistoryLogger
from shared.tool_adapters import DockerAdapter, FilesystemAdapter


class ConductorNode:
    def __init__(self):
        self.memory = MemoryManager()
        self.history_logger = HistoryLogger()
        self.docker = DockerAdapter()
        self.fs = FilesystemAdapter()
        self.action_log = []
        self.state = "IDLE"

    def setup(self):
        print("Setting up AGILE...")
        self.memory.load_memory()
        print(f"Memory initialized at {self.memory.memory_path}")
        print(f"History directory: {self.history_logger.history_dir}")
        print("AGILE setup complete")

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if request.get("type") != "start_project":
            return {"success": False, "error": "Invalid request type"}

        user_request = request.get("request", "")
        if not user_request:
            return {"success": False, "error": "No request provided"}

        start_time = time.time()

        try:
            self.state = "PLANNING"
            project_name = self._extract_project_name(user_request)
            project_dir = f"/workspace/{project_name}"

            self.memory.set_project_info(
                {
                    "name": project_name,
                    "description": user_request,
                    "type": "unknown",
                    "location": project_dir,
                    "created_at": datetime.now().isoformat(),
                    "status": "planning",
                }
            )

            self.memory.create_checkpoint("initial")

            workflow_steps = [
                ("researcher", "research_request"),
                ("coder", "generate_code"),
                ("tester", "run_tests"),
                ("documenter", "generate_docs"),
            ]

            results = {}
            success = True

            for node_name, action in workflow_steps:
                self.state = node_name.upper()
                result = self._execute_node(node_name, action, user_request)
                results[node_name] = result

                if not result.get("success"):
                    success = False
                    self._log_action(
                        node_name,
                        action,
                        {"request": user_request},
                        result,
                        time.time() - start_time,
                        False,
                    )
                    self.memory.restore_checkpoint("initial")
                    break

                self._log_action(
                    node_name,
                    action,
                    {"request": user_request},
                    result,
                    time.time() - start_time,
                    True,
                )

                patch = result.get("patch", {})
                if patch:
                    self.memory.apply_patch(patch)

            if success:
                self.state = "DOCUMENTING"
                final_report = self._generate_final_report(results)
                self.history_logger.generate_history_book(
                    self.memory.get_project_info(), self.action_log, final_report
                )

                self.memory.set_project_info({"status": "completed"})
                self.state = "DONE"

            total_duration = time.time() - start_time

            return {
                "success": success,
                "state": self.state,
                "results": results,
                "duration": total_duration,
                "project_location": project_dir if success else None,
                "history_book": "/reports/history/latest.md",
            }

        except Exception as e:
            self.state = "FAILED"
            error_msg = f"Conductor error: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}

    def _execute_node(
        self, node_name: str, action: str, user_request: str
    ) -> Dict[str, Any]:
        start_time = time.time()

        try:
            print(f"\n[Conductor] Executing {node_name}...")
            self.memory.set_node_status(node_name, "running")

            node_script = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), f"{node_name}.py"
            )

            memory_path = self.memory.memory_path
            workspace_dir = "/workspace"
            templates_dir = "/home/sandbox/templates"

            command = f"""python3 -c "
import sys
import os
import json
sys.path.insert(0, '{os.path.dirname(os.path.abspath(__file__))}')

from {node_name} import {node_name.capitalize()}Node

memory_path = '{memory_path}'
workspace_dir = '{workspace_dir}'
templates_dir = '{templates_dir}'
user_request = '{user_request}'

node = {node_name.capitalize()}Node(
    memory_path=memory_path,
    workspace_dir=workspace_dir,
    templates_dir=templates_dir
)

result = node.execute(action, user_request)
print(json.dumps(result))
"
"""

            volumes = [
                f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}:/home/sandbox",
                f"{os.path.dirname(self.memory.memory_path)}:/memory",
                f"{workspace_dir}:/workspace",
            ]

            result = self.docker.run_container(
                image="ubuntu:24.04",
                command=command,
                volumes=volumes,
                working_dir="/workspace",
            )

            duration = time.time() - start_time

            if result["success"]:
                try:
                    node_result = json.loads(result["stdout"])
                    self.memory.set_node_status(node_name, "completed")
                    return node_result
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": f"Invalid JSON output: {result['stdout']}",
                    }
            else:
                self.memory.set_node_status(node_name, "failed")
                return {
                    "success": False,
                    "error": result.get("stderr", "Unknown error"),
                }

        except Exception as e:
            self.memory.set_node_status(node_name, "failed")
            return {"success": False, "error": str(e)}

    def _log_action(
        self,
        node: str,
        action: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        duration: float,
        success: bool,
    ):
        entry = {
            "node": node,
            "action": action,
            "inputs": inputs,
            "outputs": outputs,
            "duration": duration,
            "success": success,
        }
        self.action_log.append(entry)

    def _generate_final_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        project_info = self.memory.get_project_info()

        test_results = results.get("tester", {})
        total_tests = test_results.get("tests_passed", 0) + test_results.get(
            "tests_failed", 0
        )
        all_passed = test_results.get("overall_status") == "all_tests_passed"

        return {
            "project_name": project_info.get("name", "Unknown"),
            "project_type": project_info.get("type", "Unknown"),
            "project_location": project_info.get("location", ""),
            "total_tests": total_tests,
            "tests_passed": test_results.get("tests_passed", 0),
            "tests_failed": test_results.get("tests_failed", 0),
            "all_tests_passed": all_passed,
            "status": "completed" if all_passed else "tests_failed",
        }

    def _extract_project_name(self, request: str) -> str:
        request_lower = request.lower()

        if "api" in request_lower and "todo" in request_lower:
            return "todo_api"
        elif "api" in request_lower:
            return "api_project"
        elif "cli" in request_lower:
            return "cli_tool"
        else:
            import hashlib

            hash_obj = hashlib.md5(request.encode())
            return f"project_{hash_obj.hexdigest()[:8]}"

    def get_status(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "memory_status": self.memory.get_memory().get("project", {}).get("status"),
            "nodes": {
                k: v["status"]
                for k, v in self.memory.get_memory().get("nodes", {}).items()
            },
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AGILE Conductor Node")
    parser.add_argument("--setup", action="store_true", help="Setup AGILE")
    parser.add_argument("--request", type=str, help="Project request")

    args = parser.parse_args()

    conductor = ConductorNode()

    if args.setup:
        conductor.setup()
    elif args.request:
        result = conductor.process_request(
            {"type": "start_project", "request": args.request}
        )
        print(json.dumps(result, indent=2))
    else:
        print(
            "Conductor ready. Use --setup to initialize or --request to start a project"
        )
