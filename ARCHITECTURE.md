# AGILE Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Host Operating System                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Docker Sandbox Container                │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │               kind Kubernetes Cluster                │ │ │
│  │  │                                                      │ │ │
│  │  │  ┌────────────────────────────────────────────────┐ │ │ │
│  │  │  │              Agent Pods                        │ │ │ │
│  │  │  │                                                │ │ │ │
│  │  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │ │ │
│  │  │  │  │ Planner  │  │ Executor │  │ Analyzer │    │ │ │ │
│  │  │  │  │  Agent   │  │  Agent   │  │  Agent   │    │ │ │ │
│  │  │  │  └──────────┘  └──────────┘  └──────────┘    │ │ │ │
│  │  │  │                                                │ │ │ │
│  │  │  │  ┌──────────┐  ┌──────────┐                   │ │ │ │
│  │  │  │  │Researcher│  │ Monitor  │                   │ │ │ │
│  │  │  │  │  Agent   │  │  Agent   │                   │ │ │ │
│  │  │  │  └──────────┘  └──────────┘                   │ │ │ │
│  │  │  └────────────────────────────────────────────────┘ │ │ │
│  │  │                                                      │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐                │ │ │
│  │  │  │     Redis    │  │    Ollama    │                │ │ │
│  │  │  │  (Message    │  │   (LLM       │                │ │ │
│  │  │  │    Bus)      │  │  Service)    │                │ │ │
│  │  │  └──────────────┘  └──────────────┘                │ │ │
│  │  │                                                      │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  • Docker socket mounted (for agent execution)            │ │
│  │  • Network isolation                                        │ │
│  │  • Privileged mode (for Docker-in-Docker)                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  • Container isolation from host                                 │
│  • No host OS access for agents                                 │
└───────────────────────────────────────────────────────────────────┘
```

## Communication Flow

```
User Request
     │
     ▼
┌────────────┐
│ Planner     │──── Plans task ────┐
│ Agent       │                    │
└────────────┘                    │
     │                           │
     │ Delegates tasks           │
     ▼                           │
┌────────────┐              ┌────────────┐
│ Executor   │              │ Analyzer   │
│ Agent       │◄───────┐    │ Agent       │
└────────────┘        │    └────────────┘
                      │           │
                      │           ▼
┌────────────┐   ┌────┴────┐  ┌────────────┐
│ Researcher │   │  Redis  │  │ Monitor    │
│ Agent       │──► Pub/Sub  ◄───│ Agent       │
└────────────┘   └─────────┘  └────────────┘
     │                  ▲
     │                  │
     └──────────────────┘
          │
          ▼
    ┌─────────┐
    │ Ollama  │
    │ LLM API │
    └─────────┘
```

## Data Flow

```
1. User sends request to Planner Agent
   ↓
2. Planner uses Ollama to generate task plan
   ↓
3. Planner sends sub-tasks to appropriate agents via Redis
   ↓
4. Each agent:
   a. Receives task via Redis pub/sub
   b. Uses Ollama if needed (for reasoning/command generation)
   c. Executes task (e.g., runs shell command, analyzes data)
   d. Sends result back via Redis
   ↓
5. Planner collects results
   ↓
6. Results sent back to user
```

## Security Layers

```
Layer 1: Host OS
└─> Docker container boundary

Layer 2: Sandbox Container
└─> Privileged only within container
└─> Network isolation via bridge network

Layer 3: Kubernetes Cluster
└─> kind cluster runs inside sandbox
└─> Pod isolation

Layer 4: Agent Pods
└─> Resource limits (CPU, memory)
└─> Individual pod security

Layer 5: Command Execution
└─> Agent commands restricted to sandbox
└─> No host OS access
```

## Agent Capabilities

| Agent      | Primary Role         | Can Execute Commands? | LLM Usage                   |
|------------|---------------------|----------------------|----------------------------|
| Planner    | Coordination         | No                   | Plan generation            |
| Executor   | Command execution    | Yes (sandbox only)   | Command generation         |
| Analyzer   | Data analysis        | No                   | Analysis generation        |
| Researcher | Information research | No                   | Response generation        |
| Monitor    | System monitoring    | No                   | Health assessment          |
