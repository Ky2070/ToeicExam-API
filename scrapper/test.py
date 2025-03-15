import json
import os
import re
import time
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


def find_chrome_from_registry():
    # Các đường dẫn trong registry để tìm chrome.exe
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",  # Đối với 64-bit hệ điều hành
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
    ]

    for registry_path in registry_paths:
        try:
            # Mở registry key, tùy trường hợp ứng dụng chrome thì chỗ này có thể là HKEY_CURRENT_USER
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
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

# Lấy test_id từ dữ liệu đọc được
test_id = data.get('test_id')
print(f"Test_id: {test_id}")


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
            driver.execute_script("window.scrollBy(0, window.innerHeight / 0.025);")
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
            driver.execute_script("window.scrollBy(0, window.innerHeight / 0.025);")

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


# def extract_test_data(driver):
#     question_data = {"title": [], "questions_by_part": {}}
#
#     # Lấy tiêu đề bài kiểm tra
#     try:
#         title_element = driver.find_element(By.TAG_NAME, 'h1')
#         test_title = title_element.text.strip()
#         test_title = re.sub(r'\s*Thoát$', '', test_title).strip()  # Loại bỏ chữ "Thoát" nếu có
#         question_data["title"] = test_title
#         print(f"📌 Tiêu đề bài kiểm tra: {test_title}")
#     except Exception as e:
#         print(f"❌ Lỗi khi trích xuất tiêu đề bài kiểm tra: {e}")
#
#     part_tabs = driver.find_elements(By.XPATH, "//a[contains(@class, 'nav-link') and contains(@id, 'pills-')]")
#
#     # Duyệt qua từng phần (Part)
#     for part_tab in part_tabs:
#         try:
#             part_name = part_tab.text.strip()
#             part_id = part_tab.get_attribute("href").split("#")[-1]
#             part_container = driver.find_element(By.ID, part_id)
#
#             print(f"🔍 Đang xử lý: {part_name}")
#             driver.execute_script("arguments[0].click();", part_tab)
#             time.sleep(2)  # Đợi nội dung load
#
#             # Tìm `test-question-wrapper` (chứa tất cả context-wrapper và question-wrapper)
#             test_question_wrapper = part_container.find_element(By.CSS_SELECTOR, '.test-questions-wrapper')
#             questions_for_part = []
#
#             if part_name in ["Part 3", "Part 4"]:
#                 # Xử lý các nhóm câu hỏi (question-group-wrapper)
#                 question_groups = test_question_wrapper.find_elements(By.CSS_SELECTOR, '.question-group-wrapper')
#
#                 for group in question_groups:
#                     try:
#                         context_wrapper = group.find_element(By.CSS_SELECTOR, '.context-wrapper')
#                         question_columns = group.find_elements(By.CSS_SELECTOR,
#                                                                '.questions-wrapper.two-cols .question-wrapper')
#                         print(f"🔍 Tìm thấy {len(question_columns)} câu hỏi trong nhóm Part 3/4")
#                         # Lấy audio từ context-wrapper
#                         audio_urls = [audio.get_attribute('src') for audio in
#                                       context_wrapper.find_elements(By.TAG_NAME, 'source')]
#                         # Lấy hình ảnh từ context-wrapper
#                         img_urls = [img.get_attribute('src') for img in
#                                     context_wrapper.find_elements(By.TAG_NAME, 'img')]
#                         # Lấy danh sách câu hỏi trong nhóm
#                         group_questions = []
#                         for question_wrapper in question_columns:
#                             question_number = question_wrapper.find_element(By.CLASS_NAME,
#                                                                             'question-number').text.strip()
#                             question_text = question_wrapper.find_element(By.CLASS_NAME,
#                                                                           'question-text').text.strip() if question_wrapper.find_elements(
#                                 By.CLASS_NAME, 'question-text') else None
#
#                             # Lấy đáp án
#                             answer_elements = question_wrapper.find_elements(By.CSS_SELECTOR,
#                                                                              '.question-answers .form-check')
#                             answers = {"A": "", "B": "", "C": "", "D": ""}
#                             options_found = 0
#
#                             for answer in answer_elements:
#                                 try:
#                                     label = answer.find_element(By.CSS_SELECTOR, '.form-check-label').text.strip()
#                                     option_element = answer.find_element(By.CSS_SELECTOR, 'input')
#                                     option = option_element.get_attribute("value") if option_element.get_attribute(
#                                         "value") else None
#                                     if option in answers and option is not None:
#                                         answers[option] = label.split(". ", 1)[1] if ". " in label else ""
#                                         options_found += 1
#                                 except Exception as e:
#                                     print(f"Lỗi lấy đáp án: {e}")
#
#                             if options_found < 4:
#                                 answers.pop("D", None)
#
#                             # Gom dữ liệu câu hỏi
#                             group_questions.append({
#                                 "question_number": question_number,
#                                 "question_text": question_text,
#                                 "answers": answers
#                             })
#
#                         # Lưu nhóm câu hỏi cùng với audio
#                         questions_for_part.append({
#                             "audio": audio_urls.copy(),
#                             "image": img_urls.copy(),
#                             "question_set": len(question_columns),
#                             "questions": group_questions
#                         })
#                     except Exception as e:
#                         print(f"❌ Lỗi xử lý question-group-wrapper: {e}")
#
#             else:
#             # Xử lý các phần khác (không phải Part 3, Part 4)
#             all_contexts = test_question_wrapper.find_elements(By.CSS_SELECTOR, '.context-wrapper')
#             all_questions = test_question_wrapper.find_elements(By.CSS_SELECTOR, '.question-wrapper')
#
#             for i in range(min(len(all_contexts), len(all_questions))):
#                 try:
#                     context_wrapper = all_contexts[i]
#                     question_wrapper = all_questions[i]
#
#                     # Lấy audio
#                     audio_urls = [audio.get_attribute('src') for audio in
#                                   context_wrapper.find_elements(By.TAG_NAME, 'source')]
#                     # Lấy hình ảnh từ context-wrapper
#                     img_urls = [img.get_attribute('src') for img in
#                                 context_wrapper.find_elements(By.TAG_NAME, 'img')]
#
#                     question_number = question_wrapper.find_element(By.CLASS_NAME, 'question-number').text.strip()
#                     question_text = question_wrapper.find_element(By.CLASS_NAME,
#                                                                   'question-text').text.strip() if question_wrapper.find_elements(
#                         By.CLASS_NAME, 'question-text') else None
#
#                     # Lấy đáp án
#                     answer_elements = question_wrapper.find_elements(By.CSS_SELECTOR,
#                                                                      '.question-answers .form-check')
#                     answers = {"A": "", "B": "", "C": "", "D": ""}
#                     options_found = 0
#
#                     for answer in answer_elements:
#                         try:
#                             label = answer.find_element(By.CSS_SELECTOR, '.form-check-label').text.strip()
#                             option_element = answer.find_element(By.CSS_SELECTOR, 'input')
#                             option = option_element.get_attribute("value") if option_element.get_attribute(
#                                 "value") else None
#                             if option in answers and option is not None:
#                                 answers[option] = label.split(". ", 1)[1] if ". " in label else ""
#                                 options_found += 1
#                         except Exception as e:
#                             print(f"Lỗi lấy đáp án: {e}")
#
#                     if options_found < 4:
#                         answers.pop("D", None)
#
#                     questions_for_part.append({
#                         "question_number": question_number,
#                         "question_text": question_text,
#                         "answers": answers,
#                         "audio": audio_urls.copy(),
#                         "image": img_urls.copy()
#
#                     })
#                 except Exception as e:
#                     print(f"❌ Lỗi khi xử lý context-wrapper & question-wrapper thứ {i} trong {part_name}: {e}")
#
#         question_data["questions_by_part"][part_name] = questions_for_part
#         print(f"✅ Đã trích xuất xong dữ liệu từ {part_name}.")
#
#     except Exception as e:
#         print(f"❌ Lỗi khi trích xuất dữ liệu từ {part_name}: {e}")
#
# return question_data

def extract_test_data(driver):
    question_data = {"title": [], "questions_by_part": {}}

    # Lấy tiêu đề bài kiểm tra
    try:
        title_element = driver.find_element(By.TAG_NAME, 'h1')
        test_title = title_element.text.strip()
        test_title = re.sub(r'\s*Thoát$', '', test_title).strip()  # Loại bỏ chữ "Thoát" nếu có
        question_data["title"] = test_title
        print(f"📌 Tiêu đề bài kiểm tra: {test_title}")
    except Exception as e:
        print(f"❌ Lỗi khi trích xuất tiêu đề bài kiểm tra: {e}")

    part_tabs = driver.find_elements(By.XPATH, "//a[contains(@class, 'nav-link') and contains(@id, 'pills-')]")

    # Duyệt qua từng phần (Part)
    for part_tab in part_tabs:
        try:
            part_name = part_tab.text.strip()
            part_id = part_tab.get_attribute("href").split("#")[-1]
            part_container = driver.find_element(By.ID, part_id)

            print(f"🔍 Đang xử lý: {part_name}")
            driver.execute_script("arguments[0].click();", part_tab)
            time.sleep(2)  # Đợi nội dung load

            test_question_wrapper = part_container.find_element(By.CSS_SELECTOR, '.test-questions-wrapper')
            questions_for_part = []

            if part_name in ["Part 3", "Part 4"]:
                questions_for_part = extract_part_3_4(test_question_wrapper)
            elif part_name in ["Part 6", "Part 7"]:
                questions_for_part = extract_part_6_7(test_question_wrapper)
            else:
                questions_for_part = extract_other_parts(test_question_wrapper, part_name)

            question_data["questions_by_part"][part_name] = questions_for_part
            print(f"✅ Đã trích xuất xong dữ liệu từ {part_name}.")

        except Exception as e:
            print(f"❌ Lỗi khi trích xuất dữ liệu từ {part_name}: {e}")

    return question_data


def extract_other_parts(test_question_wrapper, part_name):
    """
    Xử lý trích xuất dữ liệu cho các Part KHÔNG phải Part 3, 4, 6, 7.
    """
    questions_for_part = []

    try:
        all_contexts = test_question_wrapper.find_elements(By.CSS_SELECTOR, '.context-wrapper')
        all_questions = test_question_wrapper.find_elements(By.CSS_SELECTOR, '.question-wrapper')

        for i in range(min(len(all_contexts), len(all_questions))):
            try:
                context_wrapper = all_contexts[i]
                question_wrapper = all_questions[i]

                # Lấy audio
                audio_urls = [audio.get_attribute('src') for audio in
                              context_wrapper.find_elements(By.TAG_NAME, 'source')]
                # Lấy hình ảnh từ context-wrapper
                img_urls = [img.get_attribute('src') for img in
                            context_wrapper.find_elements(By.TAG_NAME, 'img')]

                question_number = question_wrapper.find_element(By.CLASS_NAME, 'question-number').text.strip()
                question_text = question_wrapper.find_element(By.CLASS_NAME,
                                                              'question-text').text.strip() if question_wrapper.find_elements(
                    By.CLASS_NAME, 'question-text') else None

                # Lấy đáp án
                answer_elements = question_wrapper.find_elements(By.CSS_SELECTOR,
                                                                 '.question-answers .form-check')
                answers = {"A": "", "B": "", "C": "", "D": ""}
                options_found = 0

                for answer in answer_elements:
                    try:
                        label = answer.find_element(By.CSS_SELECTOR, '.form-check-label').text.strip()
                        option_element = answer.find_element(By.CSS_SELECTOR, 'input')
                        option = option_element.get_attribute("value") if option_element.get_attribute(
                            "value") else None
                        if option in answers and option is not None:
                            answers[option] = label.split(". ", 1)[1] if ". " in label else ""
                            options_found += 1
                    except Exception as e:
                        print(f"Lỗi lấy đáp án: {e}")

                if options_found < 4:
                    answers.pop("D", None)

                questions_for_part.append({
                    "question_set": 1,
                    "question_number": question_number,
                    "question_text": question_text,
                    "answers": answers,
                    "audio": audio_urls.copy(),
                    "image": img_urls.copy()
                })
            except Exception as e:
                print(f"❌ Lỗi khi xử lý context-wrapper & question-wrapper thứ {i} trong {part_name}: {e}")

    except Exception as e:
        print(f"❌ Lỗi khi trích xuất dữ liệu từ {part_name}: {e}")

    return questions_for_part


def extract_part_3_4(test_question_wrapper):
    questions_for_part = []

    # Xử lý các nhóm câu hỏi
    question_groups = test_question_wrapper.find_elements(By.CSS_SELECTOR, '.question-group-wrapper')
    for group in question_groups:
        try:
            context_wrapper = group.find_element(By.CSS_SELECTOR, '.context-wrapper')
            audio_urls = [audio.get_attribute('src') for audio in context_wrapper.find_elements(By.TAG_NAME, 'source')]
            img_urls = [img.get_attribute('src') for img in context_wrapper.find_elements(By.TAG_NAME, 'img')]

            # Lấy danh sách câu hỏi
            question_columns = group.find_elements(By.CSS_SELECTOR, '.questions-wrapper.two-cols .question-wrapper')
            group_questions = []

            for question_wrapper in question_columns:
                question_number = question_wrapper.find_element(By.CLASS_NAME, 'question-number').text.strip()
                question_text = question_wrapper.find_element(By.CLASS_NAME,
                                                              'question-text').text.strip() if question_wrapper.find_elements(
                    By.CLASS_NAME, 'question-text') else None

                answers = extract_answers(question_wrapper)

                group_questions.append({
                    "question_number": question_number,
                    "question_text": question_text,
                    "answers": answers
                })

            questions_for_part.append({
                "audio": audio_urls.copy(),
                "image": img_urls.copy(),
                "text": "",
                "question_set": len(question_columns),
                "questions": group_questions
            })
        except Exception as e:
            print(f"❌ Lỗi xử lý nhóm câu hỏi (Part 3-4): {e}")

    return questions_for_part


def extract_part_6_7(test_question_wrapper):
    questions_for_part = []
    # Xử lý các nhóm câu hỏi
    question_groups = test_question_wrapper.find_elements(By.CSS_SELECTOR, '.question-group-wrapper > .question-twocols')
    for group in question_groups:
        # Lấy đoạn văn từ `.question-twocols-left .context-wrapper`
        try:
            context_text = group.find_element(By.CSS_SELECTOR,
                                              '.question-twocols-left > .context-wrapper').text.strip()
        except:
            context_text = ""

        # Lấy danh sách câu hỏi trong `.question-twocols-right .question-wrapper`
        question_columns = group.find_elements(By.CSS_SELECTOR, '.question-twocols-right .questions-wrapper .question-wrapper')
        print(f"Tìm thấy {len(question_columns)} bộ câu hỏi")
        group_questions = []

        for question_wrapper in question_columns:
            try:
                question_number = question_wrapper.find_element(By.CLASS_NAME, 'question-number').text.strip()
                question_text = question_wrapper.find_element(By.CLASS_NAME,
                                                              'question-text').text.strip() if question_wrapper.find_elements(
                    By.CLASS_NAME, 'question-text') else None

                answers = extract_answers(question_wrapper)

                group_questions.append({
                    "question_number": question_number,
                    "question_text": question_text,
                    "answers": answers
                })
            except Exception as e:
                print(f"❌ Lỗi xử lý câu hỏi (Part 6-7): {e}")

        questions_for_part.append({
            "audio": [],
            "image": [],
            "text": context_text,
            "question_set": len(question_columns),
            "questions": group_questions
        })

    return questions_for_part


def extract_answers(question_wrapper):
    answers = {"A": "", "B": "", "C": "", "D": ""}
    options_found = 0

    answer_elements = question_wrapper.find_elements(By.CSS_SELECTOR, '.question-answers .form-check')
    for answer in answer_elements:
        try:
            label = answer.find_element(By.CSS_SELECTOR, '.form-check-label').text.strip()
            option_element = answer.find_element(By.CSS_SELECTOR, 'input')
            option = option_element.get_attribute("value") if option_element.get_attribute("value") else None
            if option in answers and option is not None:
                answers[option] = label.split(". ", 1)[1] if ". " in label else ""
                options_found += 1
        except Exception as e:
            print(f"Lỗi lấy đáp án: {e}")

    if options_found < 4:
        answers.pop("D", None)

    return answers


def save_data_to_json(data):
    file_path = f"data-test/{test_id}.json"

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = {"title": "", "questions_by_part": {}}

    existing_data["title"] = data.get("title", existing_data["title"])

    for part_name, questions in data.get("questions_by_part", {}).items():
        if part_name not in existing_data["questions_by_part"]:
            existing_data["questions_by_part"][part_name] = []

        if part_name in ["Part 3", "Part 4"]:
            # Lưu theo nhóm câu hỏi
            for new_group in questions:
                if new_group not in existing_data["questions_by_part"][part_name]:
                    existing_data["questions_by_part"][part_name].append(new_group)

        elif part_name in ["Part 6", "Part 7"]:
            # Lưu theo đoạn văn bản + câu hỏi liên quan
            for new_passage in questions:
                passage_text = new_passage.get("text", "")  # Đổi "passage" thành "text"
                existing_passages = [
                    p for p in existing_data["questions_by_part"][part_name]
                    if p.get("text", "") == passage_text  # Đổi "passage" thành "text"
                ]

                if existing_passages:
                    existing_passages[0]["questions"].extend(
                        q for q in new_passage["questions"] if q not in existing_passages[0]["questions"]
                    )
                else:
                    existing_data["questions_by_part"][part_name].append(new_passage)

        else:
            # Lưu từng câu hỏi riêng lẻ (cho các Part khác)
            for new_question in questions:
                if isinstance(new_question, dict) and "question_number" in new_question:
                    if new_question not in existing_data["questions_by_part"][part_name]:
                        existing_data["questions_by_part"][part_name].append(new_question)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)

    print(f"✅ Dữ liệu đã được lưu vào {file_path}")

# def save_data_to_json(data):
#     file_path = f"data-test/{test_id}.json"
#
#     if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             existing_data = json.load(file)
#     else:
#         existing_data = {"title": "", "questions_by_part": {}}
#
#     existing_data["title"] = data.get("title", existing_data["title"])
#
#     for part_name, questions in data.get("questions_by_part", {}).items():
#         if part_name not in existing_data["questions_by_part"]:
#             existing_data["questions_by_part"][part_name] = []
#
#         if part_name in ["Part 3", "Part 4"]:
#             # Lưu theo nhóm câu hỏi
#             for new_group in questions:
#                 if new_group not in existing_data["questions_by_part"][part_name]:
#                     existing_data["questions_by_part"][part_name].append(new_group)
#         else:
#             # Lưu từng câu hỏi riêng lẻ
#             for new_question in questions:
#                 if isinstance(new_question, dict) and "question_number" in new_question:
#                     if new_question not in existing_data["questions_by_part"][part_name]:
#                         existing_data["questions_by_part"][part_name].append(new_question)
#
#     with open(file_path, 'w', encoding='utf-8') as file:
#         json.dump(existing_data, file, indent=4, ensure_ascii=False)
#
#     print(f"✅ Dữ liệu đã được lưu vào {file_path}")


# def save_data_to_json(data):
#     file_path = f"data-test/{test_id}.json"
#
#     if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             existing_data = json.load(file)
#     else:
#         existing_data = {"title": "", "questions_by_part": {}}
#
#     existing_data["title"] = data.get("title", existing_data["title"])
#
#     for part_name, questions in data["questions_by_part"].items():
#         if part_name not in existing_data["questions_by_part"]:
#             existing_data["questions_by_part"][part_name] = []
#
#         for question in questions:
#             if question not in existing_data["questions_by_part"][part_name]:
#                 existing_data["questions_by_part"][part_name].append(question)
#
#     with open(file_path, 'w', encoding='utf-8') as file:
#         json.dump(existing_data, file, indent=4, ensure_ascii=False)
#     print(f"Data saved successfully to {file_path}")


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
            print("Dữ liệu chuẩn bị lưu:", question_data)  # Debug kiểm tra dữ liệu
            # Lưu dữ liệu vào JSON
            save_data_to_json(question_data)
        else:
            print("Form submission failed, skipping.")
    else:
        print("Checkbox selection failed, skipping.")

    driver.quit()


if __name__ == "__main__":
    main()
