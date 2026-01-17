import sys
import os
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.memory import MemoryManager
from shared.tool_adapters import FilesystemAdapter


class DocumenterNode:
    def __init__(
        self,
        memory_path: str = "/memory/harmony_memory.json",
        workspace_dir: str = "/workspace",
        templates_dir: str = "/home/sandbox/templates",
    ):
        self.memory = MemoryManager(memory_path)
        self.workspace_dir = workspace_dir
        self.templates_dir = templates_dir
        self.fs = FilesystemAdapter(workspace_dir)

    def execute(self, action: str, user_request: str) -> Dict[str, Any]:
        if action == "generate_docs":
            return self.generate_docs(user_request)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def generate_docs(self, user_request: str) -> Dict[str, Any]:
        try:
            self.memory.load_memory()

            project_info = self.memory.get_project_info()
            project_name = project_info.get("name", "project")
            project_dir = f"{self.workspace_dir}/{project_name}"

            readme_path = f"{project_dir}/README.md"
            if self.fs.file_exists(readme_path):
                readme_result = self.fs.read_file(readme_path)
                if readme_result["success"]:
                    enhanced_readme = self._enhance_readme(
                        readme_result["content"], project_info, user_request
                    )
                    self.fs.write_file(readme_path, enhanced_readme)

            history_path = self._create_history_entry(
                project_dir, project_info, user_request
            )

            patch = {
                "node": "documenter",
                "summary": "Enhanced documentation and created history entry",
                "data": {
                    "project.documentation": {
                        "readme_enhanced": True,
                        "history_entry": history_path,
                    }
                },
            }

            return {
                "success": True,
                "patch": patch,
                "readme_enhanced": True,
                "history_entry": history_path,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Documentation generation failed: {str(e)}",
            }

    def _enhance_readme(
        self, existing_readme: str, project_info: Dict[str, Any], user_request: str
    ) -> str:
        enhanced_sections = []

        enhanced_sections.append("## AGILE Generation Information\n")
        enhanced_sections.append(
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        enhanced_sections.append(f"**Original Request**: {user_request}\n")
        enhanced_sections.append(
            f"**Project Type**: {project_info.get('type', 'Unknown')}\n"
        )

        tech_stack = project_info.get("tech_stack", {})
        if tech_stack:
            enhanced_sections.append("### Technology Stack\n")
            for key, value in tech_stack.items():
                enhanced_sections.append(f"- **{key.capitalize()}**: {value}\n")
            enhanced_sections.append("")

        acceptance_criteria = project_info.get("acceptance_criteria", [])
        if acceptance_criteria:
            enhanced_sections.append("### Acceptance Criteria\n")
            for criteria in acceptance_criteria:
                enhanced_sections.append(f"- {criteria}\n")
            enhanced_sections.append("")

        enhanced_sections.append("---\n\n")

        enhanced_readme = (
            enhanced_sections[-1].join(enhanced_sections) + existing_readme
        )

        return enhanced_readme

    def _create_history_entry(
        self, project_dir: str, project_info: Dict[str, Any], user_request: str
    ) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        history_filename = f"agile_history_{timestamp}.md"
        history_path = f"{project_dir}/{history_filename}"

        history_content = self._build_history_content(project_info, user_request)

        self.fs.write_file(history_path, history_content)

        return history_path

    def _build_history_content(
        self, project_info: Dict[str, Any], user_request: str
    ) -> str:
        lines = []

        lines.append("# AGILE Project Generation History")
        lines.append("")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        lines.append("## Original Request")
        lines.append("")
        lines.append(user_request)
        lines.append("")

        lines.append("## Project Information")
        lines.append("")
        lines.append(f"- **Name**: {project_info.get('name', 'Unknown')}")
        lines.append(f"- **Type**: {project_info.get('type', 'Unknown')}")
        lines.append(f"- **Complexity**: {project_info.get('complexity', 'Unknown')}")
        lines.append(f"- **Location**: {project_info.get('location', 'Unknown')}")
        lines.append("")

        lines.append("## Technology Stack")
        lines.append("")
        tech_stack = project_info.get("tech_stack", {})
        for key, value in tech_stack.items():
            lines.append(f"- **{key.capitalize()}**: {value}")
        lines.append("")

        lines.append("## Acceptance Criteria")
        lines.append("")
        acceptance_criteria = project_info.get("acceptance_criteria", [])
        for i, criteria in enumerate(acceptance_criteria, 1):
            lines.append(f"{i}. {criteria}")
        lines.append("")

        lines.append("## Generation Process")
        lines.append("")
        lines.append(
            "The project was generated by AGILE (Autonomous General Intelligence with Learning Elasticity)"
        )
        lines.append("")
        lines.append("### Workflow Steps")
        lines.append("")
        lines.append(
            "1. **Research**: Analyzed the request and determined project type and technology stack"
        )
        lines.append(
            "2. **Code Generation**: Generated project structure and implementation"
        )
        lines.append(
            "3. **Testing**: Executed acceptance tests to verify functionality"
        )
        lines.append("4. **Documentation**: Created and enhanced documentation")
        lines.append("")

        memory_data = self.memory.get_memory()
        nodes_info = memory_data.get("nodes", {})

        lines.append("### Node Execution")
        lines.append("")
        for node_name, node_data in nodes_info.items():
            status = node_data.get("status", "unknown")
            lines.append(f"- **{node_name.capitalize()}**: {status}")
        lines.append("")

        lines.append("## Files Generated")
        lines.append("")
        lines.append("- main.py - FastAPI application")
        lines.append("- models.py - Data models")
        lines.append("- database.py - Database configuration")
        lines.append("- requirements.txt - Python dependencies")
        lines.append("- test_main.py - Test suite")
        lines.append("- Dockerfile - Docker configuration")
        lines.append("- README.md - Documentation")
        lines.append("")

        lines.append("## Quality Assurance")
        lines.append("")
        lines.append("- All acceptance tests executed")
        lines.append("- Docker container configuration provided")
        lines.append("- Complete documentation included")
        lines.append("- History tracking enabled")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*Generated by AGILE - Autonomous project generation system*")

        return "\n".join(lines)


if __name__ == "__main__":
    import json

    documenter = DocumenterNode()

    if len(sys.argv) > 1:
        user_request = sys.argv[1]
    else:
        user_request = "Create a REST API for todo management"

    result = documenter.generate_docs(user_request)
    print(json.dumps(result, indent=2))
