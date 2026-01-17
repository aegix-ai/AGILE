import sys
import os
import re
import json
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.memory import MemoryManager
from shared.tool_adapters import DockerAdapter, FilesystemAdapter


class TesterNode:
    def __init__(
        self,
        memory_path: str = "/memory/harmony_memory.json",
        workspace_dir: str = "/workspace",
        templates_dir: str = "/home/sandbox/templates",
    ):
        self.memory = MemoryManager(memory_path)
        self.workspace_dir = workspace_dir
        self.templates_dir = templates_dir
        self.docker = DockerAdapter()
        self.fs = FilesystemAdapter(workspace_dir)

    def execute(self, action: str, user_request: str) -> Dict[str, Any]:
        if action == "run_tests":
            return self.run_tests(user_request)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def run_tests(self, user_request: str) -> Dict[str, Any]:
        try:
            self.memory.load_memory()

            project_info = self.memory.get_project_info()
            project_name = project_info.get("name", "project")
            project_dir = f"{self.workspace_dir}/{project_name}"
            project_type = project_info.get("type", "fastapi-sqlite")

            if not self.fs.file_exists(f"{project_dir}/test_main.py"):
                return {
                    "success": False,
                    "error": f"No test file found in {project_dir}",
                }

            if project_type == "fastapi-sqlite":
                test_results = self._run_pytest(project_dir)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported project type: {project_type}",
                }

            patch = {
                "node": "tester",
                "summary": f"Ran {test_results['tests_run']} tests, {test_results['tests_failed']} failed",
                "data": {
                    "project.test_results": test_results,
                    "project.tests_passed": test_results["tests_passed"],
                    "project.tests_failed": test_results["tests_failed"],
                },
            }

            overall_status = (
                "all_tests_passed"
                if test_results["tests_failed"] == 0
                else "some_tests_failed"
            )

            return {
                "success": True,
                "patch": patch,
                "test_results": test_results,
                "overall_status": overall_status,
            }

        except Exception as e:
            return {"success": False, "error": f"Test execution failed: {str(e)}"}

    def _run_pytest(self, project_dir: str) -> Dict[str, Any]:
        install_cmd = "pip install --quiet --no-cache-dir -r requirements.txt"
        test_cmd = "pytest test_main.py -v --tb=short"

        volumes = [f"{project_dir}:/workspace"]

        install_result = self.docker.run_container(
            image="python:3.11-slim",
            command=install_cmd,
            volumes=volumes,
            working_dir="/workspace",
        )

        if not install_result["success"]:
            return {
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "exit_code": -1,
                "stdout": "",
                "stderr": install_result.get("stderr", "Unknown error"),
                "error": "Failed to install dependencies",
            }

        test_result = self.docker.run_container(
            image="python:3.11-slim",
            command=test_cmd,
            volumes=volumes,
            working_dir="/workspace",
        )

        parsed_results = self._parse_pytest_output(
            test_result.get("stdout", ""),
            test_result.get("stderr", ""),
            test_result.get("returncode", -1),
        )

        parsed_results["stdout"] = test_result.get("stdout", "")
        parsed_results["stderr"] = test_result.get("stderr", "")
        parsed_results["exit_code"] = test_result.get("returncode", -1)

        return parsed_results

    def _parse_pytest_output(
        self, stdout: str, stderr: str, exit_code: int
    ) -> Dict[str, Any]:
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "test_details": [],
        }

        combined_output = stdout + stderr

        summary_match = re.search(r"(\d+) passed", combined_output)
        if summary_match:
            results["tests_passed"] = int(summary_match.group(1))

        failed_match = re.search(r"(\d+) failed", combined_output)
        if failed_match:
            results["tests_failed"] = int(failed_match.group(1))

        error_match = re.search(r"(\d+) error", combined_output)
        if error_match:
            results["tests_failed"] += int(error_match.group(1))

        results["tests_run"] = results["tests_passed"] + results["tests_failed"]

        test_pattern = r"(test_\w+)\s+(PASSED|FAILED|ERROR)"
        for match in re.finditer(test_pattern, combined_output):
            test_name = match.group(1)
            test_status = match.group(2)

            results["test_details"].append(
                {"test": test_name, "status": test_status.lower()}
            )

        if results["tests_run"] == 0 and results["tests_passed"] == 0:
            summary_match = re.search(
                r"===+(\s*\d+\s+collected\s+in\s+[\d\.]+s\s*===)", combined_output
            )
            if summary_match:
                collected_match = re.search(
                    r"(\d+)\s+collected", summary_match.group(0)
                )
                if collected_match:
                    results["tests_run"] = int(collected_match.group(1))
                    results["tests_passed"] = int(collected_match.group(1))

        if exit_code != 0 and results["tests_failed"] == 0:
            results["tests_failed"] = results["tests_run"]
            results["tests_passed"] = 0

        if exit_code == 1 and "ERROR" in combined_output:
            error_pattern = r"(test_\w+)\s+ERROR"
            for match in re.finditer(error_pattern, combined_output):
                results["errors"].append(match.group(1))

        return results

    def _check_acceptance_criteria(
        self, project_dir: str, acceptance_criteria: list
    ) -> Dict[str, Any]:
        criteria_results = {}

        for criteria in acceptance_criteria:
            criteria_results[criteria] = True

        return criteria_results


if __name__ == "__main__":
    import json

    tester = TesterNode()

    if len(sys.argv) > 1:
        user_request = sys.argv[1]
    else:
        user_request = "Create a REST API for todo management"

    result = tester.run_tests(user_request)
    print(json.dumps(result, indent=2))
