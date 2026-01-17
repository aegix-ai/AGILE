# AGILE Quick Reference

## Starting the System

1. Start the sandbox:
```bash
cd sandbox
docker-compose up -d
```

2. Enter the sandbox:
```bash
docker exec -it agile-sandbox /bin/bash
```

3. Setup the agent system:
```bash
cd /home/sandbox
./setup-agents.sh
```

## Monitoring

Check all pods:
```bash
kubectl get pods
```

Check pod logs:
```bash
kubectl logs -f deployment/planner-agent
kubectl logs -f deployment/executor-agent
kubectl logs -f deployment/analyzer-agent
kubectl logs -f deployment/researcher-agent
kubectl logs -f deployment/monitor-agent
```

Check services:
```bash
kubectl get services
```

## Testing

Run all tests:
```bash
python3 test-agents.py
```

## Cleanup

Clean up all resources:
```bash
./cleanup-agents.sh
```

## Agent Communication

The agents communicate via Redis pub/sub channels:
- `agent:planner` - Planner agent channel
- `agent:executor` - Executor agent channel
- `agent:analyzer` - Analyzer agent channel
- `agent:researcher` - Researcher agent channel
- `agent:monitor` - Monitor agent channel
- `agent:broadcast` - Broadcast channel for all agents

## Resource Limits

Each agent pod has the following limits:
- Memory: 512Mi
- CPU: 500m

Services:
- Redis: 256Mi memory, 500m CPU
- Ollama: 2Gi memory, 2000m CPU

## Troubleshooting

If pods aren't starting:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

If Ollama model isn't downloading:
```bash
kubectl logs -f deployment/ollama
```

If agents can't communicate:
```bash
kubectl get pods
kubectl exec -it deployment/redis -- redis-cli ping
```

Restart a specific deployment:
```bash
kubectl rollout restart deployment/<agent-name>
```
