FROM python:3.11-slim

# Install Tesseract and related tools
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    ghostscript \
    libgl1 \
    fonts-dejavu-core \
    && apt-get clean

# Debug: confirm tesseract path
RUN which tesseract && tesseract -v

# Set working directory
WORKDIR /app

# Copy everything into container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 10000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
