# AGILE

AGILE is a multi-agent experimental framework designed for running and orchestrating dozens of agents within a controlled sandbox environment.

## Overview

AGILE provides a systemized environment for deploying and managing multiple autonomous agents. The framework isolates agent execution within a Docker-based sandbox with elevated permissions, enabling comprehensive experimentation while maintaining safety and control.

## Sandbox Environment

The AGILE sandbox provides:

- **Privileged Execution**: Docker containers run with elevated privileges for system-level experimentation
- **Isolated Workspace**: Dedicated workspace volume for agent data and outputs
- **Full System Access**: Unconfined seccomp, cgroup host access, and all capabilities enabled
- **Network Isolation**: Bridge network for controlled inter-agent communication

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Sandbox

```bash
cd sandbox
docker-compose up -d
```

This will build and start the sandbox container in detached mode.

### Accessing the Sandbox

```bash
docker exec -it agile-sandbox /bin/bash
```

The sandbox environment includes:
- Python 3 with pip
- Essential development tools (git, vim, nano)
- Network utilities (ping, dnsutils)
- System monitoring tools (htop, tree)

## Architecture

The sandbox container is configured with:
- Base image: Ubuntu 24.04
- Non-root user: `sandbox` with sudo access
- Default credentials: `sandbox/sandbox`
- Working directory: `/home/sandbox`
- Workspace mount: `/home/sandbox/workspace`

## Project Status

This project is currently in early development, focused on establishing the sandbox infrastructure for multi-agent experimentation.
