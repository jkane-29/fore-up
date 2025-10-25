"""
Bethpage Tee Time Bot - Scheduler
Runs at 7:00 AM EST to book tee times exactly 7 days in advance
"""

from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timedelta
import pytz

from rich import print

config = dotenv_values(".env")
BOOKING_CLASS = config.get("BOOKING_CLASS", "Resident")

# Configuration
NUM_PLAYERS = int(config.get("NUM_PLAYERS", "2"))  # How many players
TIME_OF_DAY = config.get("TIME_OF_DAY", "Morning")  # Morning, Midday, Evening, or All
NUM_HOLES = config.get("NUM_HOLES", "18")  # 9 or 18
AUTO_BOOK = config.get("AUTO_BOOK", "false").lower() == "true"  # Set to true to automatically book


def get_target_date():
    """Calculate the date 7 days from now (the newly released date)"""
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    target_date = now + timedelta(days=7)
    return target_date.strftime("%d")  # Return day of month


def book_tee_time():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        start_time = time.time()
        print(f"\n[bold blue]{'='*70}[/bold blue]")
        print(f"[bold]Bethpage Tee Time Bot - Starting at {datetime.now().strftime('%I:%M:%S %p')}[/bold]")
        print(f"[bold blue]{'='*70}[/bold blue]\n")
        
        # Open the ForeUp website
        print(f"[blue]→ Opening booking page...[/blue]")
        driver.get(config["FOREUP_SOFTWARE_URL"])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "button")))
        print(f"[green]✓ Page loaded[/green]")
        time.sleep(1)
        
        # Click booking class button
        print(f"[blue]→ Selecting '{BOOKING_CLASS}' booking class...[/blue]")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if btn.text.strip() == BOOKING_CLASS:
                btn.click()
                break
        time.sleep(1)
        print(f"[green]✓ Booking class selected[/green]")
        
        # Login
        print(f"[blue]→ Logging in...[/blue]")
        try:
            login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Login') or contains(text(), 'login')]")
            for elem in login_elements:
                if elem.is_displayed() and elem.tag_name in ['button', 'a']:
                    elem.click()
                    time.sleep(1)
                    break
            
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "login_email")))
            driver.find_element(By.ID, "login_email").send_keys(config["FOREUP_USERNAME"])
            driver.find_element(By.ID, "login_password").send_keys(config["FOREUP_PASSWORD"])
            login_submit = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Log In')]")
            login_submit.click()
            time.sleep(2)
            print(f"[green]✓ Logged in successfully[/green]")
        except Exception as e:
            print(f"[yellow]! Login may have failed or already logged in: {e}[/yellow]")
        
        # Wait for calendar
        print(f"[blue]→ Loading calendar...[/blue]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".day")))
        print(f"[green]✓ Calendar loaded[/green]")
        
        # Find and click the target date (7 days out)
        target_day = get_target_date()
        print(f"[blue]→ Looking for date: {target_day} (7 days from today)...[/blue]")
        
        calendar_days = driver.find_elements(By.CSS_SELECTOR, ".day:not(.disabled)")
        clicked = False
        for day in calendar_days:
            if day.text.strip() == target_day:
                print(f"[green]✓ Found target date: {target_day}, clicking...[/green]")
                day.click()
                clicked = True
                break
        
        if not clicked:
            # Fall back to last available day
            print(f"[yellow]! Target date {target_day} not found, using last available...[/yellow]")
            calendar_days[-1].click()
        
        time.sleep(2)
        
        # Wait for filters
        print(f"[blue]→ Setting booking preferences...[/blue]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "times")))
        
        # Select number of players
        print(f"[blue]  → {NUM_PLAYERS} players...[/blue]")
        player_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'hidden-xs')]//a")
        for btn in player_buttons:
            if btn.text.strip() == str(NUM_PLAYERS):
                btn.click()
                time.sleep(0.5)
                break
        
        # Select time of day
        print(f"[blue]  → {TIME_OF_DAY} time slot...[/blue]")
        time_buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in time_buttons:
            if btn.text.strip() == TIME_OF_DAY and btn.is_displayed():
                btn.click()
                time.sleep(0.5)
                break
        
        # Select holes
        print(f"[blue]  → {NUM_HOLES} holes...[/blue]")
        hole_buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in hole_buttons:
            if btn.text.strip() == NUM_HOLES and btn.is_displayed():
                btn.click()
                time.sleep(2)  # Wait for tee times to load
                break
        
        print(f"[green]✓ Preferences set[/green]")
        
        # Wait a bit more for tee times to fully load
        time.sleep(2)
        
        # Find first available tee time
        print(f"[blue]→ Searching for available tee times...[/blue]")
        tee_times = driver.find_elements(By.CSS_SELECTOR, "li.time-legacy, li.time, #times ul li")
        
        # Filter to only visible tee time elements
        visible_tee_times = [t for t in tee_times if t.is_displayed() and t.text.strip() and ":" in t.text]
        
        if visible_tee_times:
            print(f"[green bold]✓ Found {len(visible_tee_times)} available tee times![/green bold]\n")
            
            first_tee = visible_tee_times[0]
            tee_info = first_tee.text.split("\n")
            
            elapsed = time.time() - start_time
            
            print(f"[cyan]{'='*70}[/cyan]")
            print(f"[green bold]🏌️  FIRST AVAILABLE TEE TIME:[/green bold]")
            print(f"[cyan]{'='*70}[/cyan]")
            for info in tee_info:
                print(f"  [white]{info}[/white]")
            print(f"[cyan]{'='*70}[/cyan]")
            print(f"[yellow]⏱️  Time elapsed: {elapsed:.2f} seconds[/yellow]\n")
            
            if AUTO_BOOK:
                print("[yellow bold]🎯 AUTO_BOOK is enabled - BOOKING TEE TIME NOW![/yellow bold]")
                first_tee.click()
                time.sleep(2)
                print("[green bold]✓ TEE TIME BOOKED![/green bold]")
                
                # Keep browser open to complete booking
                print("\n[blue]Browser staying open for 60 seconds to complete booking...[/blue]")
                time.sleep(60)
            else:
                print("[yellow]ℹ️  AUTO_BOOK is disabled. To auto-book, set AUTO_BOOK=true in .env[/yellow]")
                print("[blue]Browser staying open for 30 seconds for inspection...[/blue]")
                time.sleep(30)
        else:
            print("[red]✗ No tee times found - they may not be released yet[/red]")
            print("[yellow]Make sure to run this at exactly 7:00 AM EST![/yellow]")
            time.sleep(20)
        
    except Exception as e:
        print(f"[red bold]✗ Error: {e}[/red bold]")
        import traceback
        traceback.print_exc()
        time.sleep(30)
    
    finally:
        driver.quit()
        print("\n[green]✓ Bot finished[/green]")


def wait_until_release_time():
    """Wait until 7:00 AM EST to run the bot"""
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    
    # Calculate next 7:00 AM
    target = now.replace(hour=7, minute=0, second=0, microsecond=0)
    
    # If it's already past 7 AM today, target tomorrow at 7 AM
    if now >= target:
        target += timedelta(days=1)
    
    wait_seconds = (target - now).total_seconds()
    
    print(f"\n[yellow]⏰ Current time: {now.strftime('%I:%M:%S %p EST')}[/yellow]")
    print(f"[yellow]⏰ Next release: {target.strftime('%A, %B %d at %I:%M %p EST')}[/yellow]")
    print(f"[blue]⏳ Waiting {wait_seconds/3600:.1f} hours...[/blue]\n")
    
    time.sleep(wait_seconds)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        print("[yellow]Running immediately (--now flag)[/yellow]")
        book_tee_time()
    elif len(sys.argv) > 1 and sys.argv[1] == "--wait":
        print("[blue]Waiting until 7:00 AM EST release time...[/blue]")
        wait_until_release_time()
        book_tee_time()
    else:
        print("\n[bold]Bethpage Tee Time Scheduler[/bold]")
        print("\nUsage:")
        print("  python bethpage_scheduler.py --now    # Run immediately (for testing)")
        print("  python bethpage_scheduler.py --wait   # Wait until 7 AM EST, then run")
        print("\nOr set up to run daily at 7 AM EST (see instructions below)\n")

