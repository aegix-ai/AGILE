import os
import json
import psutil
import time
from typing import Dict, List, Any
from shared.base_agent import BaseAgent


class MonitorAgent(BaseAgent):
    def __init__(self):
        super().__init__("monitor", "System Monitor")
        self.system_prompt = "You are a system monitor. Analyze system metrics and provide health assessments. Alert on issues and suggest optimizations."
        self.alert_thresholds = {
            "cpu_percent": 90,
            "memory_percent": 90,
            "disk_percent": 85,
        }

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        check_type = task.get("check_type", "system")

        if check_type == "system":
            return self._check_system()
        elif check_type == "agents":
            return self._check_agents()
        elif check_type == "logs":
            return self._check_logs()
        else:
            return {"status": "error", "message": f"Unknown check type: {check_type}"}

    def _check_system(self) -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        status = "healthy"
        alerts = []

        if cpu_percent > self.alert_thresholds["cpu_percent"]:
            status = "warning"
            alerts.append(f"High CPU usage: {cpu_percent}%")

        if memory.percent > self.alert_thresholds["memory_percent"]:
            status = "warning"
            alerts.append(f"High memory usage: {memory.percent}%")

        if disk.percent > self.alert_thresholds["disk_percent"]:
            status = "critical"
            alerts.append(f"High disk usage: {disk.percent}%")

        metrics = {
            "cpu": {"percent": cpu_percent, "cores": psutil.cpu_count()},
            "memory": {
                "percent": memory.percent,
                "available": memory.available,
                "total": memory.total,
            },
            "disk": {
                "percent": disk.percent,
                "free": disk.free,
                "used": disk.used,
                "total": disk.total,
            },
        }

        self.log(f"System check: {status}")

        return {
            "status": "success",
            "system_status": status,
            "alerts": alerts,
            "metrics": metrics,
        }

    def _check_agents(self) -> Dict[str, Any]:
        agent_list = ["planner", "executor", "analyzer", "researcher", "monitor"]
        active_agents = []

        for agent in agent_list:
            try:
                channel = f"agent:{agent}"
                message = {"type": "health_check", "from": "monitor"}
                self.send_message(agent, message)
                active_agents.append(agent)
            except Exception as e:
                self.log(f"Agent {agent} not responding: {str(e)}", "WARNING")

        return {
            "status": "success",
            "active_agents": active_agents,
            "total_agents": len(agent_list),
        }

    def _check_logs(self) -> Dict[str, Any]:
        try:
            logs = self.redis_client.lrange("system_logs", 0, 10)
            recent_errors = [
                json.loads(log) for log in logs if '"level": "ERROR"' in log
            ]

            return {
                "status": "success",
                "recent_log_count": len(logs),
                "error_count": len(recent_errors),
                "errors": recent_errors[:5],
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to check logs: {str(e)}"}


if __name__ == "__main__":
    agent = MonitorAgent()
    agent.run()
