# PDF Translation GUI - Quick Start Guide

## ✅ Current Status
- ✅ Conda environment "pdf" is activated
- ✅ BabelDOC 0.4.13 is installed 
- ✅ tkinter is available for GUI
- ✅ requests library is installed
- ✅ GUI application is ready to run

## 🚀 Running the Application

### Option 1: Quick Launch (Recommended)
```bash
./run_gui.sh
```

### Option 2: Manual Launch
```bash
conda activate pdf
python src/main.py
```

## 🔧 Setting up Ollama (Required for Translation)

Before using the translation features, you need to set up Ollama:

1. **Install Ollama** (if not already installed):
   - Visit https://ollama.ai/ and download for macOS
   - Or use: `brew install ollama`

2. **Start Ollama server**:
   ```bash
   ollama serve
   ```

3. **Install a Chinese-capable model**:
   ```bash
   # Recommended models (choose one):
   ollama pull qwen2.5:7b     # 7B parameter model (faster)
   ollama pull qwen2.5:14b    # 14B parameter model (better quality)
   ollama pull llama3.1:8b    # Alternative option
   ```

4. **Verify setup**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

## 🎯 Using the GUI

1. **Start the GUI**: Run `./run_gui.sh`
2. **Connect to Ollama**: 
   - Default server: http://localhost:11434
   - Click "Test Connection"
   - Click "Refresh Models" and select your model
3. **Select Files**: Click "Select PDF Files" to choose PDFs to translate
4. **Choose Output**: Select output directory (optional)
5. **Configure**: Set languages and options
6. **Translate**: Click "Start Translation"

## 📁 Project Structure
```
transui/
├── src/
│   └── main.py              # Main GUI application
├── run_gui.sh              # Launch script
├── setup_dev.sh            # Development setup script
├── requirements.txt        # Python dependencies
├── README.md              # Detailed documentation
└── QUICK_START.md         # This file
```

## 🔍 Troubleshooting

**GUI won't start:**
- Make sure you activated the environment: `conda activate pdf`
- Check if tkinter is available: `python -c "import tkinter"`

**Translation fails:**
- Ensure Ollama is running: `ollama serve`
- Check if models are installed: `ollama list`
- Test API: `curl http://localhost:11434/api/tags`

**Missing dependencies:**
- Run the setup script: `./setup_dev.sh`

## 📝 Notes

- The application is designed to work with the existing conda environment "pdf"
- BabelDOC handles PDF parsing and layout preservation
- Ollama provides local LLM translation (no cloud required)
- Supports batch processing of multiple PDF files
- Preserves original PDF formatting and layout
