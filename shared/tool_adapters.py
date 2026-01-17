import os
import subprocess
import json
import shutil
from typing import Dict, List, Optional, Any


class FilesystemAdapter:
    def __init__(self, base_path: str = "/workspace"):
        self.base_path = base_path

    def _get_full_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_path, path)

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        full_path = self._get_full_path(path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
            return {"success": True, "path": full_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, path: str) -> Dict[str, Any]:
        full_path = self._get_full_path(path)
        try:
            with open(full_path, "r") as f:
                content = f.read()
            return {"success": True, "content": content, "path": full_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files(self, path: str = "") -> Dict[str, Any]:
        full_path = self._get_full_path(path)
        try:
            files = []
            if os.path.exists(full_path):
                for root, dirs, filenames in os.walk(full_path):
                    for filename in filenames:
                        files.append(os.path.join(root, filename))
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, path: str) -> Dict[str, Any]:
        full_path = self._get_full_path(path)
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
                return {"success": True, "path": full_path}
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
                return {"success": True, "path": full_path}
            else:
                return {"success": False, "error": "Path not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_directory(self, path: str) -> Dict[str, Any]:
        full_path = self._get_full_path(path)
        try:
            os.makedirs(full_path, exist_ok=True)
            return {"success": True, "path": full_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def file_exists(self, path: str) -> bool:
        full_path = self._get_full_path(path)
        return os.path.exists(full_path)


class DockerAdapter:
    def __init__(self):
        self.docker_path = "/usr/bin/docker"

    def run_container(
        self,
        image: str,
        command: str,
        volumes: Optional[List[str]] = None,
        working_dir: str = "/workspace",
        remove: bool = True,
    ) -> Dict[str, Any]:
        try:
            cmd = [self.docker_path, "run", "--rm"]

            if volumes:
                for volume in volumes:
                    cmd.extend(["-v", volume])

            cmd.extend(["-w", working_dir, image, "sh", "-c", command])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def build_image(
        self, dockerfile_path: str, tag: str, context: str = "."
    ) -> Dict[str, Any]:
        try:
            cmd = [self.docker_path, "build", "-f", dockerfile_path, "-t", tag, context]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Build timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def exec_in_container(self, container_id: str, command: str) -> Dict[str, Any]:
        try:
            cmd = [self.docker_path, "exec", container_id, "sh", "-c", command]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_logs(self, container_id: str, tail: int = 100) -> Dict[str, Any]:
        try:
            cmd = [self.docker_path, "logs", "--tail", str(tail), container_id]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            return {"success": True, "logs": result.stdout, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}


class GitAdapter:
    def __init__(self, base_path: str = "/workspace"):
        self.base_path = base_path

    def _run_git_command(
        self, command: List[str], cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        working_dir = cwd or self.base_path
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def init_repo(self, path: str = "") -> Dict[str, Any]:
        full_path = os.path.join(self.base_path, path) if path else self.base_path
        try:
            os.makedirs(full_path, exist_ok=True)
            result = self._run_git_command(["init"], cwd=full_path)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_all(self, path: str = "") -> Dict[str, Any]:
        full_path = os.path.join(self.base_path, path) if path else self.base_path
        result = self._run_git_command(["add", "."], cwd=full_path)
        return result

    def commit(self, message: str, path: str = "") -> Dict[str, Any]:
        full_path = os.path.join(self.base_path, path) if path else self.base_path
        result = self._run_git_command(["commit", "-m", message], cwd=full_path)
        return result

    def get_status(self, path: str = "") -> Dict[str, Any]:
        full_path = os.path.join(self.base_path, path) if path else self.base_path
        result = self._run_git_command(["status", "--porcelain"], cwd=full_path)
        return result

    def clone_repo(self, url: str, destination: str) -> Dict[str, Any]:
        full_path = os.path.join(self.base_path, destination)
        try:
            result = self._run_git_command(
                ["clone", url, full_path], cwd=self.base_path
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_log(self, path: str = "", limit: int = 10) -> Dict[str, Any]:
        full_path = os.path.join(self.base_path, path) if path else self.base_path
        result = self._run_git_command(["log", "--oneline", f"-{limit}"], cwd=full_path)
        return result
