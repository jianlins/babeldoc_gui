#!/bin/bash

# Development setup script for PDF Translation GUI

echo "=== PDF Translation GUI Development Setup ==="
echo

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda first"
    exit 1
fi

echo "✓ Conda is available"

# Check if pdf environment exists
if conda env list | grep -q "^pdf "; then
    echo "✓ Conda environment 'pdf' exists"
else
    echo "❌ Conda environment 'pdf' not found"
    echo "Please create it with BabelDOC installed:"
    echo "  conda create -n pdf python=3.12"
    echo "  conda activate pdf"
    echo "  pip install babeldoc"
    exit 1
fi

# Activate environment and check dependencies
echo "Activating environment 'pdf'..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate pdf

echo "Checking dependencies..."

# Check BabelDOC
if python -c "import babeldoc" 2>/dev/null; then
    BABELDOC_VERSION=$(python -c "import babeldoc; print(getattr(babeldoc, '__version__', 'unknown'))")
    echo "✓ BabelDOC is installed (version: $BABELDOC_VERSION)"
else
    echo "❌ BabelDOC is not installed"
    echo "Installing BabelDOC..."
    pip install babeldoc
fi

# Check tkinter
if python -c "import tkinter" 2>/dev/null; then
    echo "✓ tkinter is available"
else
    echo "❌ tkinter is not available"
    echo "You may need to install python-tk package"
    exit 1
fi

# Check/install requests
if python -c "import requests" 2>/dev/null; then
    echo "✓ requests is available"
else
    echo "Installing requests..."
    pip install requests
fi

echo
echo "=== Setup Complete! ==="
echo "You can now run the application with:"
echo "  ./run_gui.sh"
echo "or manually:"
echo "  conda activate pdf && python src/main.py"
echo

# Check if Ollama is running
echo "Checking Ollama server..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✓ Ollama server is running"
    echo "Available models:"
    curl -s http://localhost:11434/api/tags | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for model in data.get('models', []):
        print(f'  - {model[\"name\"]}')
except:
    print('  Could not parse model list')
"
else
    echo "⚠️  Ollama server is not running on localhost:11434"
    echo "Please start Ollama with: ollama serve"
    echo "And install a Chinese-capable model like: ollama pull qwen2.5:7b"
fi

echo
echo "=== Ready to use! ==="
