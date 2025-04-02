#!/usr/bin/env bash

# Install system packages needed for PDF OCR
apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    ghostscript \
    libgl1 \
    fonts-dejavu-core

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
