#!/bin/bash

# Document Archiver - Dependency Installation Script
# This script installs all required dependencies for the Document Archiver app

echo "Installing Document Archiver Dependencies..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS $VER"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install Pillow>=8.0.0
pip install python-tesseract>=0.3.8
pip install opencv-python>=4.5.0
pip install numpy>=1.19.0
pip install pdf2image>=1.16.0
pip install pytesseract>=0.3.8

# Install system dependencies based on OS
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    echo "Installing Ubuntu/Debian dependencies..."
    sudo apt-get update
    sudo apt-get install -y \
        sane-utils \
        tesseract-ocr \
        tesseract-ocr-eng \
        libtesseract-dev \
        poppler-utils \
        libpoppler-cpp-dev \
        libopencv-dev \
        python3-opencv
    
    # Install additional Tesseract language packs
    sudo apt-get install -y \
        tesseract-ocr-spa \
        tesseract-ocr-fra \
        tesseract-ocr-deu \
        tesseract-ocr-por \
        tesseract-ocr-ita

elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Fedora"* ]]; then
    echo "Installing CentOS/RHEL/Fedora dependencies..."
    if command -v dnf &> /dev/null; then
        sudo dnf install -y \
            sane-backends \
            tesseract \
            tesseract-langpack-eng \
            poppler-utils \
            opencv-devel \
            python3-opencv
    else
        sudo yum install -y \
            sane-backends \
            tesseract \
            tesseract-langpack-eng \
            poppler-utils \
            opencv-devel \
            python3-opencv
    fi

elif [[ "$OS" == *"Arch"* ]]; then
    echo "Installing Arch Linux dependencies..."
    sudo pacman -S --noconfirm \
        sane \
        tesseract \
        tesseract-data-eng \
        poppler \
        opencv \
        python-opencv

else
    echo "Unsupported OS: $OS"
    echo "Please install the following dependencies manually:"
    echo "- SANE (Scanner Access Now Easy)"
    echo "- Tesseract OCR"
    echo "- Poppler (for PDF processing)"
    echo "- OpenCV"
    echo "- Python packages: Pillow, pytesseract, opencv-python, numpy, pdf2image"
fi

# Test installations
echo "Testing installations..."

# Test Tesseract
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract installed: $(tesseract --version | head -n1)"
else
    echo "✗ Tesseract not found"
fi

# Test SANE
if command -v scanimage &> /dev/null; then
    echo "✓ SANE installed: $(scanimage --version)"
else
    echo "✗ SANE not found"
fi

# Test Python packages
python3 -c "import PIL; print('✓ Pillow installed:', PIL.__version__)" 2>/dev/null || echo "✗ Pillow not found"
python3 -c "import cv2; print('✓ OpenCV installed:', cv2.__version__)" 2>/dev/null || echo "✗ OpenCV not found"
python3 -c "import pytesseract; print('✓ pytesseract installed')" 2>/dev/null || echo "✗ pytesseract not found"
python3 -c "import numpy; print('✓ NumPy installed:', numpy.__version__)" 2>/dev/null || echo "✗ NumPy not found"
python3 -c "import pdf2image; print('✓ pdf2image installed')" 2>/dev/null || echo "✗ pdf2image not found"

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Install the Document Archiver app in ERPNext"
echo "2. Configure scanner settings in Document Archiver > Scanner Config"
echo "3. Test scanner connections"
echo "4. Start archiving documents!"
echo ""
echo "For troubleshooting, check the README.md file"