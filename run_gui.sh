#!/bin/bash

# PDF Translation GUI Launcher
# This script activates the conda environment and runs the GUI

echo "Starting PDF Translation GUI..."
echo "Activating conda environment 'pdf'..."

# Activate the conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate pdf

# Check if activation was successful
if [[ "$CONDA_DEFAULT_ENV" == "pdf" ]]; then
    echo "Environment activated successfully!"
    echo "Launching GUI..."
    python src/main.py
else
    echo "Failed to activate environment 'pdf'"
    echo "Please make sure the conda environment 'pdf' exists and has babeldoc installed"
    echo "You can create it with: conda create -n pdf python=3.9"
    echo "Then install babeldoc: pip install babeldoc"
fi
