import os
import json
import subprocess
from typing import Dict, List, Any
from shared.base_agent import BaseAgent


class ExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__("executor", "Command Executor")
        self.system_prompt = "You are a command executor. Convert requests into safe shell commands. Only execute commands that are safe for a sandbox environment."

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        request = task.get("request", "")
        if not request:
            return {"status": "error", "message": "No request provided"}

        self.log(f"Executing: {request[:100]}")

        prompt = f"Convert this request to a safe shell command for Linux: {request}\n\nOnly return the command, no explanation."

        command = self.query_llm(prompt, self.system_prompt).strip()

        if not command or command.startswith("#"):
            return {"status": "error", "message": "No valid command generated"}

        try:
            self.log(f"Running command: {command}")
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            return {
                "status": "success",
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "command": command,
                "message": "Command timed out",
            }
        except Exception as e:
            return {"status": "error", "command": command, "message": str(e)}


if __name__ == "__main__":
    agent = ExecutorAgent()
    agent.run()
