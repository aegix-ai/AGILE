import os
import json
import subprocess
from typing import Dict, List, Any
from shared.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("planner", "Task Planner & Coordinator")
        self.system_prompt = "You are a task planner. Analyze requests and create step-by-step execution plans. Respond with JSON containing 'steps' array and 'dependencies' dict."

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        request = task.get("request", "")
        if not request:
            return {"status": "error", "message": "No request provided"}

        self.log(f"Planning for request: {request[:100]}")

        prompt = f"Create a detailed execution plan for: {request}\n\nAvailable agents:\n- planner: Coordinates tasks\n- executor: Executes commands\n- analyzer: Analyzes data\n- researcher: Gathers information\n- monitor: Checks system status\n\nRespond with JSON structure."

        response = self.query_llm(prompt, self.system_prompt)

        try:
            plan = json.loads(response)
            steps = plan.get("steps", [])
            dependencies = plan.get("dependencies", {})

            for i, step in enumerate(steps):
                step_data = {
                    "type": "task",
                    "task_id": f"task_{int(time.time())}_{i}",
                    "request": step,
                    "reply_to": "planner",
                }

                target_agent = step.get("agent", "executor")
                self.send_message(target_agent, step_data)
                self.log(f"Assigned step {i + 1} to {target_agent}")

            return {"status": "success", "plan": plan, "steps_count": len(steps)}
        except Exception as e:
            self.log(f"Failed to parse plan: {str(e)}", "ERROR")
            return {
                "status": "error",
                "message": "Failed to create plan",
                "raw_response": response,
            }


if __name__ == "__main__":
    import time

    agent = PlannerAgent()
    agent.run()
