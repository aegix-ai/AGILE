import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class HistoryLogger:
    def __init__(self, history_dir: str = "/reports/history"):
        self.history_dir = history_dir
        os.makedirs(self.history_dir, exist_ok=True)

    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def record_action(
        self,
        node: str,
        action: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        duration: float,
        success: bool,
    ) -> str:
        timestamp = self._get_timestamp()

        entry = {
            "timestamp": timestamp,
            "node": node,
            "action": action,
            "inputs": inputs,
            "outputs": outputs,
            "duration": duration,
            "success": success,
        }

        return self._write_entry(entry)

    def _write_entry(self, entry: Dict[str, Any]) -> str:
        timestamp = entry.get("timestamp", self._get_timestamp())
        filename = f"{timestamp}.json"
        filepath = os.path.join(self.history_dir, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(entry, f, indent=2)
            return filepath
        except Exception as e:
            print(f"Failed to write history entry: {str(e)}")
            return ""

    def generate_history_book(
        self,
        project_info: Dict[str, Any],
        entries: List[Dict[str, Any]],
        final_report: Dict[str, Any],
    ) -> str:
        timestamp = self._get_timestamp()
        filename = f"history_book_{timestamp}.md"
        filepath = os.path.join(self.history_dir, filename)

        content = self._build_history_markdown(project_info, entries, final_report)

        try:
            with open(filepath, "w") as f:
                f.write(content)

            latest_link = os.path.join(self.history_dir, "latest.md")
            with open(latest_link, "w") as f:
                f.write(content)

            return filepath
        except Exception as e:
            print(f"Failed to generate history book: {str(e)}")
            return ""

    def _build_history_markdown(
        self,
        project_info: Dict[str, Any],
        entries: List[Dict[str, Any]],
        final_report: Dict[str, Any],
    ) -> str:
        lines = []

        lines.append("# AGILE History Book")
        lines.append("")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        if project_info:
            lines.append("## Project Information")
            lines.append("")
            lines.append(f"- **Name**: {project_info.get('name', 'N/A')}")
            lines.append(f"- **Type**: {project_info.get('type', 'N/A')}")
            lines.append(f"- **Description**: {project_info.get('description', 'N/A')}")
            lines.append(f"- **Location**: {project_info.get('location', 'N/A')}")
            lines.append(f"- **Status**: {project_info.get('status', 'N/A')}")
            lines.append("")

        lines.append("## Action Log")
        lines.append("")

        for entry in entries:
            lines.append(f"### {entry.get('timestamp', 'Unknown Time')}")
            lines.append("")
            lines.append(f"**Node**: {entry.get('node', 'Unknown')}")
            lines.append(f"**Action**: {entry.get('action', 'Unknown')}")
            lines.append(f"**Duration**: {entry.get('duration', 0):.2f}s")
            lines.append(
                f"**Status**: {'✓ Success' if entry.get('success') else '✗ Failed'}"
            )
            lines.append("")

            if entry.get("inputs"):
                lines.append("**Inputs**:")
                lines.append("```json")
                lines.append(json.dumps(entry["inputs"], indent=2))
                lines.append("```")
                lines.append("")

            if entry.get("outputs"):
                lines.append("**Outputs**:")
                lines.append("```json")
                lines.append(json.dumps(entry["outputs"], indent=2))
                lines.append("```")
                lines.append("")

            if entry.get("error"):
                lines.append(f"**Error**: {entry['error']}")
                lines.append("")

            lines.append("---")
            lines.append("")

        if final_report:
            lines.append("## Final Report")
            lines.append("")
            for key, value in final_report.items():
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
            lines.append("")

        lines.append("## Summary")
        lines.append("")
        successful = sum(1 for e in entries if e.get("success"))
        total = len(entries)
        total_duration = sum(e.get("duration", 0) for e in entries)

        lines.append(f"- **Total Actions**: {total}")
        lines.append(f"- **Successful**: {successful}")
        lines.append(f"- **Failed**: {total - successful}")
        lines.append(f"- **Total Duration**: {total_duration:.2f}s")
        lines.append(
            f"- **Success Rate**: {(successful / total * 100):.1f}%"
            if total > 0
            else "- Success Rate: N/A"
        )
        lines.append("")

        return "\n".join(lines)

    def get_latest_history(self) -> Optional[str]:
        try:
            latest_link = os.path.join(self.history_dir, "latest.md")
            if os.path.exists(latest_link):
                with open(latest_link, "r") as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Failed to get latest history: {str(e)}")
            return None

    def list_history_files(self) -> List[str]:
        try:
            files = sorted(
                [f for f in os.listdir(self.history_dir) if f.endswith(".md")]
            )
            return files
        except Exception as e:
            print(f"Failed to list history files: {str(e)}")
            return []

    def clear_history(self) -> bool:
        try:
            for filename in os.listdir(self.history_dir):
                filepath = os.path.join(self.history_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
            return True
        except Exception as e:
            print(f"Failed to clear history: {str(e)}")
            return False
