#!/bin/bash
#
# fix_app_security.sh
# Fixes macOS security warnings for the PDF Translator app
#

set -e

APP_NAME="PDF Translator.app"

echo "🔒 Fixing macOS security for $APP_NAME..."

if [ ! -d "$APP_NAME" ]; then
    echo "❌ Error: $APP_NAME not found in current directory"
    echo "   Please run this script from the directory containing the app"
    exit 1
fi

echo "1. Removing quarantine attribute..."
xattr -dr com.apple.quarantine "$APP_NAME" 2>/dev/null || true

echo "2. Self-signing the app..."
if codesign --force --deep --sign - "$APP_NAME" 2>/dev/null; then
    echo "✅ App signed successfully!"
else
    echo "⚠️  Could not sign app"
fi

echo "3. Verifying signature..."
if codesign --verify --deep --strict "$APP_NAME" 2>/dev/null; then
    echo "✅ Signature verified!"
else
    echo "⚠️  Signature verification failed"
fi

echo ""
echo "🎉 Security fixes applied!"
echo "📝 You should now be able to run the app without security warnings."
echo ""
echo "💡 If you still get warnings:"
echo "   1. Try to open the app"
echo "   2. Go to System Preferences → Security & Privacy → General"
echo "   3. Click 'Allow Anyway' next to the blocked app message"
echo "   4. Try to open the app again and click 'Open'"
