from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from rich import print

# load environment variables from .env.
# make sure you have copied the .env_example file to .env
# the project's base directory and updated the values as appropriate
config = dotenv_values(".env")


def run():

    # if you wish to use Chrome instead of Firefox, change this to the Chrome line
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # driver = webdriver.Firefox()

    # open a browser window and go to the foreup website
    driver.get(config["FOREUP_SOFTWARE_URL"])
    
    print("Waiting for page to load...")
    import time
    time.sleep(3)
    
    print(f"Current page title: {driver.title}")
    print(f"Current URL: {driver.current_url}")
    
    try:
        # click on the Annual Member booking class button
        print("Looking for Annual Member booking class button...")
        booking_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div/button[4]")
        print("Found booking button, clicking it...")
        booking_button.click()
        time.sleep(2)
    except Exception as e:
        print(f"Could not find booking button: {e}")
        print("Trying to find alternative booking class buttons...")
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(buttons)} buttons on the page")
            for i, btn in enumerate(buttons[:10]):  # Show first 10 buttons
                print(f"Button {i}: text='{btn.text}', visible={btn.is_displayed()}")
        except Exception as e2:
            print(f"Error finding buttons: {e2}")
    
    try:
        # click on the login button
        print("Looking for login button...")
        login_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div/div/p[1]/button")
        print("Found login button, clicking it...")
        login_button.click()
        time.sleep(2)
    except Exception as e:
        print(f"Could not find login button: {e}")
        print("Keeping browser open for 60 seconds for inspection...")
        time.sleep(60)
        driver.close()
        return

    # fill out the email input field
    driver.find_element(By.XPATH, '//*[@id="login_email"]').send_keys(config["FOREUP_USERNAME"])
    driver.find_element(By.XPATH, '//*[@id="login_password"]').send_keys(config["FOREUP_PASSWORD"])

    # click the form log in button
    driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div[3]/div/button[1]').click()

    '''
        you will now be logged into the website, and be presented with the booking date selection
        and time select page.
    '''

    # find the last non-disabled date on the calendar and click on it to show the tee times
    # for that day

    # wait for the page to load the calendar before continuing
    print("Waiting for the calendar datepicker-switch element to be clickable (page to load calendar)")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".datepicker-switch"))
    )
    print("Calendar is there, find the calendar days which are not disabled")
    calendar_day_list = driver.find_elements(By.CSS_SELECTOR, ".day:not(.disabled)")

    print(f"Number of days available to reserve: {len(calendar_day_list)}")

    # the last non-disabled calendar day is the one we want to click on, so let's do it!
    last_available_day = calendar_day_list[-1]
    print(f"Last available day to reserve is: {last_available_day.text}, clicking it to bring up that date's tee times")
    last_available_day.click()

    # click on the # of players == 3 button to indicate we want 3
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.hidden-xs:nth-child(2) > a:nth-child(2)')))
    driver.find_element(By.CSS_SELECTOR, 'div.hidden-xs:nth-child(2) > a:nth-child(2)').click()

    # wait for the available tee times to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "times"))
    )

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'li.time-legacy'))
    )

    # now find the first element in the tee times, it's the one we want to click to reserve the tee time!
    # it's the first LI element in the <ul> on the page
    first_tee_time = driver.find_element(By.CSS_SELECTOR, 'li.time-legacy:nth-child(1)')

    # get the text of the tee time and print it out to the console
    tee_time_info = first_tee_time.text.split("\n")

    print("\nFirst Tee Time Of Day Is:")
    print(
        f"Tee Time: {tee_time_info[0]} for {tee_time_info[1]} holes "
        f"with a max of {tee_time_info[2]} players "
        f"and the cost is: {tee_time_info[3]}\n\n"

    )


    # TODO:
    # when you are certain you want to continue, uncomment this line which will cick on the 1st available tee time
    # first_tee_time.click()

    # re-add this after you see the reservation working so it closes the browser window automatically
    # or leave it commented out and manually close the selenium web window
    # driver.close()


if __name__ == "__main__":
    run()