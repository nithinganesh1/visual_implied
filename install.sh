#!/bin/bash
# Installation Script for Smart Assistive Navigation System
# Raspberry Pi 5

set -e  # Exit on error

echo "=========================================="
echo "Smart Navigation System - Installation"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "WARNING: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "[1/6] Updating system packages..."
sudo apt-get update

# Install system dependencies
echo "[2/6] Installing system dependencies..."
sudo apt-get install -y \
    espeak \
    python3-pip \
    python3-opencv \
    libatlas-base-dev \
    libopenblas-dev \
    python3-dev \
    python3-setuptools

# Install Python dependencies
echo "[3/6] Installing Python packages..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Setup GPIO permissions
echo "[4/6] Setting up GPIO permissions..."
if ! groups $USER | grep -q "gpio"; then
    sudo usermod -a -G gpio $USER
    echo "Added $USER to gpio group"
fi

# Setup serial port permissions
echo "[5/6] Setting up serial port permissions..."
if ! groups $USER | grep -q "dialout"; then
    sudo usermod -a -G dialout $USER
    echo "Added $USER to dialout group"
fi

# Create log directory
echo "[6/6] Setting up log directory..."
mkdir -p logs
chmod 755 logs

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT NEXT STEPS:"
echo ""
echo "1. Place your YOLO model file 'best.pt' in this directory"
echo ""
echo "2. Update emergency contact in config.py:"
echo "   EMERGENCY_PHONE_NUMBER = '+916282670289'"
echo ""
echo "3. Verify hardware connections:"
echo "   - Camera: USB camera connected"
echo "   - Button: GPIO 17 (or configured pin)"
echo "   - GPS: Check /dev/ttyUSB0 or configure in config.py"
echo "   - GSM: Check /dev/serial0 or configure in config.py"
echo ""
echo "4. REBOOT required for group permissions:"
echo "   sudo reboot"
echo ""
echo "5. After reboot, test the system:"
echo "   python3 main.py"
echo ""
echo "For testing without hardware, enable mock modules in config.py:"
echo "   USE_MOCK_GPS = True"
echo "   USE_MOCK_GSM = True"
echo ""
echo "=========================================="
