import os
import json
import fcntl
import copy
from datetime import datetime
from typing import Dict, Any, Optional


class MemoryManager:
    def __init__(self, memory_path: str = "/memory/harmony_memory.json"):
        self.memory_path = memory_path
        self.memory: Dict[str, Any] = {}
        self.lock_file_path = f"{memory_path}.lock"

    def _acquire_lock(self):
        os.makedirs(os.path.dirname(self.lock_file_path), exist_ok=True)
        lock_file = open(self.lock_file_path, "w")
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            return lock_file
        except Exception as e:
            lock_file.close()
            raise Exception(f"Could not acquire lock: {str(e)}")

    def _release_lock(self, lock_file):
        if lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()
            try:
                os.remove(self.lock_file_path)
            except:
                pass

    def load_memory(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self.memory_path):
                self._create_default_memory()

            with open(self.memory_path, "r") as f:
                self.memory = json.load(f)

            return self.memory
        except json.JSONDecodeError:
            self._create_default_memory()
            return self.memory
        except Exception as e:
            raise Exception(f"Failed to load memory: {str(e)}")

    def _create_default_memory(self):
        self.memory = {
            "project": {
                "name": "",
                "description": "",
                "type": "",
                "location": "",
                "created_at": "",
                "status": "not_started",
            },
            "nodes": {
                "researcher": {"status": "idle", "patches": []},
                "coder": {"status": "idle", "patches": []},
                "tester": {"status": "idle", "patches": []},
                "documenter": {"status": "idle", "patches": []},
            },
            "containers": {"pool": {}, "active": {}},
            "history": {"entries": [], "current_session": datetime.now().isoformat()},
            "checkpoints": {},
        }
        self.save_memory()

    def _write_memory_file(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, "w") as f:
            json.dump(self.memory, f, indent=2)

    def save_memory(self) -> bool:
        lock_file = self._acquire_lock()

        try:
            self._write_memory_file()
            return True
        except Exception as e:
            raise Exception(f"Failed to save memory: {str(e)}")
        finally:
            self._release_lock(lock_file)

    def apply_patch(self, patch: Dict[str, Any]) -> bool:
        lock_file = self._acquire_lock()
        if lock_file is None:
            return False

        try:
            self.load_memory()
            node_name = patch.get("node", "unknown")

            if node_name not in self.memory["nodes"]:
                self.memory["nodes"][node_name] = {"status": "idle", "patches": []}

            patch_record = {
                "timestamp": datetime.now().isoformat(),
                "patch": patch,
                "applied": True,
            }
            self.memory["nodes"][node_name]["patches"].append(patch_record)

            for key, value in patch.get("data", {}).items():
                keys = key.split(".")
                current = self.memory
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value

            self.memory["history"]["entries"].append(
                {
                    "node": node_name,
                    "timestamp": datetime.now().isoformat(),
                    "action": "patch_applied",
                    "summary": patch.get("summary", ""),
                }
            )

            self.save_memory()
            return True
        except Exception as e:
            raise Exception(f"Failed to apply patch: {str(e)}")
        finally:
            self._release_lock(lock_file)

    def create_checkpoint(self, name: str) -> bool:
        try:
            checkpoint_data = copy.deepcopy(self.memory)
            self.memory["checkpoints"][name] = {
                "timestamp": datetime.now().isoformat(),
                "data": checkpoint_data,
            }
            self.save_memory()
            return True
        except Exception as e:
            raise Exception(f"Failed to create checkpoint: {str(e)}")

    def restore_checkpoint(self, name: str) -> bool:
        if name not in self.memory.get("checkpoints", {}):
            return False

        try:
            checkpoint_data = self.memory["checkpoints"][name]["data"]
            self.memory = copy.deepcopy(checkpoint_data)
            self.save_memory()
            return True
        except Exception as e:
            raise Exception(f"Failed to restore checkpoint: {str(e)}")

    def get_node_status(self, node_name: str) -> Dict[str, Any]:
        self.load_memory()
        if node_name in self.memory.get("nodes", {}):
            return self.memory["nodes"][node_name]
        return {"status": "unknown", "patches": []}

    def set_node_status(self, node_name: str, status: str) -> bool:
        try:
            self.load_memory()
            if node_name not in self.memory["nodes"]:
                self.memory["nodes"][node_name] = {"status": "idle", "patches": []}
            self.memory["nodes"][node_name]["status"] = status
            self.save_memory()
            return True
        except Exception as e:
            raise Exception(f"Failed to set node status: {str(e)}")

    def get_project_info(self) -> Dict[str, Any]:
        self.load_memory()
        return self.memory.get("project", {})

    def set_project_info(self, project_data: Dict[str, Any]) -> bool:
        try:
            self.load_memory()
            self.memory["project"].update(project_data)
            self.save_memory()
            return True
        except Exception as e:
            raise Exception(f"Failed to set project info: {str(e)}")

    def get_memory(self) -> Dict[str, Any]:
        return self.load_memory()

    def reset_memory(self):
        lock_file = self._acquire_lock()
        if lock_file is None:
            return False

        try:
            self._create_default_memory()
            return True
        finally:
            self._release_lock(lock_file)

    def get_history_entries(self, limit: Optional[int] = None) -> list:
        self.load_memory()
        entries = self.memory.get("history", {}).get("entries", [])
        if limit:
            return entries[-limit:]
        return entries

    def add_history_entry(self, entry: Dict[str, Any]):
        try:
            self.load_memory()
            if "history" not in self.memory:
                self.memory["history"] = {
                    "entries": [],
                    "current_session": datetime.now().isoformat(),
                }
            entry["timestamp"] = datetime.now().isoformat()
            self.memory["history"]["entries"].append(entry)
            self.save_memory()
        except Exception as e:
            raise Exception(f"Failed to add history entry: {str(e)}")
