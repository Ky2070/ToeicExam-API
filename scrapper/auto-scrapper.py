# import json
# import os
# import time  # Import thư viện time để sử dụng time.sleep
#
# from dotenv import load_dotenv
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
#
# base_path = r'C:\Users\nguye\PycharmProjects\EnglishTest\scrapper\chromedriver-win64'
# chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
#
# # Tạo service và driver
# service = Service(executable_path=chromedriver_path)
# driver = webdriver.Chrome(service=service)
#
# # Mở trang web
# driver.get('https://study4.com/tests/toeic/')
# print(driver.title)
#
# # Thêm vòng lặp while True để tiếp tục quét liên tục
# while True:
#     try:
#         # Tìm tất cả các thẻ div chứa bài thi
#         test_items = driver.find_elements(By.CLASS_NAME, 'testitem-wrapper')
#
#         # Lặp qua các phần tử và xử lý từng bài thi
#         for index, test_item in enumerate(test_items, start=1):
#             a_tag = test_item.find_element(By.TAG_NAME, 'a')
#             link = a_tag.get_attribute('href')
#             print(f"{index}. {link}")
#
#             # Chuyển đến trang chi tiết bài thi
#             driver.get(link)
#
#             # Đợi trang tải hoàn tất
#             try:
#                 WebDriverWait(driver, 15).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]'))
#                 )
#             except TimeoutException:
#                 print(f"Lỗi: Không tìm thấy checkbox trên trang {link}. Bỏ qua.")
#                 continue
#
#             # Chọn checkbox
#             checkboxes_selected = 0
#             max_scroll_attempts = 10
#             for scroll_attempt in range(max_scroll_attempts):
#                 # Cập nhật danh sách checkbox hiện tại
#                 checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input.form-check-input[type="checkbox"]')
#                 for checkbox in checkboxes:
#                     if not checkbox.is_selected() and checkbox.is_displayed():
#                         try:
#                             # Cuộn đến checkbox và chọn
#                             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
#                                                   checkbox)
#                             WebDriverWait(driver, 10).until(EC.element_to_be_clickable(checkbox))
#                             checkbox.click()
#                             checkboxes_selected += 1
#                             print(f"Checkbox đã chọn: {checkboxes_selected}")
#                             if checkboxes_selected >= 7:
#                                 break
#                         except (TimeoutException, ElementClickInterceptedException) as e:
#                             print(f"Lỗi khi tích checkbox: {e}. Bỏ qua checkbox này.")
#
#                 if checkboxes_selected >= 7:
#                     print("Đã chọn đủ 7 checkbox. Tiếp tục cuộn để tìm nút Submit.")
#                 else:
#                     # Cuộn thêm
#                     driver.execute_script("window.scrollBy(0, window.innerHeight / 0.01);")
#                     WebDriverWait(driver, 15).until(
#                         lambda d: d.execute_script("return document.readyState") == "complete"
#                     )
#
#             if checkboxes_selected < 7:
#                 print("Không thể chọn đủ 7 checkbox. Bỏ qua bài thi này.")
#                 continue
#
#             # Cuộn đến nút Submit và gửi form luyện tập
#             submit_button_found = False
#             for _ in range(10):  # Thử cuộn tối đa 10 lần
#                 try:
#                     # Tìm lại nút Submit sau mỗi lần cuộn
#                     submit_button = WebDriverWait(driver, 15).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-primary[type="submit"]'))
#                     )
#                     driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
#                                           submit_button)
#                     submit_button.click()
#                     print("Nút 'Luyện tập' đã được bấm thành công!")
#                     submit_button_found = True
#                     break
#                 except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
#                     print(f"Lỗi khi bấm nút 'Luyện tập': {e}. Cuộn thêm.")
#                     driver.execute_script("window.scrollBy(0, window.innerHeight / 0.01);")
#
#             if not submit_button_found:
#                 print("Không thể bấm nút 'Luyện tập'. Bỏ qua bài thi này.")
#                 continue
#
#             # Đợi trang đăng nhập tải
#             try:
#                 WebDriverWait(driver, 15).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-12.f-login-block'))
#                 )
#                 print("Trang đăng nhập đã tải xong.")
#
#                 # Tìm và bấm nút 'Đăng nhập với Facebook'
#                 facebook_button = WebDriverWait(driver, 15).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.s-button.f-login-button'))
#                 )
#                 facebook_button.click()
#                 print("Đã bấm nút 'Đăng nhập với Facebook'.")
#
#                 # Đợi trang Facebook tải và điền thông tin đăng nhập
#                 WebDriverWait(driver, 15).until(
#                     EC.presence_of_element_located((By.ID, 'email'))
#                 )
#
#                 # Điền username và password
#                 username_field = driver.find_element(By.ID, 'email')
#                 password_field = driver.find_element(By.ID, 'pass')
#
#                 # Tải các biến môi trường từ file .env
#                 load_dotenv('C:/Users/nguye/PycharmProjects/EnglishTest/scrapper/.env')
#
#                 # Đọc thông tin đăng nhập từ biến môi trường
#                 username = os.getenv('GMAIL')
#                 password = os.getenv('PASSWORD')
#
#                 # Sử dụng các giá trị đã đọc để nhập vào các trường username và password
#                 username_field.send_keys(username)
#                 password_field.send_keys(password)
#
#                 # Bấm nút đăng nhập
#                 login_button = driver.find_element(By.ID, 'loginbutton')
#                 login_button.click()
#                 print("Đã bấm nút 'Đăng nhập'.")
#
#                 # Sau khi đăng nhập thành công, bấm vào nút "Tiếp tục dưới tên Quốc Kỳ"
#                 try:
#                     # Đợi nút "Tiếp tục dưới tên Quốc Kỳ" có thể click được
#                     continue_button = WebDriverWait(driver, 15).until(
#                         EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Tiếp tục dưới tên Quốc Kỳ')]"))
#                     )
#                     continue_button.click()
#                     print("Đã bấm nút 'Tiếp tục dưới tên Quốc Kỳ'.")
#
#                     # Đợi trang bài thi tải hoàn tất bằng cách kiểm tra một phần tử xác định có sẵn trên trang bài thi
#                     WebDriverWait(driver, 20).until(
#                         EC.presence_of_element_located((By.ID, 'test-content'))
#                     )
#                     print("Trang bài thi đã được tải xong.")
#                 except TimeoutException:
#                     print("Lỗi: Không tìm thấy nút 'Tiếp tục dưới tên Quốc Kỳ' hoặc trang bài thi không tải kịp.")
#
#             except TimeoutException:
#                 print("Lỗi: Không tìm thấy trang đăng nhập Facebook hoặc các phần tử cần thiết. Bỏ qua.")
#                 continue
#
#         # Thêm thời gian ngủ giữa các lần quét (nếu cần thiết)
#         time.sleep(30)  # Chờ 5 giây trước khi tiếp tục lặp lại
#     except Exception as e:
#         print(f"Lỗi trong quá trình xử lý: {e}. Tiếp tục...")
#         time.sleep(10)  # Chờ thêm 10 giây nếu gặp lỗi, rồi tiếp tục
