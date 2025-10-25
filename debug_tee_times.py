from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

from rich import print

config = dotenv_values(".env")
BOOKING_CLASS = config.get("BOOKING_CLASS", "Resident")

def debug_tee_times():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        print(f"[blue]Opening {config['FOREUP_SOFTWARE_URL']}[/blue]")
        driver.get(config["FOREUP_SOFTWARE_URL"])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
        time.sleep(2)
        
        # Click booking class
        print(f"[blue]Clicking '{BOOKING_CLASS}' button...[/blue]")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if btn.text.strip() == BOOKING_CLASS:
                btn.click()
                break
        time.sleep(2)
        
        # Login
        print("[blue]Logging in...[/blue]")
        try:
            login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Login') or contains(text(), 'login')]")
            for elem in login_elements:
                if elem.is_displayed() and elem.tag_name in ['button', 'a']:
                    elem.click()
                    time.sleep(2)
                    break
            
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "login_email")))
            driver.find_element(By.ID, "login_email").send_keys(config["FOREUP_USERNAME"])
            driver.find_element(By.ID, "login_password").send_keys(config["FOREUP_PASSWORD"])
            login_submit = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Log In')]")
            login_submit.click()
            time.sleep(3)
        except:
            pass
        
        # Wait for calendar
        print("[blue]Waiting for calendar...[/blue]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".day")))
        
        # Click on first available day (not last)
        calendar_days = driver.find_elements(By.CSS_SELECTOR, ".day:not(.disabled)")
        if calendar_days:
            first_day = calendar_days[0]
            print(f"[blue]Clicking on first available day: {first_day.text}[/blue]")
            first_day.click()
            time.sleep(3)
            
            # Take screenshot
            driver.save_screenshot("after_date_click.png")
            print("[green]✓ Screenshot saved to after_date_click.png[/green]")
            
            # Check page source for tee times container
            print("\n[yellow]Looking for tee times elements...[/yellow]")
            
            # Try different selectors
            selectors = [
                ("li.time-legacy", "CSS: li.time-legacy"),
                ("#times", "ID: times"),
                (".time", "CSS: .time"),
                ("li[class*='time']", "CSS: li with 'time' in class"),
                ("ul li", "CSS: ul li (all list items)")
            ]
            
            for selector, desc in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"  {desc}: Found {len(elements)} elements")
                    if elements and len(elements) <= 10:
                        for i, elem in enumerate(elements[:5]):
                            text = elem.text.strip()[:50]
                            print(f"    [{i}]: {text}")
                except Exception as e:
                    print(f"  {desc}: Error - {e}")
            
            # Check if there's a message about no times
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if "no times" in page_text.lower() or "no tee times" in page_text.lower():
                print("\n[red]Page shows 'No times available' message[/red]")
            
            print("\n[blue]Keeping browser open for 60 seconds for inspection...[/blue]")
            print("[yellow]Check the browser window to see what's displayed![/yellow]")
            time.sleep(60)
        
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        time.sleep(30)
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_tee_times()

