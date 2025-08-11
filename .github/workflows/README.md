# GitHub Actions Build System

This directory contains GitHub Actions workflows for building and releasing compiled binary versions of the PDF Translation GUI application.

## Workflows

### 1. Release Workflow (`release.yml`)

**Trigger**: Automatically runs when you push a version tag (e.g., `v1.0.0`, `v2.1.3`)

**What it does**:
- Creates a GitHub release
- Builds executable binaries for:
  - Linux (x64)
  - Windows (x64) 
  - macOS (x64)
  - macOS (ARM64/Apple Silicon)
- Uploads the binaries as release assets
- Archives are compressed (`.tar.gz` for Unix, `.zip` for Windows)

**How to use**:
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### 2. Manual Build Workflow (`build.yml`)

**Trigger**: Manual trigger via GitHub Actions web interface

**What it does**:
- Allows you to select which platforms to build for
- Builds executable binaries on demand
- Uploads binaries as workflow artifacts (downloadable for 7 days)
- Useful for testing before creating an official release

**How to use**:
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select "Build Binaries (Manual)" workflow
4. Click "Run workflow"
5. Choose which platforms to build for
6. Click "Run workflow" button

## Binary Output

The workflows create the following binary files:

- **Linux**: `pdf-translator-gui-linux-x64.tar.gz`
- **Windows**: `pdf-translator-gui-windows-x64.zip` 
- **macOS Intel**: `pdf-translator-gui-macos-x64.tar.gz`
- **macOS Apple Silicon**: `pdf-translator-gui-macos-arm64.tar.gz`

Each archive contains a single executable file that can be run without installing Python or dependencies.

## Dependencies Handling

The workflows handle dependencies by:

1. **System Dependencies**: Installs platform-specific system libraries
2. **Python Dependencies**: Installs core requirements like `requests`, `numpy`, `torch`, etc.
3. **BabelDOC Fallback**: Creates stub modules if BabelDOC is not publicly available
4. **PyInstaller**: Bundles everything into standalone executables

## Troubleshooting

### If builds fail:

1. **Missing dependencies**: The workflow tries to install common dependencies, but you may need to add specific ones to the workflow files
2. **BabelDOC issues**: The workflow includes fallback stub modules, but you may need to adjust these if your code requires specific BabelDOC functionality
3. **PyInstaller issues**: You may need to add hidden imports or adjust the PyInstaller configuration in the workflows

### To customize:

1. **Add more dependencies**: Edit the "Install dependencies" steps in the workflow files
2. **Change executable name**: Modify the `--name` parameter in the PyInstaller commands
3. **Add icon**: Create an icon file and reference it in the PyInstaller spec file
4. **Exclude platforms**: Remove unwanted platform entries from the matrix in the workflow files

## Testing Locally

Before pushing tags, you can test the build process locally:

```bash
# Install PyInstaller
pip install pyinstaller

# Build locally (similar to what GitHub Actions does)
pyinstaller --onefile --windowed --name pdf-translator-gui src/main.py

# Test the executable
./dist/pdf-translator-gui  # On Unix
# or
dist\pdf-translator-gui.exe  # On Windows
```

## Notes

- **File size**: The executables will be large (100MB+) because they include the Python interpreter and all dependencies
- **First run**: May be slower on first launch as PyInstaller unpacks files
- **Platform specific**: Each binary only runs on its target platform
- **Antivirus**: Some antivirus software may flag PyInstaller executables as suspicious (false positive)
