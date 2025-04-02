#!/usr/bin/env bash

# Install Tesseract and Poppler
apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils

# Install Python dependencies
pip install -r requirements.txt
