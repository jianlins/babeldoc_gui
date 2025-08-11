#!/bin/bash
#
# create_macos_app.sh
# Creates a proper macOS app bundle for the PDF Translator
#

set -e

echo "Creating macOS App Bundle for PDF Translator..."

APP_NAME="PDF Translator"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Clean up any existing app bundle
if [ -d "$APP_DIR" ]; then
    echo "Removing existing app bundle..."
    rm -rf "$APP_DIR"
fi

# Create app bundle structure
echo "Creating app bundle structure..."
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy icon
if [ -f "$PROJECT_DIR/icons/app_icon.icns" ]; then
    echo "Copying app icon..."
    cp "$PROJECT_DIR/icons/app_icon.icns" "$RESOURCES_DIR/"
else
    echo "Warning: app_icon.icns not found. Creating default icon..."
    # Create a simple default icon if the generated one doesn't exist
    python3 -c "
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple icon
size = 512
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw background circle
center = size // 2
radius = size // 2 - 20
draw.ellipse([center - radius, center - radius, center + radius, center + radius], 
             fill=(52, 152, 219, 255), outline=(41, 128, 185, 255), width=4)

# Draw PDF text
try:
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size // 6)
except:
    font = ImageFont.load_default()
    
text = 'PDF'
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_x = (size - text_width) // 2
text_y = (size - text_height) // 2 - 20

draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

# Draw translation arrow
arrow_y = text_y + text_height + 20
arrow_start = size // 3
arrow_end = size * 2 // 3
draw.line([(arrow_start, arrow_y), (arrow_end, arrow_y)], fill=(255, 255, 255, 255), width=8)
draw.polygon([(arrow_end - 15, arrow_y - 10), (arrow_end, arrow_y), (arrow_end - 15, arrow_y + 10)], 
             fill=(255, 255, 255, 255))

image.save('$RESOURCES_DIR/app_icon.png')
print('Default icon created')
"
fi

# Create Info.plist
echo "Creating Info.plist..."
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>pdf-translator</string>
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.pdftranslator.app</string>
    <key>CFBundleName</key>
    <string>PDF Translator</string>
    <key>CFBundleDisplayName</key>
    <string>PDF Translator</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>PDF Document</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>pdf</string>
            </array>
            <key>CFBundleTypeIconFile</key>
            <string>app_icon</string>
            <key>LSHandlerRank</key>
            <string>Alternate</string>
        </dict>
    </array>
</dict>
</plist>
EOF

# Create launcher script
echo "Creating launcher script..."
cat > "$MACOS_DIR/pdf-translator" << 'EOF'
#!/bin/bash

# Get the directory of this script (inside the app bundle)
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT_DIR="$(dirname "$APP_DIR")"

# Find the project directory (assume it's in the same directory as the .app)
PROJECT_DIR="$SCRIPT_DIR"

# Look for the main Python script
MAIN_SCRIPT="$PROJECT_DIR/src/main.py"

if [ ! -f "$MAIN_SCRIPT" ]; then
    # Try alternative locations
    for possible_dir in "$PROJECT_DIR" "$PROJECT_DIR/transui" "$HOME/Projects/PycharmProjects/transui"; do
        if [ -f "$possible_dir/src/main.py" ]; then
            PROJECT_DIR="$possible_dir"
            MAIN_SCRIPT="$possible_dir/src/main.py"
            break
        fi
    done
fi

if [ ! -f "$MAIN_SCRIPT" ]; then
    osascript -e 'display alert "PDF Translator Error" message "Could not find main.py script. Please ensure the app is in the same directory as the project files."'
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR"

# Try to activate conda environment and run the application
if command -v conda >/dev/null 2>&1; then
    # Try with conda
    if conda env list | grep -q "^pdf "; then
        exec conda run --name pdf python "$MAIN_SCRIPT"
    else
        # Fallback to system python
        exec python3 "$MAIN_SCRIPT"
    fi
else
    # Fallback to system python
    exec python3 "$MAIN_SCRIPT"
fi
EOF

# Make launcher script executable
chmod +x "$MACOS_DIR/pdf-translator"

echo "✅ macOS App Bundle created successfully!"
echo ""
echo "📱 App Bundle: $APP_DIR"
echo "🎯 You can now:"
echo "   • Double-click the app to run it"
echo "   • Drag it to Applications folder"
echo "   • Add it to Dock"
echo "   • It will appear with the custom icon"
echo ""
echo "📝 Note: The app will work as long as it's in the same directory as the project files."
echo "      If you move the .app file, also move the entire project folder."
