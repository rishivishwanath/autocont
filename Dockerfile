FROM python:3.12

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libmagic1 \
      poppler-utils \
      tesseract-ocr \
      imagemagick \
      curl \
      wget
    # Verify FFmpeg installation


# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY speech ./speech
COPY fonts ./fonts
COPY add_audio.py .
COPY generate_speech.py .
COPY pipeline.py .
COPY summarise_feed.py .
COPY upload_video.py .
COPY utils.py .
COPY main.py .
COPY generate_video.py .
COPY generate_video_audio.py .
COPY generate_video_text.py .
COPY video_generation_pipeline.py .
COPY generate_random_text.py .

# Let Cloud Run set the port dynamically
ENV PORT=8080

# Expose the Cloud Run expected port
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]