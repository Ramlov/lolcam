#!/bin/bash
echo "🔧 Fixing Selfie Booth Installation..."

# Navigate to your project directory
cd ~/newlolcam/lolcam

# Clear pip cache
pip cache purge

# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages individually to identify any issues
echo "Installing packages one by one..."
packages=(
    "kivy==2.3.0"
    "kivymd==1.1.1" 
    "Pillow==10.0.0"
    "qrcode[pil]==7.4.2"
    "pyserial==3.5"
    "numpy==1.24.3"
    "opencv-python-headless==4.8.1.78"
    "google-api-python-client==2.108.0"
    "google-auth-httplib2==0.1.1"
    "google-auth-oauthlib==1.1.0"
)

for package in "${packages[@]}"; do
    echo "Installing $package..."
    pip install --no-cache-dir "$package"
    if [ $? -eq 0 ]; then
        echo "✅ $package installed successfully"
    else
        echo "❌ Failed to install $package"
    fi
done

# Install picamera2 via apt
sudo apt install -y python3-picamera2

echo "✅ Installation complete!"
echo "Activate virtual environment: source venv/bin/activate"
echo "Run the app: python main.py"