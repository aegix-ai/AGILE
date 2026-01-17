#!/bin/bash
set -e

echo "=== AGILE Setup Script ==="
echo "Setting up AGILE (Autonomous General Intelligence with Learning Elasticity)"
echo ""

cd /home/sandbox

echo "[1/5] Creating directory structure..."
mkdir -p workspace memory reports history templates
echo "✓ Directories created"

echo ""
echo "[2/5] Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "✓ Docker is installed: $(docker --version)"
else
    echo "✗ Docker is not installed. Exiting."
    exit 1
fi

echo ""
echo "[3/5] Initializing memory system..."
python3 -c "
import sys
sys.path.insert(0, '/home/sandbox/AGILE')
from shared.memory import MemoryManager
memory = MemoryManager('/home/sandbox/memory/harmony_memory.json')
memory.load_memory()
print('✓ Memory system initialized')
"

echo ""
echo "[4/5] Verifying AGILE nodes..."
for node in conductor researcher coder tester documenter; do
    if [ -f "/home/sandbox/AGILE/nodes/${node}.py" ]; then
        echo "  ✓ ${node}.py found"
    else
        echo "  ✗ ${node}.py NOT found"
        exit 1
    fi
done

echo ""
echo "[5/5] Creating initial history entry..."
python3 -c "
import sys
sys.path.insert(0, '/home/sandbox/AGILE')
from shared.history_logger import HistoryLogger
logger = HistoryLogger('/home/sandbox/reports/history')
import os
os.makedirs('/home/sandbox/reports/history', exist_ok=True)
with open('/home/sandbox/reports/history/setup.md', 'w') as f:
    f.write('# AGILE Setup\n\nSetup completed at: ' + __import__('datetime').datetime.now().isoformat())
print('✓ History system initialized')
"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "AGILE is ready to use!"
echo ""
echo "Directory structure:"
echo "  /home/sandbox/AGILE      - AGILE code and nodes"
echo "  /home/sandbox/workspace  - Generated projects"
echo "  /home/sandbox/memory     - Shared memory (harmony_memory.json)"
echo "  /home/sandbox/reports    - History book"
echo ""
echo "Usage examples:"
echo ""
echo "  # Setup AGILE (already done)"
echo "  cd /home/sandbox/AGILE"
echo "  python3 -c 'from nodes.conductor import Conductor; c = Conductor(); c.setup()'"
echo ""
echo "  # Start a project"
echo "  python3 -c \"from nodes.conductor import Conductor; c = Conductor(); result = c.process_request({'type': 'start_project', 'request': 'Create a REST API for todo management'}); print(result)\""
echo ""
echo "  # Or use the conductor CLI"
echo "  cd /home/sandbox/AGILE"
echo "  python3 nodes/conductor.py --request \"Create a REST API for todo management\""
echo ""
echo "Happy coding!"
