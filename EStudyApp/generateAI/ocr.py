# utils/ocr.py
import shutil

import requests
from PIL import Image, UnidentifiedImageError
import pytesseract
from io import BytesIO

import logging
import platform

# Thiết lập logging cho ứng dụng
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kiểm tra hệ điều hành và thiết lập đường dẫn Tesseract nếu cần
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    # Kiểm tra xem tesseract đã được cài và có trong PATH chưa '/usr/bin/tesseract'  # nếu đã cài
    if not shutil.which("tesseract"):
        raise EnvironmentError("Tesseract OCR không được cài đặt trong hệ thống Linux. Cài bằng: apt-get install tesseract-ocr")


def extract_text_from_image_urls(image_urls):
    """
    Nhận danh sách URL ảnh, trả về nội dung văn bản trích xuất bằng OCR.
    """
    if not isinstance(image_urls, list):
        image_urls = [image_urls]

    extracted_texts = []
    for url in image_urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # kiểm tra lỗi HTTP
            image = Image.open(BytesIO(response.content)).convert("RGB")  # đảm bảo ảnh ở đúng mode
            text = pytesseract.image_to_string(image)
            extracted_texts.append(text.strip() or "[Ảnh không có văn bản rõ ràng]")
        except UnidentifiedImageError:
            extracted_texts.append(f"❌ Không thể nhận diện định dạng ảnh từ: {url}")
        except requests.exceptions.RequestException as e:
            extracted_texts.append(f"❌ Lỗi tải ảnh từ {url}: {str(e)}")
        except Exception as e:
            extracted_texts.append(f"⚠️ Lỗi không xác định với {url}: {str(e)}")

    return "\n\n---\n\n".join(extracted_texts)
