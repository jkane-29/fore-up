from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

config = dotenv_values(".env")

def debug_page():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        driver.get(config["FOREUP_SOFTWARE_URL"])
        print(f"\n{'='*60}")
        print(f"URL: {driver.current_url}")
        print(f"Title: {driver.title}")
        print(f"{'='*60}\n")
        
        time.sleep(3)
        
        # Take a screenshot
        driver.save_screenshot("page_screenshot.png")
        print("✓ Screenshot saved to page_screenshot.png\n")
        
        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons:\n")
        for i, btn in enumerate(buttons):
            if btn.is_displayed():
                text = btn.text.strip().replace('\n', ' | ')
                classes = btn.get_attribute('class')
                print(f"  Button #{i}: '{text}' [class: {classes}]")
        
        # Find all links
        links = driver.find_elements(By.TAG_NAME, "a")
        visible_links = [l for l in links if l.is_displayed() and l.text.strip()]
        print(f"\nFound {len(visible_links)} visible links:\n")
        for i, link in enumerate(visible_links[:15]):  # Show first 15
            text = link.text.strip().replace('\n', ' | ')
            print(f"  Link #{i}: '{text}'")
        
        # Look for login-related elements
        print("\nSearching for login-related elements...")
        try:
            login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Login') or contains(text(), 'login') or contains(text(), 'Sign In') or contains(text(), 'sign in')]")
            print(f"Found {len(login_elements)} login-related elements:")
            for elem in login_elements[:5]:
                print(f"  - {elem.tag_name}: '{elem.text}' [class: {elem.get_attribute('class')}]")
        except Exception as e:
            print(f"Error finding login elements: {e}")
        
        print("\n\nBrowser will stay open for 30 seconds for manual inspection...")
        print("Check the browser window to see the actual page!")
        time.sleep(30)
        
    finally:
        driver.quit()
        print("\nBrowser closed.")

if __name__ == "__main__":
    debug_page()

