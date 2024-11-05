# Sử dụng hình ảnh chính thức Python 3.10.0 làm hình ảnh cơ sở
FROM python:3.10.0-slim

# Thiết lập biến môi trường để Python không tạo bytecode và không buffer đầu ra
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các gói cần thiết cho hệ thống
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt pip và các phụ thuộc của dự án
COPY requirements.txt /app/
COPY .env /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Sao chép toàn bộ mã nguồn vào thư mục làm việc trong container
COPY . /app/

# Thu thập các tệp tĩnh
RUN python manage.py collectstatic --noinput

# Lệnh để chạy ứng dụng Django sử dụng Gunicorn
# CMD ["python", "EnglishApp.wsgi:application", "--bind", "0.0.0.0:8080"]
CMD ["python", "manage.py", "runserver"]