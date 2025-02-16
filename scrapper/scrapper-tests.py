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
        # Tìm phần tử có id là 'new-economy-toeic-test-2'
        test_item = driver.find_element(By.ID, 'new-economy-toeic-test-10')

        # Lấy thẻ <a> trong test_item để lấy link
        a_tag = test_item.find_element(By.XPATH,
                                       "/html/body/div[3]/div[2]/div[3]/div/div[1]/div[1]/div/div[2]/div/div/a[2]")  # Lấy thẻ cha của thẻ <h2> chứa id
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


def extract_test_data(driver):
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
            ['pills-3153-tab', 'pills-3154-tab', 'pills-3155-tab', 'pills-3156-tab', 'pills-3157-tab', 'pills-3158-tab',
             'pills-3159-tab'],
            ['partcontent-3153', 'partcontent-3154', 'partcontent-3155', 'partcontent-3156', 'partcontent-3157',
             'partcontent-3158', 'partcontent-3159']
    ):
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
    file_path = "new-economy-test-10.json"

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
