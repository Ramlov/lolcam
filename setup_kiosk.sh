#!/bin/bash

echo "Setting up Selfie Booth Kiosk Mode..."

# Create systemd service
sudo tee /etc/systemd/system/selfie-booth.service > /dev/null <<EOF
[Unit]
Description=Selfie Booth Application
After=graphical.target network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/selfie-booth
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStart=/usr/bin/python3 /home/pi/selfie-booth/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOF

# Enable auto-login
sudo raspi-config nonint do_boot_behaviour B4

# Disable screen blanking
sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart > /dev/null <<EOF
@xset s off
@xset -dpms
@xset s noblank
EOF

# Reload and enable service
sudo systemctl daemon-reload
sudo systemctl enable selfie-booth.service

echo "Setup complete! Reboot to start automatically."
echo "Start manually with: sudo systemctl start selfie-booth.service"