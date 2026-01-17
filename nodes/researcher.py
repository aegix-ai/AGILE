import sys
import os
import re
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.memory import MemoryManager


class ResearcherNode:
    def __init__(
        self,
        memory_path: str = "/memory/harmony_memory.json",
        workspace_dir: str = "/workspace",
        templates_dir: str = "/home/sandbox/templates",
    ):
        self.memory = MemoryManager(memory_path)
        self.workspace_dir = workspace_dir
        self.templates_dir = templates_dir

    def execute(self, action: str, user_request: str) -> Dict[str, Any]:
        if action == "research_request":
            return self.research_request(user_request)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def research_request(self, user_request: str) -> Dict[str, Any]:
        try:
            self.memory.load_memory()

            analysis = self._analyze_request(user_request)

            project_type = analysis["project_type"]
            complexity = analysis["complexity"]
            acceptance_criteria = analysis["acceptance_criteria"]

            tech_stack = {
                "backend": "FastAPI",
                "database": "SQLite",
                "testing": "pytest",
                "language": "Python 3.11",
            }

            patch = {
                "node": "researcher",
                "summary": f"Researched request: {user_request[:50]}...",
                "data": {
                    "project.type": project_type,
                    "project.complexity": complexity,
                    "project.tech_stack": tech_stack,
                    "project.acceptance_criteria": acceptance_criteria,
                },
            }

            self.memory.set_project_info(
                {
                    "type": project_type,
                    "complexity": complexity,
                    "tech_stack": tech_stack,
                    "acceptance_criteria": acceptance_criteria,
                }
            )

            return {"success": True, "patch": patch, "analysis": analysis}

        except Exception as e:
            return {"success": False, "error": f"Research failed: {str(e)}"}

    def _analyze_request(self, request: str) -> Dict[str, Any]:
        request_lower = request.lower()

        project_type = "fastapi-sqlite"
        complexity = "simple"
        acceptance_criteria = []

        if (
            "api" in request_lower
            or "rest" in request_lower
            or "endpoint" in request_lower
        ):
            project_type = "fastapi-sqlite"
            acceptance_criteria.append("API has proper endpoints")
            acceptance_criteria.append("API responds with proper status codes")
            acceptance_criteria.append("API accepts JSON input")

        if "crud" in request_lower or (
            "create" in request_lower
            and "read" in request_lower
            and "update" in request_lower
            and "delete" in request_lower
        ):
            acceptance_criteria.append(
                "Supports Create, Read, Update, Delete operations"
            )
            complexity = "medium"

        if "todo" in request_lower:
            acceptance_criteria.append("Has /todos endpoint for listing todos")
            acceptance_criteria.append("Has POST /todos endpoint for creating todos")
            acceptance_criteria.append(
                "Has GET /todos/{id} endpoint for retrieving todo"
            )
            acceptance_criteria.append("Has PUT /todos/{id} endpoint for updating todo")
            acceptance_criteria.append(
                "Has DELETE /todos/{id} endpoint for deleting todo"
            )

        if (
            "authentication" in request_lower
            or "auth" in request_lower
            or "login" in request_lower
        ):
            acceptance_criteria.append("Has authentication endpoints")
            complexity = "complex"

        if (
            "database" in request_lower
            or "db" in request_lower
            or "sql" in request_lower
        ):
            acceptance_criteria.append("Uses database for persistence")

        if "test" in request_lower or "testing" in request_lower:
            acceptance_criteria.append("Has comprehensive test coverage")

        if len(acceptance_criteria) > 5:
            complexity = "complex"
        elif len(acceptance_criteria) > 3:
            complexity = "medium"
        else:
            complexity = "simple"

        if not acceptance_criteria:
            acceptance_criteria = [
                "Project compiles/runs without errors",
                "Basic functionality works as expected",
            ]

        return {
            "project_type": project_type,
            "complexity": complexity,
            "acceptance_criteria": acceptance_criteria,
            "keywords": self._extract_keywords(request),
            "estimated_components": self._estimate_components(request_lower),
        }

    def _extract_keywords(self, request: str) -> list:
        keywords = []

        tech_keywords = [
            "api",
            "rest",
            "graphql",
            "web",
            "cli",
            "mobile",
            "desktop",
            "fastapi",
            "flask",
            "django",
            "express",
            "react",
            "angular",
            "sql",
            "nosql",
            "mongodb",
            "postgresql",
            "mysql",
            "sqlite",
            "docker",
            "kubernetes",
            "redis",
            "rabbitmq",
            "kafka",
        ]

        request_lower = request.lower()

        for keyword in tech_keywords:
            if keyword in request_lower:
                keywords.append(keyword)

        functional_keywords = re.findall(
            r"\b(user|auth|login|signup|profile|dashboard|admin|settings|todo|task|product|order|payment)\b",
            request_lower,
        )
        keywords.extend(set(functional_keywords))

        return list(set(keywords))

    def _estimate_components(self, request_lower: str) -> Dict[str, int]:
        components = {"endpoints": 0, "models": 0, "tests": 0}

        if "todo" in request_lower:
            components["endpoints"] = 5
            components["models"] = 1
            components["tests"] = 5
        elif "api" in request_lower:
            components["endpoints"] = 3
            components["models"] = 1
            components["tests"] = 3
        else:
            components["endpoints"] = 2
            components["models"] = 1
            components["tests"] = 2

        if "crud" in request_lower:
            components["endpoints"] = components["endpoints"] * 2

        return components


if __name__ == "__main__":
    import json

    researcher = ResearcherNode()

    if len(sys.argv) > 1:
        user_request = sys.argv[1]
    else:
        user_request = "Create a REST API for todo management with CRUD operations"

    result = researcher.research_request(user_request)
    print(json.dumps(result, indent=2))
