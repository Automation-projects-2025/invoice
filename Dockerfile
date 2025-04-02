FROM python:3.11-slim

# Install system dependencies needed for OCR and image decoding
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    ghostscript \
    libgl1 \
    libjpeg62-turbo \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    fonts-dejavu-core \
    && apt-get clean

# Debug: confirm tesseract is installed
RUN which tesseract && tesseract -v

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose app port
EXPOSE 10000

# Start app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
