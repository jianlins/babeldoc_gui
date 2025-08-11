#!/bin/bash

# PDF Translation GUI Launcher Script
# This script activates the conda environment and launches the GUI

echo "PDF Translation GUI - BabelDOC + Ollama"
echo "======================================"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda not found. Please install Anaconda or Miniconda."
    exit 1
fi

# Check if the pdf environment exists
if ! conda env list | grep -q "pdf"; then
    echo "Error: conda environment 'pdf' not found."
    echo "Please create and set up the environment with BabelDOC installed."
    exit 1
fi

# Activate the environment and run the application
echo "Activating conda environment 'pdf'..."
eval "$(conda shell.bash hook)"
conda activate pdf

echo "Checking dependencies..."
python -c "import babeldoc" 2>/dev/null || {
    echo "Error: BabelDOC not found in the environment."
    echo "Please install BabelDOC in the 'pdf' environment."
    exit 1
}

echo "Starting PDF Translation GUI..."
python src/main.py
