import json
import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException

base_path = r'C:\Users\nguye\PycharmProjects\EnglishTest\scrapper\chromedriver-win64'
chromedriver_path = os.path.join(base_path, 'chromedriver.exe')

# Tạo service và driver
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service)

# Mở trang web
driver.get('https://study4.com/tests/toeic/')
print(driver.title)

try:
    # Tìm tất cả các thẻ div chứa bài thi
    test_items = driver.find_elements(By.CLASS_NAME, 'testitem-wrapper')

    # Lặp qua các phần tử và xử lý từng bài thi
    for index, test_item in enumerate(test_items, start=2):
        a_tag = test_item.find_element(By.TAG_NAME, 'a')
        link = a_tag.get_attribute('href')
        print(f"{index}. {link}")

        # Chuyển đến trang chi tiết bài thi
        driver.get(link)

        # Đợi trang tải hoàn tất
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]'))
            )
        except TimeoutException:
            print(f"Lỗi: Không tìm thấy checkbox trên trang {link}. Bỏ qua.")
            continue

        # Chọn checkbox
        checkboxes_selected = 0
        max_scroll_attempts = 10
        for scroll_attempt in range(max_scroll_attempts):
            # Cập nhật danh sách checkbox hiện tại
            checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]')
            for checkbox in checkboxes:
                if not checkbox.is_selected() and checkbox.is_displayed():
                    try:
                        # Cuộn đến checkbox và chọn
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                              checkbox)
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(checkbox))
                        checkbox.click()
                        checkboxes_selected += 1
                        print(f"Checkbox đã chọn: {checkboxes_selected}")
                        if checkboxes_selected >= 7:
                            break
                    except (TimeoutException, ElementClickInterceptedException) as e:
                        print(f"Lỗi khi tích checkbox: {e}. Bỏ qua checkbox này.")

            if checkboxes_selected >= 7:
                print("Đã chọn đủ 7 checkbox. Tiếp tục cuộn để tìm nút Submit.")
            else:
                # Cuộn thêm
                driver.execute_script("window.scrollBy(0, window.innerHeight / 0.05);")
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )

        if checkboxes_selected < 7:
            print("Không thể chọn đủ 7 checkbox. Bỏ qua bài thi này.")
            continue

        # Cuộn đến nút Submit và gửi form luyện tập
        submit_button_found = False
        for _ in range(5):  # Thử cuộn tối đa 10 lần
            try:
                # Tìm lại nút Submit sau mỗi lần cuộn
                submit_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-primary[type="submit"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                      submit_button)
                submit_button.click()
                print("Nút 'Luyện tập' đã được bấm thành công!")
                submit_button_found = True
                break
            except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
                print(f"Lỗi khi bấm nút 'Luyện tập': {e}. Cuộn thêm.")
                driver.execute_script("window.scrollBy(0, window.innerHeight / 0.05);")

        if not submit_button_found:
            print("Không thể bấm nút 'Luyện tập'. Bỏ qua bài thi này.")
            continue

        # Đợi trang đăng nhập tải
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-12.f-login-block'))
            )
            print("Trang đăng nhập đã tải xong.")

            # Tìm và bấm nút 'Đăng nhập với Facebook'
            facebook_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.s-button.f-login-button'))
            )
            facebook_button.click()
            print("Đã bấm nút 'Đăng nhập với Facebook'.")

            # Đợi trang Facebook tải và điền thông tin đăng nhập
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'email'))
            )

            # Điền username và password
            username_field = driver.find_element(By.ID, 'email')
            password_field = driver.find_element(By.ID, 'pass')

            # Tải các biến môi trường từ file .env
            load_dotenv('C:/Users/nguye/PycharmProjects/EnglishTest/scrapper/.env')

            # Đọc thông tin đăng nhập từ biến môi trường
            username = os.getenv('GMAIL')
            password = os.getenv('PASSWORD')

            # Sử dụng các giá trị đã đọc để nhập vào các trường username và password
            username_field.send_keys(username)
            password_field.send_keys(password)

            # Bấm nút đăng nhập
            login_button = driver.find_element(By.ID, 'loginbutton')
            login_button.click()
            print("Đã bấm nút 'Đăng nhập'.")

            # Sau khi đăng nhập thành công, bấm vào nút "Tiếp tục dưới tên Quốc Kỳ"
            try:
                # Đợi nút "Tiếp tục dưới tên Quốc Kỳ" có thể click được
                continue_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Tiếp tục dưới tên Quốc Kỳ')]"))
                )
                continue_button.click()
                print("Đã bấm nút 'Tiếp tục dưới tên Quốc Kỳ'.")

                # Đợi trang bài thi tải hoàn tất bằng cách kiểm tra một phần tử xác định có sẵn trên trang bài thi
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, 'test-content'))
                )
                print("Trang bài thi đã được tải xong.")
            except TimeoutException:
                print("Lỗi: Không tìm thấy nút 'Tiếp tục dưới tên Quốc Kỳ' hoặc trang bài thi không tải kịp.")

        except TimeoutException:
            print("Lỗi: Không tìm thấy trang đăng nhập Facebook hoặc các phần tử cần thiết. Bỏ qua.")
            continue

        # Đường dẫn tới file JSON
        DATA_FILE = "data.json"


        def load_existing_data(file_path):
            """Tải dữ liệu từ file JSON."""
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        return json.load(file)
                except json.JSONDecodeError:
                    print("File JSON bị lỗi hoặc không hợp lệ. Tạo dữ liệu mới.")
                    return {"audio": [], "images": [], "questions": []}
            return {"audio": [], "images": [], "questions": []}


        def save_data(file_path, data):
            """Lưu dữ liệu vào file JSON."""
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)


        def save_question_data(file_path, question_data):
            """Lưu thông tin câu hỏi nếu chưa tồn tại."""
            data = load_existing_data(file_path)
            if question_data not in data["questions"]:
                data["questions"].append(question_data)
                save_data(file_path, data)
                print(f"Đã lưu câu hỏi: {question_data}")
            else:
                print("Câu hỏi đã tồn tại trong dữ liệu.")


        def save_url_if_not_exists(file_path, url, key):
            """Lưu URL vào danh mục (audio hoặc images) nếu chưa tồn tại."""
            data = load_existing_data(file_path)
            if url not in data[key]:
                data[key].append(url)
                save_data(file_path, data)
                print(f"Đã lưu URL {url} vào danh mục '{key}'.")
            else:
                print(f"URL {url} đã tồn tại trong danh mục '{key}'.")


        def extract_questions_from_parts(driver):
            """Trích xuất câu hỏi từ các phần khác nhau (Part 1 đến Part 7)."""
            additional_content = None
            parts = [
                {'id': 'pills-729-tab', 'content_id': 'partcontent-729'},  # Part 1
                {'id': 'pills-730-tab', 'content_id': 'partcontent-730'},  # Part 2
                {'id': 'pills-731-tab', 'content_id': 'partcontent-731'},  # Part 3
                {'id': 'pills-732-tab', 'content_id': 'partcontent-732'},  # Part 4
                {'id': 'pills-733-tab', 'content_id': 'partcontent-733'},  # Part 5
                {'id': 'pills-734-tab', 'content_id': 'partcontent-734'},  # Part 6
                {'id': 'pills-735-tab', 'content_id': 'partcontent-735'},  # Part 7
            ]
            for part in parts:
                try:
                    # Chuyển sang tab phần tương ứng
                    part_tab = driver.find_element(By.ID, part['id'])
                    part_tab.click()

                    # Đợi phần nội dung của tab hiển thị
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, part['content_id']))
                    )

                    # Sau khi chuyển đến tab, trích xuất dữ liệu từ phần này
                    part_content = driver.find_element(By.ID, part['content_id'])

                    # Trích xuất các câu hỏi trong phần này
                    question_wrapper = part_content.find_element(By.CSS_SELECTOR, '.test-questions-wrapper')
                    question_elements = question_wrapper.find_elements(By.CSS_SELECTOR, '.question-wrapper')

                    for wrapper in question_elements:
                        try:
                            # Lấy số thứ tự câu hỏi
                            question_number_element = wrapper.find_element(By.CSS_SELECTOR, '.question-number')
                            question_number = question_number_element.text.strip()

                            # Lấy nội dung câu hỏi
                            try:
                                question_text_element = wrapper.find_element(By.CSS_SELECTOR, '.question-text')
                                question_text = question_text_element.text.strip()
                            except Exception:
                                question_text = None  # Nếu không tìm thấy, gán là None

                            # Lấy danh sách các đáp án
                            answers_elements = wrapper.find_elements(By.CSS_SELECTOR, '.question-answers .form-check')
                            answers = [
                                answer_element.find_element(By.CSS_SELECTOR, '.form-check-label').text.strip()
                                for answer_element in answers_elements
                            ]
                            print(part['id'])
                            # Chỉ xử lý thêm nội dung cho Part 6 và Part 7
                            if part['id'] in ['pills-734-tab', 'pills-735-tab']:
                                try:
                                    # Tìm tất cả các phần tử 'question-twocols-left'
                                    question_twocols_left_elements = part_content.find_elements(By.CSS_SELECTOR,
                                                                                                '.question-twocols-left')
                                    all_paragraphs_content = []

                                    for element in question_twocols_left_elements:
                                        try:
                                            # Debug: In HTML của phần tử hiện tại
                                            print("HTML hiện tại:", element.get_attribute('outerHTML'))

                                            # paragraph = element.find_element(By.XPATH,
                                            #                                  './/div[@class="context-content text-highlightable"]/div/p')
                                            all_paragraphs_content.append(element.get_attribute('outerHTML').strip())
                                        except Exception as inner_e:
                                            print(f"Lỗi khi tìm thẻ <p>: {inner_e}")
                                    # Nếu có nội dung thẻ <p>, lưu trữ
                                    if all_paragraphs_content:
                                        additional_content = all_paragraphs_content
                                except Exception as e:
                                    print(f"Lỗi khi xử lý 'question-twocols-left': {e}")

                            # Lưu thông tin câu hỏi vào JSON
                            question_data = {
                                "question_number": question_number,
                                "question_text": question_text,
                                "answers": answers,
                                "page": None  # Thêm nội dung thẻ <p> nếu có
                            }
                            save_question_data(DATA_FILE, question_data)

                        except Exception as e:
                            print(f"Lỗi khi xử lý câu hỏi trong question-wrapper: {e}")
                except Exception as e:
                    print(f"Lỗi khi xử lý phần {part['content_id']}: {e}")


        def extract_audio_urls(driver):
            """Trích xuất URL audio từ trang web."""
            try:
                audio_elements = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'audio'))
                )
                for audio_element in audio_elements:
                    source_element = audio_element.find_element(By.TAG_NAME, 'source')
                    audio_url = source_element.get_attribute('src')
                    save_url_if_not_exists(DATA_FILE, audio_url, "audio")
            except Exception as e:
                print(f"Lỗi khi trích xuất audio: {e}")


        def extract_image_urls(driver):
            """Trích xuất URL ảnh từ trang web."""
            try:
                img_elements = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'img'))
                )
                for img_element in img_elements:
                    img_url = img_element.get_attribute('src')
                    save_url_if_not_exists(DATA_FILE, img_url, "images")
            except Exception as e:
                print(f"Lỗi khi trích xuất ảnh: {e}")

        # Hàm chính để chạy toàn bộ quá trình trích xuất
        def run_extraction(driver):
            try:
                extract_audio_urls(driver)
                extract_image_urls(driver)
                extract_questions_from_parts(driver)
            except Exception as e:
                print(f"Lỗi khi chạy script: {e}")


        run_extraction(driver)

        driver.get('https://study4.com/tests/toeic/')
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'testitem-wrapper'))
            )
            print("Đã trở về trang chủ thành công.")
        except TimeoutException:
            print("Lỗi: Không thể quay về trang chủ.")
except Exception as e:
    print(f"Đã xảy ra lỗi không mong muốn: {e}")
finally:
    # Đóng driver
    driver.close()
    print("Đã đóng driver thành công.")
