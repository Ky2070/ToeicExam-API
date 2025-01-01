import json
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException, NoSuchElementException

# Load environment variables for credentials
load_dotenv('C:/Users/nguye/PycharmProjects/EnglishTest/scrapper/.env')

# Setup paths for Chromedriver
base_path = r'C:\Users\nguye\PycharmProjects\EnglishTest\scrapper\chromedriver-win64'
chromedriver_path = os.path.join(base_path, 'chromedriver.exe')

# Initialize WebDriver
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service)


def get_test_links():
    driver.get('https://study4.com/tests/toeic/')
    print(driver.title)

    try:
        test_items = driver.find_elements(By.CLASS_NAME, 'testitem-wrapper')
        test_links = []

        for index, test_item in enumerate(test_items, start=1):
            a_tag = test_item.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            test_links.append(link)
            print(f"{index}. {link}")
        return test_links
    except Exception as e:
        print(f"Error extracting test links: {e}")
        return []


def handle_checkbox_selection():
    checkboxes_selected = 0
    max_scroll_attempts = 10
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
            driver.execute_script("window.scrollBy(0, window.innerHeight / 0.05);")
            WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")

    return checkboxes_selected >= 7


def submit_form():
    submit_button_found = False
    for _ in range(5):
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

        continue_button = WebDriverWait(driver, 15).until(
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


def extract_test_parts(driver):
    question_data = {"title": None, "questions": [], "audio": [], "images": []}

    # Lấy tiêu đề bài kiểm tra
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
    # Hàm hỗ trợ trích xuất audio và hình ảnh từ mỗi phần
    def extract_audio_and_images_from_part(part_content):
        audio_urls = []
        img_urls = []

        # Trích xuất audio
        try:
            audio_elements = part_content.find_elements(By.TAG_NAME, 'audio')
            for audio_element in audio_elements:
                source_element = audio_element.find_element(By.TAG_NAME, 'source')
                audio_url = source_element.get_attribute('src')
                if audio_url not in audio_urls:
                    audio_urls.append(audio_url)
        except Exception as e:
            print(f"Lỗi khi trích xuất audio: {e}")

        # Trích xuất ảnh
        try:
            img_elements = part_content.find_elements(By.TAG_NAME, 'img')
            for img_element in img_elements:
                img_url = img_element.get_attribute('src')
                if img_url not in img_urls:
                    img_urls.append(img_url)
        except Exception as e:
            print(f"Lỗi khi trích xuất ảnh: {e}")

        return audio_urls, img_urls

    try:

        # ID của các phần (Part 1 - Part 7)
        part_ids = ['729', '730', '731', '732', '733', '734', '735']

        # Lặp qua từng phần
        for part_id in part_ids:
            try:
                # Tìm tab và nội dung theo ID
                part_tab = driver.find_element(By.ID, f"pills-{part_id}-tab")
                part_content = driver.find_element(By.ID, f"partcontent-{part_id}")

                # Nhấn vào tab để hiển thị nội dung
                part_tab.click()
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, f"partcontent-{part_id}")))

                # Trích xuất audio và hình ảnh từ phần nội dung
                audio_urls, img_urls = extract_audio_and_images_from_part(part_content)
                question_data["audio"].extend(audio_urls)
                question_data["images"].extend(img_urls)

                # Trích xuất câu hỏi
                question_wrapper = part_content.find_element(By.CSS_SELECTOR, '.test-questions-wrapper')
                question_elements = question_wrapper.find_elements(By.CSS_SELECTOR, '.question-wrapper')

                for wrapper in question_elements:
                    question = {}
                    question['question_number'] = wrapper.find_element(By.CSS_SELECTOR, '.question-number').text.strip()

                    try:
                        question['question_text'] = wrapper.find_element(By.CSS_SELECTOR, '.question-text').text.strip()
                    except NoSuchElementException:
                        question['question_text'] = None
                        print(f"Warning: No question text found for question number {question['question_number']}")

                    answers = []
                    answer_elements = wrapper.find_elements(By.CSS_SELECTOR, '.question-answers .form-check')
                    for answer in answer_elements:
                        answers.append(answer.find_element(By.CSS_SELECTOR, '.form-check-label').text.strip())

                    question['answers'] = answers
                    question_data["questions"].append(question)

                print(f"Extracted data from part {part_id}.")

            except Exception as e:
                print(f"Lỗi khi trích xuất dữ liệu từ phần {part_tab.get_attribute('id')}: {e}")

    except Exception as e:
        print(f"Lỗi khi xử lý các phần của bài kiểm tra: {e}")

    return question_data


def extract_test_10_parts(driver):
    question_data_test_10 = {"title": None, "questions": [], "audio": [], "images": []}

    try:
        title_element = driver.find_element(By.CSS_SELECTOR, '.h4')
        test_title = title_element.text.strip()  # Lấy nội dung tiêu đề
        question_data_test_10["title"] = test_title
        print(f"Test Title: {test_title}")
    except Exception as e:
        print(f"Lỗi khi trích xuất tiêu đề bài kiểm tra: {e}")
    # Hàm hỗ trợ trích xuất audio và hình ảnh từ mỗi phần

    def extract_audio_and_images_from_part(part_content):
        audio_urls = []
        img_urls = []

        # Trích xuất audio
        try:
            audio_elements = part_content.find_elements(By.TAG_NAME, 'audio')
            for audio_element in audio_elements:
                source_element = audio_element.find_element(By.TAG_NAME, 'source')
                audio_url = source_element.get_attribute('src')
                if audio_url not in audio_urls:
                    audio_urls.append(audio_url)
        except Exception as e:
            print(f"Lỗi khi trích xuất audio: {e}")

        # Trích xuất ảnh
        try:
            img_elements = part_content.find_elements(By.TAG_NAME, 'img')
            for img_element in img_elements:
                img_url = img_element.get_attribute('src')
                if img_url not in img_urls:
                    img_urls.append(img_url)
        except Exception as e:
            print(f"Lỗi khi trích xuất ảnh: {e}")

        return audio_urls, img_urls

    try:

        # ID của các phần (Part 1 - Part 7)
        part_ids = ['3153', '3154', '3155', '3156', '3157', '3158', '3159']

        # Lặp qua từng phần
        for part_id in part_ids:
            try:
                # Tìm tab và nội dung theo ID
                part_tab = driver.find_element(By.ID, f"pills-{part_id}-tab")
                part_content = driver.find_element(By.ID, f"partcontent-{part_id}")

                # Nhấn vào tab để hiển thị nội dung
                part_tab.click()
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, f"partcontent-{part_id}")))

                # Trích xuất audio và hình ảnh từ phần nội dung
                audio_urls, img_urls = extract_audio_and_images_from_part(part_content)
                question_data_test_10["audio"].extend(audio_urls)
                question_data_test_10["images"].extend(img_urls)

                # Trích xuất câu hỏi
                question_wrapper = part_content.find_element(By.CSS_SELECTOR, '.test-questions-wrapper')
                question_elements = question_wrapper.find_elements(By.CSS_SELECTOR, '.question-wrapper')

                for wrapper in question_elements:
                    question = {}
                    question['question_number'] = wrapper.find_element(By.CSS_SELECTOR, '.question-number').text.strip()

                    try:
                        question['question_text'] = wrapper.find_element(By.CSS_SELECTOR, '.question-text').text.strip()
                    except NoSuchElementException:
                        question['question_text'] = None
                        print(f"Warning: No question text found for question number {question['question_number']}")

                    answers = []
                    answer_elements = wrapper.find_elements(By.CSS_SELECTOR, '.question-answers .form-check')
                    for answer in answer_elements:
                        answers.append(answer.find_element(By.CSS_SELECTOR, '.form-check-label').text.strip())

                    question['answers'] = answers
                    question_data_test_10["questions"].append(question)

                print(f"Extracted data from part {part_id}.")

            except Exception as e:
                print(f"Lỗi khi trích xuất dữ liệu từ phần {part_tab.get_attribute('id')}: {e}")

    except Exception as e:
        print(f"Lỗi khi xử lý các phần của bài kiểm tra: {e}")

    return question_data_test_10


def save_data_to_json(data):
    file_path = "data.json"

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


def save_data_10_to_json(data):
    file_path = "data10.json"

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
    test_links = get_test_links()

    for link in test_links:
        driver.get(link)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]'))
        )

        if handle_checkbox_selection():
            if submit_form():
                login_with_facebook()

                # Trích xuất dữ liệu câu hỏi, audio và hình ảnh
                question_data = extract_test_parts(driver)
                # Lưu dữ liệu vào JSON
                save_data_to_json(question_data)

                question_data_test_10 = extract_test_10_parts(driver)
                # Lưu dữ liệu vào JSON
                save_data_10_to_json(question_data_test_10)
            else:
                print("Form submission failed, skipping.")
        else:
            print("Checkbox selection failed, skipping.")

    driver.quit()


if __name__ == "__main__":
    main()