import sys
import os
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.memory import MemoryManager
from shared.tool_adapters import FilesystemAdapter


class CoderNode:
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
        if action == "generate_code":
            return self.generate_code(user_request)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def generate_code(self, user_request: str) -> Dict[str, Any]:
        try:
            self.memory.load_memory()

            project_info = self.memory.get_project_info()
            project_name = project_info.get("name", "project")
            project_type = project_info.get("type", "fastapi-sqlite")
            project_dir = os.path.abspath(
                os.path.join(self.workspace_dir, project_name)
            )

            os.makedirs(project_dir, exist_ok=True)

            if project_type == "fastapi-sqlite":
                generated_files = self._generate_fastapi_sqlite(
                    project_dir, user_request
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported project type: {project_type}",
                }

            patch = {
                "node": "coder",
                "summary": f"Generated {project_type} project with {len(generated_files)} files",
                "data": {
                    "project.generated_files": generated_files,
                    "project.files_count": len(generated_files),
                },
            }

            return {
                "success": True,
                "patch": patch,
                "project_location": project_dir,
                "generated_files": generated_files,
                "files_count": len(generated_files),
            }

        except Exception as e:
            return {"success": False, "error": f"Code generation failed: {str(e)}"}

    def _generate_fastapi_sqlite(self, project_dir: str, user_request: str) -> list:
        generated_files = []

        main_py = self._get_fastapi_main_content(user_request)
        self.fs.write_file(f"{project_dir}/main.py", main_py)
        generated_files.append("main.py")

        models_py = self._get_fastapi_models_content()
        self.fs.write_file(f"{project_dir}/models.py", models_py)
        generated_files.append("models.py")

        database_py = self._get_fastapi_database_content()
        self.fs.write_file(f"{project_dir}/database.py", database_py)
        generated_files.append("database.py")

        requirements_txt = self._get_fastapi_requirements_content()
        self.fs.write_file(f"{project_dir}/requirements.txt", requirements_txt)
        generated_files.append("requirements.txt")

        test_main_py = self._get_fastapi_test_content()
        self.fs.write_file(f"{project_dir}/test_main.py", test_main_py)
        generated_files.append("test_main.py")

        dockerfile = self._get_fastapi_dockerfile_content()
        self.fs.write_file(f"{project_dir}/Dockerfile", dockerfile)
        generated_files.append("Dockerfile")

        readme_md = self._get_fastapi_readme_content(user_request)
        self.fs.write_file(f"{project_dir}/README.md", readme_md)
        generated_files.append("README.md")

        return generated_files

    def _get_fastapi_main_content(self, user_request: str) -> str:
        return """from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from database import engine, Base
from models import Todo

app = FastAPI(title="Todo API", version="1.0.0")

Base.metadata.create_all(bind=engine)

class TodoCreate(BaseModel):
    title: str
    description: str = ""

class TodoUpdate(BaseModel):
    title: str = None
    description: str = None
    completed: bool = None

@app.get("/", tags=["root"])
async def root():
    return {"message": "Todo API is running", "version": "1.0.0"}

@app.get("/todos", response_model=List[Todo], tags=["todos"])
async def get_todos():
    from database import SessionLocal
    db = SessionLocal()
    todos = db.query(Todo).all()
    db.close()
    return todos

@app.get("/todos/{todo_id}", response_model=Todo, tags=["todos"])
async def get_todo(todo_id: int):
    from database import SessionLocal
    db = SessionLocal()
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    db.close()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=Todo, status_code=201, tags=["todos"])
async def create_todo(todo: TodoCreate):
    from database import SessionLocal
    db = SessionLocal()
    db_todo = Todo(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    db.close()
    return db_todo

@app.put("/todos/{todo_id}", response_model=Todo, tags=["todos"])
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    from database import SessionLocal
    db = SessionLocal()
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not db_todo:
        db.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todo_update.title is not None:
        db_todo.title = todo_update.title
    if todo_update.description is not None:
        db_todo.description = todo_update.description
    if todo_update.completed is not None:
        db_todo.completed = todo_update.completed
    
    db.commit()
    db.refresh(db_todo)
    db.close()
    return db_todo

@app.delete("/todos/{todo_id}", tags=["todos"])
async def delete_todo(todo_id: int):
    from database import SessionLocal
    db = SessionLocal()
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not db_todo:
        db.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    db.close()
    return {"message": "Todo deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

    def _get_fastapi_models_content(self) -> str:
        return """from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel

class Todo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False

    class Config:
        from_attributes = True

class TodoDB:
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
"""

    def _get_fastapi_database_content(self) -> str:
        return """from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

    def _get_fastapi_requirements_content(self) -> str:
        return """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pytest==7.4.3
httpx==0.25.1
"""

    def _get_fastapi_test_content(self) -> str:
        return """import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_todo():
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo"
    }
    response = client.post("/todos", json=todo_data)
    assert response.status_code == 201
    assert response.json()["title"] == "Test Todo"
    assert response.json()["completed"] == False

def test_get_todo():
    create_response = client.post("/todos", json={"title": "Get Test", "description": "Test"})
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]
    
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get Test"

def test_update_todo():
    create_response = client.post("/todos", json={"title": "Update Test", "description": "Test"})
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]
    
    update_data = {"title": "Updated Title", "completed": True}
    response = client.put(f"/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["completed"] == True

def test_delete_todo():
    create_response = client.post("/todos", json={"title": "Delete Test", "description": "Test"})
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]
    
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404

def test_get_nonexistent_todo():
    response = client.get("/todos/99999")
    assert response.status_code == 404
"""

    def _get_fastapi_dockerfile_content(self) -> str:
        return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    def _get_fastapi_readme_content(self, user_request: str) -> str:
        return f"""# Todo API

FastAPI-based REST API for todo management.

## Description

This project was generated for: {user_request}

## Features

- Create, read, update, and delete todos
- SQLite database for persistence
- Fast API responses with proper status codes
- Docker support for easy deployment

## Installation

### Using Python

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Using Docker

```bash
docker build -t todo-api .
docker run -p 8000:8000 todo-api
```

## API Endpoints

### GET /
Root endpoint

### GET /todos
Get all todos

### GET /todos/{{id}}
Get a specific todo by ID

### POST /todos
Create a new todo
```json
{{
  "title": "Todo title",
  "description": "Todo description"
}}
```

### PUT /todos/{{id}}
Update a todo
```json
{{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}}
```

### DELETE /todos/{{id}}
Delete a todo

## Testing

```bash
pytest test_main.py
```

## Development

The API runs on `http://localhost:8000`

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
"""


if __name__ == "__main__":
    import json

    coder = CoderNode()

    if len(sys.argv) > 1:
        user_request = sys.argv[1]
    else:
        user_request = "Create a REST API for todo management"

    result = coder.generate_code(user_request)
    print(json.dumps(result, indent=2))
