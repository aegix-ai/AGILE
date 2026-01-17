#!/usr/bin/env python3
"""
Test script for AGILE multi-agent system
Tests communication between agents
"""

import redis
import json
import time
import requests
from typing import Dict, Any


class AgentTester:
    def __init__(self):
        self.redis_host = "redis"
        self.redis_port = 6379
        self.redis_client = redis.Redis(
            host=self.redis_host, port=self.redis_port, decode_responses=True
        )
        self.ollama_url = "http://ollama:11434"

    def send_task(self, agent: str, request: str | Dict[str, Any]) -> str:
        message = {
            "type": "task",
            "request": request,
            "reply_to": "tester",
            "task_id": f"test_{int(time.time())}",
        }

        channel = f"agent:{agent}"
        self.redis_client.publish(channel, json.dumps(message))
        request_str = (
            str(request)[:50] if not isinstance(request, str) else request[:50]
        )
        print(f"[Tester] Sent task to {agent}: {request_str}...")

        return message["task_id"]

    def wait_for_result(self, timeout: int = 30) -> Dict[str, Any]:
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe("agent:tester")

        start_time = time.time()
        while time.time() - start_time < timeout:
            message = pubsub.get_message(timeout=1)
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                if data.get("type") == "task_result":
                    return data

        return {"status": "timeout", "message": "No response received"}

    def test_ollama(self) -> bool:
        print("\n[Test] Testing Ollama connection...")
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": "qwen2.5:0.5b", "prompt": "Say hello", "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            print(
                f"[Test] Ollama response: {result.get('response', 'No response')[:100]}"
            )
            return True
        except Exception as e:
            print(f"[Test] Ollama connection failed: {e}")
            return False

    def test_redis(self) -> bool:
        print("\n[Test] Testing Redis connection...")
        try:
            self.redis_client.ping()
            print("[Test] Redis connection successful")
            return True
        except Exception as e:
            print(f"[Test] Redis connection failed: {e}")
            return False

    def test_agent(self, agent: str) -> bool:
        print(f"\n[Test] Testing {agent} agent...")

        if agent == "planner":
            result = self.send_task("planner", "Create a plan to check system status")
        elif agent == "executor":
            result = self.send_task("executor", "List files in /app")
        elif agent == "analyzer":
            result = self.send_task(
                "analyzer", "Analyze this sample log output: ERROR something went wrong"
            )
        elif agent == "researcher":
            result = self.send_task("researcher", "What is machine learning?")
        elif agent == "monitor":
            result = self.send_task("monitor", {"check_type": "system"})
        else:
            print(f"[Test] Unknown agent: {agent}")
            return False

        response = self.wait_for_result()

        if response.get("status") == "success":
            print(f"[Test] {agent} agent test PASSED")
            print(f"       Result: {str(response.get('result', {}))[:200]}")
            return True
        else:
            print(f"[Test] {agent} agent test FAILED")
            print(f"       Error: {response}")
            return False

    def run_all_tests(self):
        print("=" * 60)
        print("AGILE Multi-Agent System Tests")
        print("=" * 60)

        results = {}

        results["redis"] = self.test_redis()
        results["ollama"] = self.test_ollama()

        if not results["redis"] or not results["ollama"]:
            print("\n[Error] Core services not available, skipping agent tests")
            return results

        results["planner"] = self.test_agent("planner")
        results["executor"] = self.test_agent("executor")
        results["analyzer"] = self.test_agent("analyzer")
        results["researcher"] = self.test_agent("researcher")
        results["monitor"] = self.test_agent("monitor")

        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        for test, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"{test:20s}: {status}")

        all_passed = all(results.values())
        print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

        return results


if __name__ == "__main__":
    tester = AgentTester()
    tester.run_all_tests()
