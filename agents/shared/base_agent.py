import os
import json
import time
import requests
import redis
from typing import Dict, List, Optional, Any
from datetime import datetime


class BaseAgent:
    def __init__(self, agent_name: str, role: str):
        self.agent_name = agent_name
        self.role = role
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_client = redis.Redis(
            host=self.redis_host, port=self.redis_port, decode_responses=True
        )

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "agent": self.agent_name,
            "level": level,
            "message": message,
        }
        print(f"[{timestamp}] [{level}] {self.agent_name}: {message}")
        self.redis_client.lpush("system_logs", json.dumps(log_entry))

    def query_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            payload = {"model": "qwen2.5:0.5b", "prompt": prompt, "stream": False}

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(
                f"{self.ollama_url}/api/generate", json=payload, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            self.log(f"LLM query failed: {str(e)}", "ERROR")
            return ""

    def send_message(self, target_agent: str, message: Dict[str, Any]) -> bool:
        try:
            channel = f"agent:{target_agent}"
            message["from"] = self.agent_name
            message["timestamp"] = datetime.now().isoformat()
            self.redis_client.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            self.log(f"Failed to send message to {target_agent}: {str(e)}", "ERROR")
            return False

    def listen_for_messages(self, timeout: int = 10) -> Optional[Dict[str, Any]]:
        try:
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe(f"agent:{self.agent_name}")
            message = pubsub.get_message(timeout=timeout)
            if message and message["type"] == "message":
                return json.loads(message["data"])
            return None
        except Exception as e:
            self.log(f"Failed to receive message: {str(e)}", "ERROR")
            return None

    def broadcast(self, message: Dict[str, Any]) -> bool:
        try:
            channel = "agent:broadcast"
            message["from"] = self.agent_name
            message["timestamp"] = datetime.now().isoformat()
            self.redis_client.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            self.log(f"Failed to broadcast message: {str(e)}", "ERROR")
            return False

    def get_state(self) -> Dict[str, Any]:
        return {"agent_name": self.agent_name, "role": self.role, "status": "active"}

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.log(f"Executing task: {task.get('type', 'unknown')}")
        result = self.process_task(task)
        self.log(f"Task completed: {result.get('status', 'unknown')}")
        return result

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement process_task")

    def run(self):
        self.log(f"Starting {self.role} agent")
        while True:
            try:
                message = self.listen_for_messages()
                if message and message.get("type") == "task":
                    result = self.execute_task(message)
                    if "reply_to" in message:
                        self.send_message(
                            message["reply_to"],
                            {
                                "type": "task_result",
                                "task_id": message.get("task_id"),
                                "result": result,
                            },
                        )
            except KeyboardInterrupt:
                self.log("Shutting down")
                break
            except Exception as e:
                self.log(f"Error in main loop: {str(e)}", "ERROR")
                time.sleep(5)
