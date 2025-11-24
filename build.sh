#!/bin/bash

# Change to script directory
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo ""

# Create output folder before everything
if [ ! -d "dist" ]; then
    echo "Creating dist folder..."
    mkdir -p dist
    echo "Dist folder created!"
else
    echo "Dist folder already exists."
fi
echo ""

echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

echo ""
echo "Creating executable..."
echo ""

# Check if src directory exists
if [ ! -d "src" ]; then
    echo "ERROR: src directory not found!"
    exit 1
fi

# Check if executable is running (only if local dist folder exists)
if pgrep -x "WhatsAppRebooter.exe" > /dev/null 2>&1; then
    # Process is running, only block if it's from this folder
    if [ -f "dist/WhatsAppRebooter.exe" ]; then
        echo "WARNING: WhatsAppRebooter.exe from this folder is running!"
        echo "Close the application before building again."
        exit 1
    else
        echo "WARNING: WhatsAppRebooter.exe detected (possibly from another folder)."
        echo "Since local executable doesn't exist, continuing build..."
    fi
fi

# Check if icon exists (use absolute path to avoid issues)
ICON_PARAM=""
if [ -f "assets/icon.ico" ]; then
    # Use absolute path to ensure it works even with --specpath
    ICON_PATH="$(cd "$(dirname "$0")" && pwd)/assets/icon.ico"
    ICON_PARAM="--icon=\"$ICON_PATH\""
    echo "Icon found: $ICON_PATH"
else
    echo "Warning: Icon not found. Using Windows default."
fi

# Run PyInstaller and set output folder
# Use --paths to add src to PYTHONPATH
# --collect-submodules collects all submodules automatically
if [ -n "$ICON_PARAM" ]; then
    pyinstaller --onefile --windowed --name "WhatsAppRebooter" $ICON_PARAM --distpath "dist" --workpath "dist/build" --specpath "dist" --paths "." --collect-submodules src --hidden-import win32timezone main.py
else
    pyinstaller --onefile --windowed --name "WhatsAppRebooter" --distpath "dist" --workpath "dist/build" --specpath "dist" --paths "." --collect-submodules src --hidden-import win32timezone main.py
fi

# Copy assets folder to dist (for icons and resources)
if [ -d "assets" ]; then
    echo ""
    echo "Copying assets folder to dist..."
    if [ -d "dist/assets" ]; then
        rm -rf "dist/assets"
    fi
    cp -r "assets" "dist/assets"
    echo "Assets folder copied successfully!"
else
    echo ""
    echo "Warning: Assets folder not found."
fi

echo ""
echo "========================================"
if [ -f "dist/WhatsAppRebooter.exe" ]; then
    echo "SUCCESS! Executable created at:"
    echo "$(pwd)/dist/WhatsAppRebooter.exe"
else
    echo "ERROR: Executable was not created!"
    echo "Check error messages above."
fi
echo "========================================"
