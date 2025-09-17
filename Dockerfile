# Use Python 3.12
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        tesseract-ocr \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
# uvicorn EnglishApp.asgi:application --host 0.0.0.0 --port 8000
CMD ["uvicorn", "EnglishApp.asgi:application", "--host", "0.0.0.0", "--port", "8000"]