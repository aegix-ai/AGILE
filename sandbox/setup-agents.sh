#!/bin/bash
set -e

echo "=== AGILE Multi-Agent System Setup ==="
echo "Setting up Kubernetes cluster and deploying agents..."

echo "Step 1: Creating kind cluster..."
cat <<EOF | kind create cluster --name agile --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraMounts:
      - hostPath: /var/run/docker.sock
        containerPath: /var/run/docker.sock
  - role: worker
    extraMounts:
      - hostPath: /var/run/docker.sock
        containerPath: /var/run/docker.sock
  - role: worker
    extraMounts:
      - hostPath: /var/run/docker.sock
        containerPath: /var/run/docker.sock
EOF

echo "Step 2: Creating ConfigMap for agent code..."
kubectl create configmap agents-code \
  --from-file=agents/planner_agent.py \
  --from-file=agents/executor_agent.py \
  --from-file=agents/analyzer_agent.py \
  --from-file=agents/researcher_agent.py \
  --from-file=agents/monitor_agent.py \
  --from-file=agents/shared/base_agent.py \
  --from-file=agents/shared/__init__.py \
  --from-file=agents/requirements.txt \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Step 3: Deploying Redis message bus..."
kubectl apply -f kubernetes/redis.yaml

echo "Waiting for Redis to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/redis

echo "Step 4: Deploying Ollama..."
kubectl apply -f kubernetes/ollama.yaml

echo "Waiting for Ollama to be ready and model to download..."
kubectl wait --for=condition=available --timeout=300s deployment/ollama

echo "Step 5: Deploying agents..."
kubectl apply -f kubernetes/planner-agent.yaml
kubectl apply -f kubernetes/executor-agent.yaml
kubectl apply -f kubernetes/analyzer-agent.yaml
kubectl apply -f kubernetes/researcher-agent.yaml
kubectl apply -f kubernetes/monitor-agent.yaml

echo "Waiting for all agents to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/planner-agent
kubectl wait --for=condition=available --timeout=120s deployment/executor-agent
kubectl wait --for=condition=available --timeout=120s deployment/analyzer-agent
kubectl wait --for=condition=available --timeout=120s deployment/researcher-agent
kubectl wait --for=condition=available --timeout=120s deployment/monitor-agent

echo ""
echo "=== Setup Complete ==="
echo "Cluster status:"
kubectl get pods

echo ""
echo "Services:"
kubectl get services

echo ""
echo "To check logs for a specific agent:"
echo "  kubectl logs -f deployment/planner-agent"
echo "  kubectl logs -f deployment/executor-agent"
echo "  kubectl logs -f deployment/analyzer-agent"
echo "  kubectl logs -f deployment/researcher-agent"
echo "  kubectl logs -f deployment/monitor-agent"
echo ""
echo "To interact with the planner agent:"
echo "  kubectl exec -it deployment/planner-agent -- python -c \"from planner_agent import PlannerAgent; import json; agent = PlannerAgent(); result = agent.execute_task({'type': 'task', 'request': 'list all files in current directory', 'reply_to': 'planner'}); print(json.dumps(result, indent=2))\""
