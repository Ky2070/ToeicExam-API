import platform

import pytesseract
from PIL import Image
import requests
from io import BytesIO

# Chỉ set tesseract_cmd nếu đang chạy trên Windows
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# URL of the image
image_url = 'https://s4-media1.study4.com/media/gg_imgs/test/9a18decce4319016bc774c19922917c0c4ff4413.jpg'

# Fetch the image from the URL
response = requests.get(image_url)
img = Image.open(BytesIO(response.content))

# Optional: Specify the path to the Tesseract executable if it's not in your PATH

# Extract text from the image
text = pytesseract.image_to_string(img)

print("Extracted Text:")
print(text)