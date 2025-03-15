import json
import os
import re
import time
import winreg
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Xác định đường dẫn thư mục chứa script và file .env
env_path = Path(__file__).parent / '.env'
# Load biến môi trường từ file .env
print(env_path)
load_dotenv(env_path)

# Thay đổi User-Agent để giả mạo trình duyệt thật
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")


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
driver.set_window_size(1920, 1080)


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

driver.get('https://study4.com/')


def click_button_login():
    try:
        # Đợi trang tải xong
        time.sleep(3)

        # Tìm nút đăng nhập bằng XPATH
        login_button = driver.find_element(By.XPATH,
                                           "//a[contains(@class, 'btn-primary') and contains(text(), 'Đăng nhập')]")

        # Cuộn tới phần tử nếu cần thiết
        driver.execute_script("arguments[0].scrollIntoView();", login_button)

        # Click vào nút đăng nhập
        login_button.click()

        print("Đã nhấp vào nút đăng nhập, đợi trang tải...")

        # Đợi trang mới xuất hiện sau khi đăng nhập
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        print("Trang mới đã tải xong!")

    except Exception as e:
        print("Lỗi khi nhấp vào nút đăng nhập hoặc tải trang mới:", e)

    # Giữ trình duyệt mở để kiểm tra (có thể bỏ dòng này nếu không cần)
    time.sleep(5)


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
        # print("Test content loaded.")
    except TimeoutException as e:
        print(f"Error during login: {e}")


def click_test_link():
    try:
        # Đợi phần tử xuất hiện
        tests_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'nav-link') and @href='/tests/']"))
        )

        # Click vào link Đề thi online
        tests_link.click()
        print("Đã nhấp vào link Đề thi online!")

        # Đợi phần tử xuất hiện
        toeic_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'nav-link') and @href='/tests/toeic/']"))
        )
        # Click vào link TOEIC
        toeic_link.click()
        print("Đã nhấp vào link TOEIC!")

    except Exception as e:
        print("Lỗi khi nhấp vào link Đề thi online:", e)


def get_test_links():
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


def click_solution_link():
    try:
        # Đợi phần tử xuất hiện
        solution_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'nav-link') and @href='#test-solutions']"))
        )

        # Thử nhấp vào link đáp án
        solution_link.click()
        print("Đã nhấp vào link Đáp án!")
        time.sleep(2)
        view_solutions_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href, '/solutions/') and contains(text(), 'Xem đáp án đề thi')]"))
        )
        view_solutions_link.click()
        print("Đã nhấp vào link Xem đáp án đề thi!")
        time.sleep(2)
    except Exception as e:
        print("Lỗi khi nhấp vào link Đáp án:", e)


def scrape_answers():
    data = []

    title_element = driver.find_element(By.TAG_NAME, 'h1')
    test_title = title_element.text.strip()  # Lấy nội dung tiêu đề
    # Loại bỏ "Thoát" nếu có
    test_title = re.sub(r'\s*Thoát$', '', test_title).strip()
    if test_title:  # Kiểm tra tiêu đề không rỗng
        title = {
            "Tiêu đề": test_title
        }
        data.append(title)
        print(f"Tiêu đề bài kiểm tra: {test_title}")
    else:
        print("Tiêu đề bài kiểm tra rỗng!")

    part_tabs = driver.find_elements(By.XPATH, "//a[contains(@class, 'nav-link') and contains(@id, 'pills-')]")

    for part_tab in part_tabs:
        part_name = part_tab.text.strip()
        part_id = part_tab.get_attribute("href").split("#")[-1]  # Lấy ID của nội dung Part
        print(part_id)
        print(f"📌 Đang xử lý: {part_name}")
        driver.execute_script("arguments[0].click();", part_tab)
        time.sleep(2)  # Đợi nội dung load
        # Click vào nút "Hiện Transcript"
        # try:
        #     transcript_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Hiện Transcript')]")
        #     driver.execute_script("arguments[0].click();", transcript_button)
        #     time.sleep(2)
        # except:
        #     print(f"❌ Không tìm thấy nút 'Hiện Transcript' cho {part_name}")

        # Lấy nội dung transcript
        # try:
        #     transcript_element = driver.find_element(By.XPATH,
        #                                              "//div[contains(@class, 'context-transcript')]//div[contains(@class, 'collapse show')]")
        #     transcript_text = transcript_element.text.strip()
        # except:
        #     transcript_text = "Không có transcript"

        # Lấy danh sách câu hỏi CHỈ của Part hiện tại
        questions = []
        try:
            part_container = driver.find_element(By.ID, part_id)  # Chỉ lấy nội dung trong Part này
            question_wrapper = part_container.find_element(By.CSS_SELECTOR, '.test-questions-wrapper')
            question_elements = question_wrapper.find_elements(By.CSS_SELECTOR, '.question-wrapper')
            print(f"📌 Số câu hỏi tìm thấy trong {part_name}: {len(question_elements)}")

            if question_elements:
                for question in question_elements:
                    try:
                        question_number = question.find_element(By.CSS_SELECTOR,
                                                                ".question-number").text.strip()
                        correct_answer = question.find_element(By.CSS_SELECTOR,
                                                               ".text-success").text.replace(
                            "Đáp án đúng:", "").strip()

                        # ✅ Chỉ thêm câu hỏi hợp lệ
                        if question_number and correct_answer:
                            questions.append({"question_number": question_number, "correct_answer": correct_answer})
                        else:
                            print(
                                f"⚠️ Bỏ qua câu hỏi bị thiếu dữ liệu trong {part_name} (Số: {question_number}, Đáp án: {correct_answer})")

                    except Exception as e:
                        print(f"⚠️ Lỗi khi xử lý câu hỏi trong {part_name}: {e}")
                        continue
            else:
                print(f"⚠️ Không tìm thấy câu hỏi trong {part_name}")
        except:
            print(f"⚠️ Không thể lấy danh sách câu hỏi cho {part_name}")

        # **Chỉ lưu nếu có câu hỏi hợp lệ**
        if questions:
            part_data = {
                "Part": part_name,
                "Question_set": len(question_elements),
                # "Transcript": transcript_text,
                "Danh sách câu hỏi": questions
            }
            data.append(part_data)

    # Lưu dữ liệu vào file
    file_path = f"answers/{test_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Dữ liệu đã được lưu vào {file_path}!")


def main():
    click_button_login()
    login_with_facebook()
    click_test_link()
    link = get_test_links()

    driver.get(link)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]'))
    )
    click_solution_link()
    scrape_answers()
    driver.quit()


if __name__ == "__main__":
    main()
