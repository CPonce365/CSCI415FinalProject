#!/bin/bash
# CDN Node Setup Script

# Exit on any error
set -e

echo "Setting up Git configuration..."
git config --global core.editor "vim"
git config --global user.name "Calosha"
git config --global user.email "alexey.chernyuk@gmail.com"

echo "Installing GitHub CLI..."
sudo apt update
sudo apt install -y gh

echo "Authenticating with GitHub..."
# This will prompt for authentication - consider using a token directly for automation
gh auth login

echo "Cloning repository..."
git clone https://github.com/Calosha/Final_project_metrics.git

echo "Installing Python dependencies..."
sudo apt install -y python3-pip
cd Final_project_metrics
pip3 install -r requirements.txt

echo "Creating and starting service..."
sudo cp ./service/cdnapi.service /etc/systemd/system/cdnapi.service
sudo systemctl daemon-reload
sudo systemctl enable cdnapi
sudo systemctl start cdnapi

echo "Checking service status..."
sudo systemctl status cdnapi
