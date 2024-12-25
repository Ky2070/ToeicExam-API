import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Định nghĩa đường dẫn gốc
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
    for index, test_item in enumerate(test_items, start=1):
        # Tìm thẻ <a> và lấy link
        a_tag = test_item.find_element(By.TAG_NAME, 'a')
        link = a_tag.get_attribute('href')
        print(f"{index}. {link}")

        # Chuyển đến trang chi tiết bài thi
        driver.get(link)

        # Đợi trang tải hoàn tất
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]'))
            )
        except TimeoutException:
            print(f"Lỗi: Không tìm thấy checkbox trên trang {link}. Bỏ qua.")
            continue

        # Tìm tất cả checkbox
        checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]')

        # Cuộn trang để tải nội dung
        last_height = driver.execute_script("return document.body.scrollHeight")
        timeout_count = 0

        while True:
            position = last_height // 5
            driver.execute_script(f"window.scrollTo(0, {position});")

            try:
                WebDriverWait(driver, 10).until(
                    lambda driver: driver.execute_script("return document.body.scrollHeight") > last_height
                )
            except TimeoutException:
                timeout_count += 1
                print(f"Lỗi cuộn trang: Không tải thêm nội dung sau {timeout_count} lần.")
                if timeout_count > 2:  # Thoát nếu thử quá 2 lần
                    break

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Tích chọn các checkbox
        for checkbox in checkboxes:
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(checkbox))
                checkbox.click()
            except TimeoutException:
                print("Lỗi: Không thể tích chọn checkbox. Bỏ qua checkbox này.")

        # Gửi form luyện tập
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary[type="submit"]')
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(submit_button))
            submit_button.click()

            # Đợi trang luyện tập tải xong
            WebDriverWait(driver, 10).until(EC.title_contains("Luyện tập"))
            print(f"Đang ở trang luyện tập: {driver.title}")
        except TimeoutException:
            print(f"Lỗi: Không thể gửi form trên trang {link}. Bỏ qua.")
            continue

        # Quay lại trang chính
        driver.back()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'testitem-wrapper')))

except Exception as e:
    print(f"Đã xảy ra lỗi không mong muốn: {e}")
finally:
    # Đóng driver
    driver.close()
