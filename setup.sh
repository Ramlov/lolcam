# Add the Raspberry Pi repository
echo "deb http://archive.raspberrypi.com/debian/ bookworm main" | sudo tee /etc/apt/sources.list.d/raspi.list

# Import the signing key
curl -fsSL https://archive.raspberrypi.com/debian/raspberrypi.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/raspberrypi.gpg

# Update package lists
sudo apt update
