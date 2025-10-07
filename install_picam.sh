#!/bin/bash
# install_picamera2.sh
# This script installs Picamera2 and its dependencies on a Debian/Ubuntu-based system

set -e  # Exit immediately if a command exits with a non-zero status

echo "Updating package list..."
sudo apt update

echo "Installing system dependencies..."
sudo apt install -y python3-libcamera python3-kms++
sudo apt install -y python3-pyqt5 python3-prctl libatlas-base-dev ffmpeg python3-pip

echo "Upgrading numpy and installing Picamera2..."
pip3 install --upgrade numpy
pip3 install picamera2

echo "✅ Installation complete!"
