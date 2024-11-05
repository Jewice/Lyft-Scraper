import pwinput
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import os

LYFT_LOGIN_URL = "https://account.lyft.com/auth/email?v=lyft-for-business&next=https%3A%2F%2Fbusiness.lyft.com%2Flogin"
LYFT_EMAIL_INPUT_CSS = "//input[@name='email' and @id='email']"
OUTLOOK_EMAIL_INPUT_CSS = "//input[@name='loginfmt' and @id='i0116']"
OUTLOOK_PASSWORD_INPUT_CSS = "//input[@name='passwd' and @id='i0118']"
OUTLOOK_SUBMIT_BUTTON_CSS = "//input[@id='idSIButton9']"

# Automatically download and manage the correct version of ChromeDriver
service = ChromeService(ChromeDriverManager().install())


# Set up Selenium WebDriver using the managed driver
driver = webdriver.Chrome(service=service)

# Prompt the user to input their email address and password
email = input("Please enter your UCSD email address: ")
password = input("Please enter your password (hidden): ")

# Open Lyft Business Authentication Page
driver.get(LYFT_LOGIN_URL)

# Initialize webdriver with wait capability
wait = WebDriverWait(driver, 20)  # Wait up to 20 seconds

# Populate the email input field and submit
email_input = wait.until(EC.presence_of_element_located((By.XPATH, LYFT_EMAIL_INPUT_CSS)))
email_input.send_keys(email)
email_input.send_keys(Keys.RETURN)

# Open the login page
driver.get("https://mail.ucsd.edu")

# Wait for the page to redirect to Outlook (e.g., wait for the email input field to be visible)
email_input = wait.until(EC.presence_of_element_located((By.XPATH, OUTLOOK_EMAIL_INPUT_CSS)))
email_input.send_keys(email)
email_input.send_keys(Keys.RETURN)

password_input = wait.until(EC.presence_of_element_located((By.XPATH, OUTLOOK_PASSWORD_INPUT_CSS)))
password_input.send_keys(password)

sign_in_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
sign_in_button.click()

# Wait for Duo 2FA to appear and handle it manually
# Wait for an appropriate element that indicates the Duo screen has loaded (you can modify this to target specific elements)
"""wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='row text-title' and contains(text(), 'Stay signed in?')]")))

wait.until(EC.presence_of_element_located((By.ID, "trust-this-browser-label")))  # Wait for the device confirmation header
yes_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Yes, this is my device')]")
yes_button.click()"""

wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='row text-title' and contains(text(), 'Stay signed in?')]")))
# Click "Yes" button or continue, assuming default action is acceptable.
yes_button = driver.find_element(By.XPATH, "//input[@id='idSIButton9' and @type='submit']")
yes_button.click()

# Wait for the inbox to be loaded
wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Inbox')]")))
print("Logged in successfully and Inbox is accessible!")

# Find the newest email with the specified subject
latest_email_subject = "Here's your one-time Lyft Business log-in link"
email = wait.until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), \"{latest_email_subject}\")]")))

# Click the latest email
email.click()
print("Opened the email with the subject:", latest_email_subject)

# Wait for the email body to load
wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Securely log into Lyft')]")))

# Find the link in the email body
link_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@style, 'text-decoration:none') and contains(text(), 'Log in')]")))
login_link = link_element.get_attribute('href')

print("Found the login link:", login_link)

driver.get(login_link)

# Wait for the "All rides" tab to become clickable and then click it
tab_all_rides = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='tab-all']")))

# Click the "All rides" tab
tab_all_rides.click()

# Optional: print confirmation after clicking
print("Clicked the 'All rides' tab")

# Get the ride details

# Define the current month and year for filtering
current_month = datetime.now().month
current_year = datetime.now().year

# Create a directory to save screenshots if it doesn’t exist
output_directory = os.path.join(os.getcwd(), f"ride_screenshots_{current_month}_{current_year}")
os.makedirs(output_directory, exist_ok=True)

# Initialize a counter for unique naming of screenshots
screenshot_counter = 1
screenshots = []

# Locate the main ride list container
ride_list_container = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "ride-list"))
)

while True:
    # Locate all ride items within the list
    ride_elements = ride_list_container.find_elements(By.CSS_SELECTOR, "[data-e2e='ride-list-item']")
    print(f"Found {len(ride_elements)} rides in the list")
    new_screenshot_taken = False

    for ride in ride_elements:
        try:
            # Ensure the ride element is clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(ride))
            
            # Click on each ride to open the detailed view
            ride.click()
            time.sleep(1)  # Wait for the detailed view to load
            
            # Wait until the ride detail view is visible
            ride_detail_view = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "ride-card-full-info"))
            )
            # Get the date element and check if it’s in the current month
            date_element = ride.find_element(By.CSS_SELECTOR, "h2[data-testid='ride-card-summary-title']")
            date_text = date_element.text
            
            # Parse the date text to extract the ride date (format: MM/DD)
            ride_date = datetime.strptime(date_text.split(" on ")[-1], '%m/%d')
            ride_date = ride_date.replace(year=current_year)

            if ride_date.month != current_month:
                # If not from the current month, skip this ride
                close_button = ride_detail_view.find_element(By.CSS_SELECTOR, "button.close-button-class")
                close_button.click()
                time.sleep(0.5)  # Short wait for closing animation
                continue

            # Format the ride's timestamp (month_day_hour_minute)
            timestamp = ride_date.strftime("%Y_%m_%d_%H_%M")

            # Create a dynamic file name based on the ride's date and time
            screenshot_name = os.path.join(output_directory, f"ride_screenshot_{timestamp}.png")

            try:
                # Take a screenshot and save it
                driver.save_screenshot(screenshot_name)
                screenshots.append(screenshot_name)
                print(f"Screenshot taken for current month ride: {screenshot_name}")
            except Exception as e:
                print(f"Error taking screenshot: {e}")  

            # Increase the counter for unique screenshot names
            screenshot_counter += 1
            new_screenshot_taken = True

            # Close the ride details
            close_button = ride_detail_view.find_element(By.CSS_SELECTOR, "button.close-button-class")
            close_button.click()
            time.sleep(0.5)  # Short wait for closing animation

        except Exception as e:
            print(f"Error processing ride: {e}")
            continue

    # Scroll down to load more rides if new screenshots were taken
    if new_screenshot_taken:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", ride_list_container)
        time.sleep(2)  # Adjust sleep time as needed
    else:
        break  # Exit loop if no new screenshots were taken

# Final message for exported screenshots
print(f"All screenshots saved in the directory '{output_directory}'.")

