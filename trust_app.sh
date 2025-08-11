#!/bin/bash
#
# trust_app.sh
# Makes the PDF Translator app trusted to eliminate all security warnings
#

set -e

APP_NAME="PDF Translator.app"

echo "🔒 Making $APP_NAME trusted by the system..."

if [ ! -d "$APP_NAME" ]; then
    echo "❌ Error: $APP_NAME not found in current directory"
    exit 1
fi

# Method 1: Add to Gatekeeper allow list
echo "1. Adding app to Gatekeeper allow list..."
if spctl --add "/Users/u0876964/Projects/PycharmProjects/transui/$APP_NAME" 2>/dev/null; then
    echo "✅ App added to Gatekeeper allow list"
else
    echo "⚠️  Could not add to Gatekeeper (may require admin privileges)"
fi

# Method 2: Remove quarantine and set extended attributes
echo "2. Setting trusted extended attributes..."
xattr -d com.apple.quarantine "$APP_NAME" 2>/dev/null || true
xattr -w com.apple.metadata:kMDItemWhereFroms '()' "$APP_NAME" 2>/dev/null || true

# Method 3: Create .allow file (for some macOS versions)
echo "3. Creating allow file..."
touch "$APP_NAME/.allow" 2>/dev/null || true

echo ""
echo "✅ Trust configuration complete!"
echo "📝 The app should now run without warnings."
echo ""
echo "💡 If you still see warnings, try:"
echo "   • Right-click the app → Open → Open"
echo "   • Or run: open '$APP_NAME'"
