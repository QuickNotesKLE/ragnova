# ==========================================================
# FastAPI + Tesseract OCR + Poppler (for pdf2image)
# ==========================================================
FROM python:3.11-slim

# ----------------------------------------------------------
# 🧩 Install system dependencies
# ----------------------------------------------------------
RUN apt-get update && apt-get install -y \
    poppler-utils \         # for pdf2image
    tesseract-ocr \         # for local OCR
    libjpeg-dev \           # for Pillow image handling
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# 🏗️ Set working directory
# ----------------------------------------------------------
WORKDIR /app

# Copy dependency list (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------
# 📦 Copy project files
# ----------------------------------------------------------
COPY . .

# ----------------------------------------------------------
# 🔧 Expose port (Railway dynamically assigns one)
# ----------------------------------------------------------
EXPOSE 8080

# Optional: specify Tesseract language data location
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# ----------------------------------------------------------
# 🚀 Start FastAPI app
# ----------------------------------------------------------
# Use ${PORT:-8080} fallback for local dev; Railway sets $PORT automatically
CMD ["bash", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
