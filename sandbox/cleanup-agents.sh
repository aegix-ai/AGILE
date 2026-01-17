#!/bin/bash
set -e

echo "=== AGILE Multi-Agent System Cleanup ==="
echo "Cleaning up Kubernetes cluster and resources..."

echo "Deleting all Kubernetes resources..."
kubectl delete -f kubernetes/monitor-agent.yaml --ignore-not-found=true
kubectl delete -f kubernetes/researcher-agent.yaml --ignore-not-found=true
kubectl delete -f kubernetes/analyzer-agent.yaml --ignore-not-found=true
kubectl delete -f kubernetes/executor-agent.yaml --ignore-not-found=true
kubectl delete -f kubernetes/planner-agent.yaml --ignore-not-found=true
kubectl delete -f kubernetes/ollama.yaml --ignore-not-found=true
kubectl delete -f kubernetes/redis.yaml --ignore-not-found=true

echo "Deleting ConfigMap..."
kubectl delete configmap agents-code --ignore-not-found=true

echo "Deleting kind cluster..."
kind delete cluster --name agile

echo ""
echo "=== Cleanup Complete ==="
echo "Kubernetes cluster and all resources have been removed."
