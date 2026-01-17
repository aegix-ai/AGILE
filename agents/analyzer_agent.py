import os
import json
import re
from typing import Dict, List, Any
from shared.base_agent import BaseAgent


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("analyzer", "Data Analyzer")
        self.system_prompt = "You are a data analyzer. Examine logs, outputs, and data. Provide insights, patterns, and summaries. Respond with clear, actionable analysis."

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        data = task.get("data", "")
        data_type = task.get("data_type", "text")
        analysis_type = task.get("analysis_type", "summary")

        if not data:
            return {"status": "error", "message": "No data provided"}

        self.log(f"Analyzing {data_type} data ({len(str(data))} chars)")

        prompt = f"Analyze this {data_type} data and provide a {analysis_type}:\n\n{data[:2000]}\n\nFocus on patterns, errors, and key insights."

        analysis = self.query_llm(prompt, self.system_prompt)

        if analysis_type == "summary":
            summary = self._generate_summary(data)
            return {
                "status": "success",
                "analysis": analysis,
                "summary": summary,
                "data_length": len(str(data)),
            }

        return {
            "status": "success",
            "analysis": analysis,
            "data_type": data_type,
            "data_length": len(str(data)),
        }

    def _generate_summary(self, data: str) -> Dict[str, Any]:
        lines = str(data).split("\n")
        return {
            "total_lines": len(lines),
            "non_empty_lines": len([l for l in lines if l.strip()]),
            "errors_found": len([l for l in lines if "error" in l.lower()]),
            "warnings_found": len([l for l in lines if "warn" in l.lower()]),
        }


if __name__ == "__main__":
    agent = AnalyzerAgent()
    agent.run()
