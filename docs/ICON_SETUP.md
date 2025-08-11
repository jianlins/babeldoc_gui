# Application Icon Setup - README

## Overview
The PDF Translator application now includes a custom icon that appears in:
- Application window title bar
- macOS Dock when running
- macOS App Bundle
- System toolbar/taskbar

## Icon Features

### 🎨 Design
- **Theme**: Modern flat design with PDF translation concept
- **Colors**: Professional blue gradient (#3498db to #2980b9)
- **Symbol**: "PDF" text with translation arrow
- **Sizes**: Multiple resolutions for crisp display on all devices

### 📱 Platform Support
- **macOS**: Uses `.icns` format for best integration
- **Windows**: Uses `.ico` format for Windows compatibility
- **Linux**: Uses `.png` format as fallback
- **All Platforms**: Automatically detects and uses appropriate format

## Files Created

### Icon Files (in `icons/` directory)
```
icons/
├── app_icon.icns          # macOS icon bundle
├── app_icon.ico           # Windows icon
├── app_icon.png           # Main PNG icon (512x512)
├── app_icon_16.png        # 16x16 for small UI elements
├── app_icon_32.png        # 32x32 for toolbars
├── app_icon_48.png        # 48x48 for window decorations
├── app_icon_64.png        # 64x64 for lists
├── app_icon_128.png       # 128x128 for applications
├── app_icon_256.png       # 256x256 for high-DPI
├── app_icon_512.png       # 512x512 for maximum quality
└── app_icon.iconset/      # macOS iconset source folder
    ├── icon_16x16.png
    ├── icon_16x16@2x.png
    ├── icon_32x32.png
    ├── icon_32x32@2x.png
    ├── icon_128x128.png
    ├── icon_128x128@2x.png
    ├── icon_256x256.png
    ├── icon_256x256@2x.png
    ├── icon_512x512.png
    └── icon_512x512@2x.png
```

### App Bundle
```
PDF Translator.app/
├── Contents/
│   ├── Info.plist         # App metadata
│   ├── MacOS/
│   │   └── pdf-translator # Launcher script
│   └── Resources/
│       └── app_icon.icns  # App icon
```

## How It Works

### 1. Icon Generation
The application automatically generates icons in multiple formats:
- Uses Pillow (PIL) to create high-quality vector-style graphics
- Generates all required sizes for different use cases
- Creates platform-specific formats (.icns, .ico, .png)

### 2. Icon Loading
The `setup_app_icon()` method in `main.py`:
- Detects the operating system
- Chooses the best icon format for the platform
- Sets the window icon using `tkinter.iconphoto()`
- Handles errors gracefully if icon files are missing

### 3. App Bundle Integration
The `create_macos_app.sh` script:
- Creates a proper macOS .app bundle structure
- Includes the icon in the Resources folder
- Sets up Info.plist with icon references
- Creates a launcher script that finds and runs the Python application

## Usage

### Running with Icon
The icon is automatically loaded when you run the application:
```bash
conda activate pdf
python src/main.py
```

### Creating macOS App Bundle
To create a double-clickable macOS app with icon:
```bash
./create_macos_app.sh
```

Then you can:
- Double-click "PDF Translator.app" to run
- Drag it to Applications folder
- Add it to Dock for easy access

### Customizing the Icon
To modify the icon:
1. Edit the icon generation code in `setup_app_icon()` method
2. Or replace the files in the `icons/` directory with your own
3. Run the app to see changes
4. Recreate the app bundle if needed

## Technical Details

### Icon Generation Code
The icon is generated programmatically using Pillow:
- Vector-style drawing for crisp edges at any size
- Gradient backgrounds for modern appearance
- Text rendering with system fonts
- Transparent backgrounds for better integration

### Platform Detection
```python
import platform
system = platform.system()
if system == "Darwin":      # macOS
    # Use .icns format
elif system == "Windows":   # Windows
    # Use .ico format
else:                      # Linux and others
    # Use .png format
```

### Error Handling
- Graceful fallback if Pillow is not installed
- Creates temporary icons if needed
- Logs errors for debugging
- Continues running even if icon setup fails

## Dependencies

### Required (for icon generation)
- **Pillow**: `pip install Pillow`
  - Used for creating and manipulating images
  - Should be installed in your conda environment

### Optional (for macOS app bundle)
- **iconutil**: Built into macOS
  - Converts iconset to .icns format
  - Used by the app creation script

## Troubleshooting

### Icon Not Appearing
1. **Check Pillow installation**: `pip install Pillow`
2. **Verify icon files exist**: Look in `icons/` directory
3. **Check console output**: Look for icon-related error messages
4. **Restart application**: Sometimes icon changes need a restart

### App Bundle Issues
1. **Permission errors**: Make sure `create_macos_app.sh` is executable
2. **Path issues**: Keep the .app file in the same directory as the project
3. **Conda environment**: The launcher script tries to find and activate the 'pdf' environment

### Platform-Specific Issues

**macOS:**
- Icon should appear in Dock and window title
- App bundle provides best integration
- Requires macOS 10.12 or later

**Windows:**
- Icon appears in taskbar and window title
- May need to restart explorer.exe to see taskbar changes

**Linux:**
- Icon support varies by window manager
- PNG format provides best compatibility

## Future Improvements
1. **Dynamic icon themes**: Light/dark mode support
2. **Status indicators**: Show translation progress in icon
3. **Document icons**: Custom icons for different file types
4. **Installer creation**: Automated installer with icon registration
