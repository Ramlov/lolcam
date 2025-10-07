#!/bin/bash

# Selfie Booth All-in-One Startup Script
echo "🎪 Starting Selfie Booth..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down Selfie Booth..."
    pkill -f "python.*main.py" 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Set display for DSI screen
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority

# Set Kivy environment variables for better DSI compatibility
export KIVY_GL_BACKEND=gl
export KIVY_WINDOW=sdl2

# Check if X server is running
if ! xset q &>/dev/null; then
    echo "🖥️  Starting X server..."
    startx &
    X_PID=$!
    sleep 5
fi

# Wait for X to be ready
echo "⏳ Waiting for display to be ready..."
until xset q &>/dev/null; do
    sleep 1
done

# Kill any existing instances
echo "🧹 Cleaning up any existing instances..."
pkill -f "python.*main.py" 2>/dev/null
sleep 2

# Start the Selfie Booth application
echo "🚀 Starting Selfie Booth application..."
python3 main.py

# If app exits, wait a bit and restart (optional)
echo "🔄 Application ended. Restarting in 5 seconds..."
sleep 5
exec "$0" "$@"