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

def debug_with_filters():
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
        
        # Click on FIRST available day 
        calendar_days = driver.find_elements(By.CSS_SELECTOR, ".day:not(.disabled)")
        if calendar_days:
            first_day = calendar_days[0]  # Use first day, not last
            print(f"[blue]Clicking on FIRST available day: {first_day.text}[/blue]")
            first_day.click()
            time.sleep(2)
            
            # Wait for filters
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "times")))
            
            # Select 2 players
            print("[blue]Selecting 2 players...[/blue]")
            player_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'hidden-xs')]//a")
            for btn in player_buttons:
                if btn.text.strip() == "2":
                    btn.click()
                    time.sleep(1)
                    print("[green]✓ Clicked 2 players[/green]")
                    break
            
            # Select All time
            print("[blue]Selecting 'All' time...[/blue]")
            time_buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in time_buttons:
                if btn.text.strip() == "All" and btn.is_displayed():
                    btn.click()
                    time.sleep(1)
                    print("[green]✓ Clicked All time[/green]")
                    break
            
            # Select 18 holes
            print("[blue]Selecting 18 holes...[/blue]")
            hole_buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in hole_buttons:
                text = btn.text.strip()
                if text == "18" and btn.is_displayed():
                    btn.click()
                    time.sleep(3)  # Wait longer for tee times to load
                    print("[green]✓ Clicked 18 holes[/green]")
                    break
            
            # Take screenshot after all filters
            driver.save_screenshot("after_filters.png")
            print("[green]✓ Screenshot saved to after_filters.png[/green]")
            
            # Check for tee times
            print("\n[yellow]Checking for tee times...[/yellow]")
            time.sleep(2)
            
            # Get the #times element content
            times_div = driver.find_element(By.ID, "times")
            print(f"Times div text: {times_div.text[:200]}")
            
            # Try multiple selectors
            selectors_to_try = [
                "li.time-legacy",
                "li.time",
                "#times li",
                "#times ul li",
                ".time-available",
                "[data-time]"
            ]
            
            for selector in selectors_to_try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  Selector '{selector}': found {len(elements)} elements")
                if elements:
                    for i, elem in enumerate(elements[:3]):
                        print(f"    [{i}]: {elem.text[:80]}")
            
            print("\n[blue]Browser staying open for 60 seconds - check it manually![/blue]")
            time.sleep(60)
        
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        time.sleep(30)
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_with_filters()

