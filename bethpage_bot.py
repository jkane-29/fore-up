from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

from rich import print

# load environment variables from .env
config = dotenv_values(".env")

# Configure which booking class to use (change this to match your needs)
# Options: "Resident", "Verified NYS Resident - Bethpage/Sunken Meadow", "Non Resident",
#          "Verified Access/Liberty Pass", "Verified Junior Resident", "Verified Senior Resident"
BOOKING_CLASS = config.get("BOOKING_CLASS", "Resident")


def run():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # Open the ForeUp website
        print(f"[blue]Opening {config['FOREUP_SOFTWARE_URL']}[/blue]")
        driver.get(config["FOREUP_SOFTWARE_URL"])
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "button"))
        )
        
        print(f"[green]✓ Page loaded: {driver.title}[/green]")
        time.sleep(2)
        
        # Find and click the booking class button
        print(f"[blue]Looking for '{BOOKING_CLASS}' booking button...[/blue]")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        
        booking_button = None
        for btn in buttons:
            if btn.text.strip() == BOOKING_CLASS:
                booking_button = btn
                break
        
        if not booking_button:
            print(f"[red]✗ Could not find booking button for '{BOOKING_CLASS}'[/red]")
            print("\n[yellow]Available booking options:[/yellow]")
            for i, btn in enumerate(buttons):
                if btn.is_displayed() and btn.text.strip():
                    print(f"  {i+1}. {btn.text.strip()}")
            print("\n[yellow]Please update BOOKING_CLASS in .env file[/yellow]")
            time.sleep(10)
            return
        
        print(f"[green]✓ Found '{BOOKING_CLASS}' button, clicking...[/green]")
        booking_button.click()
        time.sleep(2)
        
        # Now we should see the login section or booking interface
        print("[blue]Looking for login section...[/blue]")
        
        # Check if we need to log in
        try:
            # Look for login button or link
            login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Login') or contains(text(), 'login') or contains(text(), 'Sign In')]")
            
            if login_elements:
                print(f"[green]✓ Found {len(login_elements)} login elements[/green]")
                for elem in login_elements:
                    if elem.is_displayed() and elem.tag_name in ['button', 'a']:
                        print(f"[blue]Clicking login element: {elem.text}[/blue]")
                        elem.click()
                        time.sleep(2)
                        break
            
            # Wait for login form
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "login_email"))
            )
            
            print("[blue]Filling in login credentials...[/blue]")
            driver.find_element(By.ID, "login_email").send_keys(config["FOREUP_USERNAME"])
            driver.find_element(By.ID, "login_password").send_keys(config["FOREUP_PASSWORD"])
            
            # Click login button
            login_submit = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Log In')]")
            print("[blue]Submitting login...[/blue]")
            login_submit.click()
            
            time.sleep(3)
            print("[green]✓ Login submitted[/green]")
            
        except Exception as e:
            print(f"[yellow]Note: {e}[/yellow]")
            print("[blue]Checking if we're already on the booking page...[/blue]")
        
        # Wait for the calendar to load
        print("[blue]Waiting for calendar to load...[/blue]")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".datepicker-switch, .day"))
        )
        print("[green]✓ Calendar loaded[/green]")
        
        # Find available dates
        calendar_days = driver.find_elements(By.CSS_SELECTOR, ".day:not(.disabled)")
        print(f"[green]✓ Found {len(calendar_days)} available days[/green]")
        
        if calendar_days:
            last_day = calendar_days[-1]
            print(f"[blue]Clicking on last available day: {last_day.text}[/blue]")
            last_day.click()
            time.sleep(2)
            
            # Wait for filters to appear
            print("[blue]Waiting for booking filters...[/blue]")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "times"))
            )
            
            # Select number of players (default to 4)
            try:
                print("[blue]Selecting 4 players...[/blue]")
                player_buttons = driver.find_elements(By.XPATH, "//div[preceding-sibling::div[contains(text(), 'Players')]]//a | //div[contains(@class, 'hidden-xs')]//a")
                for btn in player_buttons:
                    if btn.text.strip() == "4":
                        btn.click()
                        time.sleep(1)
                        break
                print("[green]✓ Selected 4 players[/green]")
            except Exception as e:
                print(f"[yellow]Could not select players: {e}[/yellow]")
            
            # Select time of day (default to All)
            try:
                print("[blue]Selecting 'All' time of day...[/blue]")
                time_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'All') or contains(text(), 'Morning') or contains(text(), 'Midday')]")
                for btn in time_buttons:
                    if btn.text.strip() == "All":
                        btn.click()
                        time.sleep(1)
                        break
                print("[green]✓ Selected 'All' time of day[/green]")
            except Exception as e:
                print(f"[yellow]Could not select time: {e}[/yellow]")
            
            # Select holes (default to 18)
            try:
                print("[blue]Selecting 18 holes...[/blue]")
                hole_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '18') or contains(text(), '9') or contains(text(), 'Both')]")
                for btn in hole_buttons:
                    if btn.text.strip() == "18":
                        btn.click()
                        time.sleep(2)
                        break
                print("[green]✓ Selected 18 holes[/green]")
            except Exception as e:
                print(f"[yellow]Could not select holes: {e}[/yellow]")
            
            # Now wait for tee times to load
            print("[blue]Waiting for tee times to load...[/blue]")
            time.sleep(3)
            
            # Find first available tee time
            tee_times = driver.find_elements(By.CSS_SELECTOR, "li.time-legacy, li.time, ul#times li")
            if tee_times:
                first_tee = tee_times[0]
                tee_info = first_tee.text.split("\n")
                print(f"\n[green]{'='*60}[/green]")
                print(f"[green bold]First Available Tee Time:[/green bold]")
                for info in tee_info:
                    print(f"  {info}")
                print(f"[green]{'='*60}[/green]\n")
                
                # NOTE: Uncomment the line below to actually book the tee time
                # first_tee.click()
                print("[yellow]To book this tee time, uncomment the 'first_tee.click()' line[/yellow]")
            else:
                print("[red]✗ No tee times found[/red]")
        else:
            print("[red]✗ No available days found[/red]")
        
        # Keep browser open for inspection
        print("\n[blue]Browser will stay open for 30 seconds...[/blue]")
        time.sleep(30)
        
    except Exception as e:
        print(f"[red]✗ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        time.sleep(30)
    
    finally:
        driver.quit()
        print("[green]✓ Browser closed[/green]")


if __name__ == "__main__":
    run()

