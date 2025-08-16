# PDF Translation GUI - BabelDOC + Ollama

A Python GUI application for translating PDF files to Chinese using BabelDOC and local Ollama LLM server.

## Features

- **Easy PDF Selection**: Select one or multiple PDF files for translation
- **Ollama Integration**: Uses local Ollama server for translation (privacy-friendly)
- **Multiple Output Formats**: Generate Chinese-only PDFs and/or dual-language PDFs
- **Real-time Progress**: Monitor translation progress with detailed logging
- **Configurable Settings**: Adjust translation speed, languages, and output options
- **Model Selection**: Choose from available Ollama models

## Prerequisites

1. **Conda Environment**: You should have a conda environment named "pdf" with BabelDOC installed
2. **Ollama Server**: Install and run Ollama locally with a Chinese-capable model

### Setting up Ollama

1. Install Ollama from https://ollama.ai/
2. Pull a Chinese-capable model (recommended):
   ```bash
   ollama pull qwen2.5:14b
   # or
   ollama pull qwen2.5:7b
   # or
   ollama pull llama3.1:8b
   ```
3. Start Ollama server:
   ```bash
   ollama serve
   ```

## Installation

Download the compiled binary for your platform from the [GitHub Releases page](https://github.com/jianlins/babeldoc_gui/releases).

### macOS

1. Download the `.tar.gz` archive for macOS (arm64) from the Releases page.
2. Extract the archive and locate `babeldoc_gui` or `main.app`.
3. Double-click to launch the application.

### Windows

1. Download the `.zip` archive for Windows from the Releases page.
2. Extract the archive and locate `babeldoc_gui.exe`.
3. Double-click to launch the application.

### Linux

1. Download the `.tar.gz` archive for Linux from the Releases page.
2. Extract the archive and locate `babeldoc_gui`.
3. Run the executable file directly.

No Python environment setup is required for the binary version.

## Usage

### Step 1: Setup Ollama Connection
1. Ensure Ollama is running (default: http://localhost:11434)
2. Click "Test Connection" to verify connectivity
3. Click "Refresh Models" to see available models
4. Select your preferred model (e.g., qwen2.5:14b)

### Step 2: Select Files and Output
1. Click "Select PDF Files" to choose one or more PDF files
2. Click "Select Output Directory" (optional - defaults to same directory as input files)

### Step 3: Configure Translation Options
1. Set source language (default: English)
2. Set target language (default: Chinese)
3. Adjust translation speed (QPS) - lower values are more conservative
4. Choose output formats:
   - Dual-language PDF: Original and translated text side by side
   - Chinese-only PDF: Only translated text

### Step 4: Start Translation
1. Click "Start Translation"
2. Monitor progress in the progress bar and log section
3. Translated files will be saved to the specified output directory

## Output Files

The application generates the following files:
- `{original_name}_translated.pdf` - Chinese-only version
- `{original_name}_dual.pdf` - Dual-language version (if enabled)

## Troubleshooting

### Common Issues

1. **"Failed to connect to Ollama"**
   - Ensure Ollama is running: `ollama serve`
   - Check if the URL is correct (default: http://localhost:11434)
   - Try pulling a model: `ollama pull qwen2.5:14b`

2. **"Failed to initialize BabelDOC"**
   - Ensure you're in the correct conda environment: `conda activate pdf`
   - Verify BabelDOC is installed: `python -c "import babeldoc"`

3. **Translation fails or produces poor results**
   - Try a different model (qwen2.5 models are recommended for Chinese)
   - Reduce QPS if the server is overloaded
   - Check the log section for detailed error messages

4. **Memory issues**
   - Use smaller models (e.g., qwen2.5:7b instead of qwen2.5:14b)
   - Translate files one at a time
   - Reduce QPS setting

### Supported Models

The application works best with models that support Chinese translation:
- **Recommended**: qwen2.5:14b, qwen2.5:7b (Alibaba's Qwen models)
- **Alternative**: llama3.1:8b, mistral:7b
- **Note**: Ensure the model you choose supports Chinese language

## Technical Details

### Architecture
- **GUI Framework**: tkinter (built-in Python GUI toolkit)
- **PDF Processing**: BabelDOC (advanced PDF layout analysis and translation)
- **LLM Backend**: Ollama (local LLM server)
- **Translation Engine**: Custom OllamaTranslator extending OpenAI API compatibility

### Key Components
1. **OllamaTranslator**: Custom translator class that interfaces with Ollama
2. **PDFTranslatorGUI**: Main GUI application class
3. **Async Translation**: Uses BabelDOC's async translation API for real-time progress

### Configuration Options
- Source/Target languages
- Translation speed (QPS)
- Output formats (dual/mono)
- Model selection
- Output directory

## Performance Tips

1. **Model Selection**: Larger models provide better quality but slower speed
2. **QPS Setting**: Start with 1-2 QPS and increase if your hardware can handle it
3. **File Size**: Very large PDFs may take significant time and memory
4. **Hardware**: GPU acceleration helps with model inference speed

## License

This application integrates with BabelDOC and Ollama. Please refer to their respective licenses:
- BabelDOC: https://github.com/funstory-ai/BabelDOC
- Ollama: https://github.com/ollama/ollama

## Contributing

Feel free to submit issues and enhancement requests!
