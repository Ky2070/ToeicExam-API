# Sử dụng image Python chính thức
FROM python:3.10-slim

# Đặt biến môi trường để ngăn yêu cầu đầu vào từ Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cài đặt các dependency cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    tesseract-ocr \
    libsm6 libxext6 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# # Thiết lập thư mục làm việc trong container
# WORKDIR /app

# Sao chép tệp yêu cầu của Django vào container
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn ứng dụng Django vào container
COPY . .

# Mở port (thường dùng cho dev, có thể thay đổi)
EXPOSE 8000

RUN python manage.py collectstatic --noinput

# Chạy lệnh để khởi chạy ứng dụng Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "EnglishApp.wsgi:application"]
