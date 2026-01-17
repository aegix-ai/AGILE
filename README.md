# AGILE

AGILE is a multi-agent experimental framework designed for running and orchestrating multiple autonomous agents within a controlled Kubernetes cluster inside a Docker sandbox.

## Overview

AGILE provides a systemized environment for deploying and managing multiple autonomous agents. The framework isolates agent execution within a Docker-based sandbox that contains a Kubernetes (kind) cluster, enabling comprehensive multi-agent experimentation while maintaining safety and control.

## Architecture

The AGILE system consists of:

- **Sandbox Container**: Ubuntu-based Docker container with privileged execution
- **Kubernetes Cluster**: kind (Kubernetes in Docker) cluster running inside the sandbox
- **Message Bus**: Redis for inter-agent communication
- **LLM Service**: Ollama running qwen2.5 0.5B model
- **Five Specialized Agents**: Planner, Executor, Analyzer, Researcher, and Monitor agents

## Agents

### 1. Planner Agent
- **Role**: Task planning and coordination
- **Function**: Analyzes requests and creates step-by-step execution plans, delegates tasks to other agents
- **LLM Usage**: Generates structured execution plans

### 2. Executor Agent
- **Role**: Command execution
- **Function**: Executes shell commands within the sandbox environment
- **Privilege Level**: Sandbox-restricted (cannot access host OS)
- **LLM Usage**: Converts natural language requests to shell commands

### 3. Analyzer Agent
- **Role**: Data analysis and log processing
- **Function**: Analyzes logs, outputs, and data for patterns, errors, and insights
- **LLM Usage**: Provides detailed analysis and summaries

### 4. Researcher Agent
- **Role**: Information gathering
- **Function**: Researches topics and provides comprehensive information
- **LLM Usage**: Generates informative responses on various topics
- **Caching**: Maintains knowledge base for cached queries

### 5. Monitor Agent
- **Role**: System health monitoring
- **Function**: Monitors system metrics, agent status, and logs
- **LLM Usage**: Provides health assessments and alerts
- **System Access**: Uses psutil for system metrics (CPU, memory, disk)

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Sandbox

```bash
cd sandbox
docker-compose up -d
```

This will build and start the sandbox container.

### Accessing the Sandbox

```bash
docker exec -it agile-sandbox /bin/bash
```

### Setting Up the Agent System

Once inside the sandbox, run:

```bash
cd /home/sandbox
chmod +x setup-agents.sh
./setup-agents.sh
```

This script will:
1. Create a kind Kubernetes cluster
2. Deploy Redis message bus
3. Deploy Ollama with qwen2.5 0.5B model
4. Deploy all five agents
5. Wait for services to be ready

### Testing the Agents

After setup, test the system:

```bash
python3 test-agents.py
```

This will test:
- Redis connectivity
- Ollama connectivity
- All five agent functions

### Viewing Agent Logs

```bash
kubectl logs -f deployment/planner-agent
kubectl logs -f deployment/executor-agent
kubectl logs -f deployment/analyzer-agent
kubectl logs -f deployment/researcher-agent
kubectl logs -f deployment/monitor-agent
```

### Checking System Status

```bash
kubectl get pods
kubectl get services
```

## Security & Isolation

The system is designed with multiple layers of isolation:

1. **Host OS**: Protected by Docker container boundaries
2. **Sandbox Container**: Privileged only within itself, not on host
3. **Kubernetes Cluster**: Isolated within the sandbox
4. **Agent Pods**: Each agent runs in its own pod with resource limits
5. **Command Privileges**: Executor agent commands are restricted to the sandbox environment

## Project Structure

```
AGILE/
├── sandbox/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── setup-agents.sh
│   └── test-agents.py
├── kubernetes/
│   ├── redis.yaml
│   ├── ollama.yaml
│   ├── planner-agent.yaml
│   ├── executor-agent.yaml
│   ├── analyzer-agent.yaml
│   ├── researcher-agent.yaml
│   └── monitor-agent.yaml
├── agents/
│   ├── shared/
│   │   ├── __init__.py
│   │   └── base_agent.py
│   ├── planner_agent.py
│   ├── executor_agent.py
│   ├── analyzer_agent.py
│   ├── researcher_agent.py
│   ├── monitor_agent.py
│   └── requirements.txt
└── README.md
```

## Technology Stack

- **Container Runtime**: Docker
- **Orchestration**: Kubernetes (kind)
- **LLM**: Ollama with qwen2.5 0.5B model
- **Message Bus**: Redis
- **Language**: Python 3.11
- **Base OS**: Ubuntu 24.04
