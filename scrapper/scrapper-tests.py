import json
import os
import winreg
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Xác định đường dẫn thư mục chứa script và file .env
env_path = Path(__file__).parent / '.env'
# Load biến môi trường từ file .env
print(env_path)
load_dotenv(env_path)


# # Setup paths for Chromedriver
# base_path = r'C:\Users\nguye\PycharmProjects\EnglishTest\scrapper\chromedriver-win64'
# chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
#
# # Initialize WebDriver
# service = Service(executable_path=chromedriver_path)
# driver = webdriver.Chrome(service=service)
# Cung cấp đường dẫn đến Chrome binary


def find_chrome_from_registry():
    # Các đường dẫn trong registry để tìm chrome.exe
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",  # Đối với 64-bit hệ điều hành
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
    ]

    for registry_path in registry_paths:
        try:
            # Mở registry key, tùy trường hợp ứng dụng chrome thì chỗ này có thể là HKEY_CURRENT_USER
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path)
            chrome_path, _ = winreg.QueryValueEx(registry_key, None)
            winreg.CloseKey(registry_key)

            # Kiểm tra sự tồn tại của file chrome.exe
            if os.path.exists(chrome_path):
                return chrome_path
        except FileNotFoundError:
            continue

    # Nếu không tìm thấy chrome trong registry, trả về None
    return None


# Tìm Chrome từ registry
chrome_path = find_chrome_from_registry()

if chrome_path:
    print(f"Chrome found at: {chrome_path}")
    # Cấu hình Selenium để sử dụng Chrome đã tìm được
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
else:
    print("Chrome executable could not be found!")
    exit()  # Thoát chương trình nếu không tìm thấy Chrome
# Tự động tải và cài đặt phiên bản ChromeDriver tương thích với phiên bản Chrome
service = Service(ChromeDriverManager().install())

# Khởi tạo WebDriver với Service và Options
driver = webdriver.Chrome(service=service, options=chrome_options)


# Hàm để đọc dữ liệu từ file .txt
def read_data_from_file(file_path):
    data = {}
    try:
        with open(file_path, 'r') as file:
            current_part = None
            for line in file:
                line = line.strip()  # Loại bỏ dấu cách thừa và dòng trống
                if line:  # Nếu dòng không rỗng
                    if '=' in line:  # Kiểm tra nếu có dấu '=' để phân tách key và value
                        key, value = line.split('=', 1)  # Tách dữ liệu thành key và value
                        key = key.strip()  # Loại bỏ dấu cách thừa
                        value = value.strip()

                        # Lưu test_id
                        if key == "test_id":
                            data[key] = value
                        # Lưu các phần part id và content id
                        elif key.startswith('part_'):
                            part_key = key.split('_')[1]  # Lấy phần số (1, 2, 3, ...)
                            if part_key not in data:
                                data[part_key] = {}  # Nếu chưa có key part, tạo dictionary cho nó
                            part_subkey = key.split('_')[2]  # Lấy phần id hoặc content id
                            data[part_key][part_subkey] = value
                    else:
                        print(f"Warning: Skipping invalid line: {line}")
    except FileNotFoundError as e:
        print(f"File {file_path} not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return data


# Đọc dữ liệu từ file test_data.txt
print(f"Current working directory: {os.getcwd()}")

data = read_data_from_file('test-data.txt')

# Kiểm tra dữ liệu đã đọc được
print("Data read from file:", data)

# Lấy test_id từ dữ liệu đọc được
test_id = data.get('test_id')
print(f"Test_id: {test_id}")

# Cấu hình lại các part_id và content_id từ dữ liệu đã đọc từ file
part_ids = []
content_ids = []

for i in range(1, 8):
    # Lấy dữ liệu từ dictionary đã đọc được
    part_id_key = str(i)  # Sử dụng phần số như 1, 2, 3, ... thay vì 'part_{i}_id'
    content_id_key = str(i)  # Sử dụng phần số tương ứng

    # Lấy dữ liệu từ part i
    part_ids.append(data.get(part_id_key, {}).get('id'))
    content_ids.append(data.get(part_id_key, {}).get('content'))

# Kiểm tra các giá trị đã lấy ra từ file
print("Part IDs:", part_ids)
print("Content IDs:", content_ids)


def get_test_links():
    driver.get('https://study4.com/tests/toeic/')
    print(driver.title)

    try:
        test_item = driver.find_element(By.ID, test_id)

        # Lấy thẻ <a> trong test_item để lấy link
        # Lấy thẻ <a> cha của thẻ <h2> chứa test_id
        a_tag = test_item.find_element(By.XPATH, './ancestor::a')  # Tìm thẻ <a> cha
        link = a_tag.get_attribute('href')

        print(f"Found link: {link}")
        return link
    except Exception as e:
        print(f"Error extracting test links: {e}")
        return []


def handle_checkbox_selection():
    checkboxes_selected = 0
    max_scroll_attempts = 7
    for scroll_attempt in range(max_scroll_attempts):
        checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]')
        for checkbox in checkboxes:
            if not checkbox.is_selected() and checkbox.is_displayed():
                try:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                          checkbox)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(checkbox))
                    checkbox.click()
                    checkboxes_selected += 1
                    print(f"Checkbox selected: {checkboxes_selected}")
                    if checkboxes_selected >= 7:
                        break
                except (TimeoutException, ElementClickInterceptedException) as e:
                    print(f"Error clicking checkbox: {e}")

        if checkboxes_selected >= 7:
            print("Selected 7 checkboxes, moving to submit.")
            break
        else:
            driver.execute_script("window.scrollBy(0, window.innerHeight / 0.01);")
            WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")

    return checkboxes_selected >= 7


def submit_form():
    submit_button_found = False
    for _ in range(7):
        try:
            submit_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-primary[type="submit"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
            submit_button.click()
            print("Form submitted successfully.")
            submit_button_found = True
            break
        except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
            print(f"Error submitting form: {e}")
            driver.execute_script("window.scrollBy(0, window.innerHeight / 0.05);")

    return submit_button_found


def login_with_facebook():
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-12.f-login-block'))
        )
        print("Login page loaded successfully.")

        facebook_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.s-button.f-login-button'))
        )
        facebook_button.click()
        print("Clicked 'Login with Facebook' button.")

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'email')))
        username_field = driver.find_element(By.ID, 'email')
        password_field = driver.find_element(By.ID, 'pass')

        username = os.getenv('GMAIL')
        password = os.getenv('PASSWORD')

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = driver.find_element(By.ID, 'loginbutton')
        login_button.click()
        print("Logged in with Facebook.")

        continue_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Tiếp tục dưới tên Quốc Kỳ')]"))
        )
        continue_button.click()
        print("Clicked continue with national flag.")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'test-content'))
        )
        print("Test content loaded.")
    except TimeoutException as e:
        print(f"Error during login: {e}")


def extract_test_data(driver):
    # question_data = {
    #     "questionSetPart": [
    #         {
    #             "id": None,
    #             "audio": None,
    #             "page": None,
    #             "image": None,
    #             "fromQues": None,
    #             "toQues": None,
    #             "questionQuestionSet": [
    #                 {
    #                     "id": None,
    #                     "questionNumber": None,
    #                     "questionText": None,
    #                     "answers": {
    #                         "A": None,
    #                         "B": None,
    #                         "C": None,
    #                         "D": None
    #                     },
    #                     "partId": None
    #                 }
    #             ]
    #         }
    #     ]
    # }
    question_data = {"title": None, "questions": [], "audio": [], "images": []}
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, '.h4')
        test_title = title_element.text.strip()  # Lấy nội dung tiêu đề
        if test_title:  # Kiểm tra tiêu đề không rỗng
            question_data["title"] = test_title
            print(f"Tiêu đề bài kiểm tra: {test_title}")
        else:
            print("Tiêu đề bài kiểm tra rỗng!")
    except Exception as e:
        print(f"Lỗi khi trích xuất tiêu đề bài kiểm tra: {e}")

    # Trích xuất cả audio và hình ảnh
    def extract_audio_and_images_from_part(part_content):
        audio_urls = []
        img_urls = []

        # Trích xuất audio
        try:
            audio_elements = part_content.find_elements(By.TAG_NAME, 'audio')
            for audio_element in audio_elements:
                source_element = audio_element.find_element(By.TAG_NAME, 'source')
                audio_url = source_element.get_attribute('src')
                if audio_url not in audio_urls:  # Kiểm tra xem URL đã tồn tại chưa
                    audio_urls.append(audio_url)
        except Exception as e:
            print(f"Lỗi khi trích xuất audio: {e}")

        # Trích xuất ảnh
        try:
            img_elements = part_content.find_elements(By.TAG_NAME, 'img')
            for img_element in img_elements:
                img_url = img_element.get_attribute('src')
                if img_url not in img_urls:  # Kiểm tra xem URL đã tồn tại chưa
                    img_urls.append(img_url)
        except Exception as e:
            print(f"Lỗi khi trích xuất ảnh: {e}")

        return audio_urls, img_urls

    # Loop through different parts (Part 1 - Part 7)
    for part_id, content_id in zip(
            part_ids, content_ids
    ):
        print(f"Part ID: {part_id}, Content ID: {content_id}")
        try:
            part_tab = driver.find_element(By.ID, part_id)
            part_tab.click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, content_id)))

            part_content = driver.find_element(By.ID, content_id)

            # Trích xuất audio và hình ảnh từ phần nội dung
            audio_urls, img_urls = extract_audio_and_images_from_part(part_content)

            # Lưu các URL audio và ảnh vào question_data hoặc nơi bạn muốn
            for audio_url in audio_urls:
                print(f"Audio URL found: {audio_url}")
            for img_url in img_urls:
                print(f"Image URL found: {img_url}")

            # Thêm các URL audio và hình ảnh vào question_data
            question_data["audio"].extend(audio_urls)
            question_data["images"].extend(img_urls)

            # Trích xuất các câu hỏi
            question_wrapper = part_content.find_element(By.CSS_SELECTOR, '.test-questions-wrapper')
            question_elements = question_wrapper.find_elements(By.CSS_SELECTOR, '.question-wrapper')

            for wrapper in question_elements:
                question = {}
                question['question_number'] = wrapper.find_element(By.CSS_SELECTOR, '.question-number').text.strip()
                # question['question_text'] = wrapper.find_element(By.CSS_SELECTOR, '.question-text').text.strip()
                # Handle case where there is no question-text (missing question)
                try:
                    question['question_text'] = wrapper.find_element(By.CSS_SELECTOR, '.question-text').text.strip()
                except NoSuchElementException:
                    question['question_text'] = None  # Set to None if no question text is found
                    print(f"Warning: No question text found for question number {question['question_number']}")

                answers = []
                answer_elements = wrapper.find_elements(By.CSS_SELECTOR, '.question-answers .form-check')
                for answer in answer_elements:
                    answers.append(answer.find_element(By.CSS_SELECTOR, '.form-check-label').text.strip())

                question['answers'] = answers
                question_data["questions"].append(question)

            print(f"Extracted questions from {part_id}.")
        except Exception as e:
            print(f"Error extracting data from part {part_id}: {e}")

    return question_data


def save_data_to_json(data):
    file_path = "data-test/new-economy-test-2.json"

    # Initialize the data structure if the file is empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = {"questions": [], "audio": [], "images": []}

    # Add new data
    for question in data["questions"]:
        if question not in existing_data['questions']:
            existing_data['questions'].append(question)

    for audio_url in data["audio"]:
        if audio_url not in existing_data['audio']:
            existing_data['audio'].append(audio_url)

    for img_url in data["images"]:
        if img_url not in existing_data['images']:
            existing_data['images'].append(img_url)

    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)
    print("Data saved to JSON.")


def main():
    link = get_test_links()

    driver.get(link)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]'))
    )

    if handle_checkbox_selection():
        if submit_form():
            login_with_facebook()

            # Trích xuất dữ liệu câu hỏi, audio và hình ảnh
            question_data = extract_test_data(driver)

            # Lưu dữ liệu vào JSON
            save_data_to_json(question_data)
        else:
            print("Form submission failed, skipping.")
    else:
        print("Checkbox selection failed, skipping.")

    driver.quit()


if __name__ == "__main__":
    main()
