import os
import json
import time
from typing import Dict, List, Any
from shared.base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("researcher", "Information Researcher")
        self.system_prompt = "You are an information researcher. Given a topic, provide comprehensive but concise information including key facts, relevant context, and useful resources."
        self.knowledge_base = {}

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        if not query:
            return {"status": "error", "message": "No query provided"}

        self.log(f"Researching: {query[:100]}")

        cache_key = query.lower().strip()
        if cache_key in self.knowledge_base:
            self.log("Found cached result")
            return {
                "status": "success",
                "cached": True,
                "result": self.knowledge_base[cache_key],
            }

        prompt = f"Provide a comprehensive overview of: {query}\n\nInclude:\n1. Key facts\n2. Important concepts\n3. Practical applications\n4. Related topics\n\nKeep it concise but informative."

        result = self.query_llm(prompt, self.system_prompt)

        self.knowledge_base[cache_key] = result

        return {
            "status": "success",
            "cached": False,
            "query": query,
            "result": result,
            "knowledge_base_size": len(self.knowledge_base),
        }

    def get_knowledge_summary(self) -> Dict[str, Any]:
        return {
            "total_queries": len(self.knowledge_base),
            "queries": list(self.knowledge_base.keys()),
        }


if __name__ == "__main__":
    agent = ResearcherAgent()
    agent.run()
