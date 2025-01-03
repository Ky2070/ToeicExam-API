import os
import logging
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load environment variables
load_dotenv('C:/Users/nguye/PycharmProjects/EnglishTest/scrapper/.env')

# Retrieve email and password from .env
email = os.getenv('NAME')
password = os.getenv('PASS')

if not email or not password:
    logging.error("Email or password is missing in the environment variables.")
    raise ValueError("Email or password is missing in the environment variables.")

# Setup paths for Chromedriver
base_path = r'C:\Users\nguye\PycharmProjects\EnglishTest\scrapper\chromedriver-win64'
chromedriver_path = os.path.join(base_path, 'chromedriver.exe')

# Initialize WebDriver
try:
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # Maximize the browser window
    driver.maximize_window()
    logging.info("WebDriver initialized and window maximized.")
except WebDriverException as e:
    logging.error(f"Failed to initialize WebDriver: {e}")
    raise

try:
    # Navigate to the target URL
    target_url = "https://englishapp-client.vercel.app/"
    driver.get(target_url)
    logging.info(f"Navigated to URL: {target_url}")

    # Wait until the "Thư Viện Đề Thi" button is clickable
    wait = WebDriverWait(driver, 35)
    try:
        test_library_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Thư Viện Đề Thi')]")
        ))
        logging.info("'Thư Viện Đề Thi' button is clickable.")
        test_library_button.click()
        logging.info("Clicked 'Thư Viện Đề Thi' button.")

        # Validate the URL
        if "/tests" not in driver.current_url:
            logging.error("Failed to navigate to the 'Thư Viện Đề Thi' page.")
            raise AssertionError("Navigation error")
        logging.info("Successfully navigated to the 'Thư Viện Đề Thi' page.")
    except TimeoutException:
        logging.error("Timeout: 'Thư Viện Đề Thi' button not found.")
        raise

    # Wait for "Làm bài" button
    try:
        exam_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='/tests/1']/button[contains(text(),'Làm bài')]")
        ))
        logging.info("'Làm bài' button is clickable.")
        exam_button.click()
        logging.info("Clicked 'Làm bài' button.")
    except TimeoutException:
        logging.warning("'Làm bài' button not found, checking for login link.")

        # Check for login requirement
    try:
        login_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(),'Đăng nhập') and @href='/login']")  # Ensure XPath is correct
        ))
        logging.info("Login link is visible and clickable. Redirecting to login page.")
        login_link.click()

        # Wait for login page to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "space-y-4")))  # Wait until the login form is loaded

        # Find and input email
        email_input = driver.find_element(By.NAME, "email")  # Use the correct attribute
        email_input.clear()
        email_input.send_keys(email)
        logging.info("Entered email.")

        # Find and input password
        password_input = driver.find_element(By.NAME, "password")  # Use the correct attribute
        password_input.clear()
        password_input.send_keys(password)
        logging.info("Entered password.")

        # Find and click the login button
        login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Đăng nhập')]")  # Ensure XPath is correct
        login_button.click()
        logging.info("Clicked the login button.")

        # Wait for successful login by checking for a unique element on the page
        wait.until(EC.url_contains('https://englishapp-client.vercel.app/'))  # Ensure that we are redirected to the test page
        logging.info("Successfully logged in.")

        # After logging in, navigate to "Thư Viện Đề Thi" again
        # Navigate to the target URL
        # Wait for the "Thư Viện Đề Thi" button to become clickable again
        test_library_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Thư Viện Đề Thi')]")
        ))
        logging.info("'Thư Viện Đề Thi' button is clickable.")
        test_library_button.click()
        logging.info("Clicked 'Thư Viện Đề Thi' button.")

        # Wait for "Làm bài" button to be clickable again
        exam_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='/tests/1']/button[contains(text(),'Làm bài')]")
        ))
        exam_button.click()
        logging.info("Clicked 'Làm bài' button after login.")
    except TimeoutException:
        logging.error("Login link or form not found.")
        raise
    try:
        # Wait for the test detail page to load
        logging.info("Waiting for the test detail page to load...")
        WebDriverWait(driver, 60).until(  # Increased wait time to 60 seconds
            EC.presence_of_element_located((By.CLASS_NAME, "px-2"))
        )
        logging.info("Test detail page loaded successfully.")

        # Add a sleep time to keep the browser open for a while after loading the page
        time.sleep(30)  # Keeps the browser open for 30 seconds to check the page

    except TimeoutException:
        logging.error("Test detail page did not load within the timeout period.")
        raise

except (TimeoutException, NoSuchElementException, AssertionError) as e:
    logging.error(f"Test failed: {e}")
finally:
    driver.quit()
    logging.info("Browser closed.")
