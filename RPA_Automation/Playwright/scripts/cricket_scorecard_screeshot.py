from playwright.sync_api import sync_playwright
import time

def capture_cricket_scorecard():
    """
    Opens a browser, searches for India vs South Africa Women's World Cup Final 2025,
    and captures a screenshot of the scorecard.
    """
    with sync_playwright() as p:
        # Launch browser with additional args to appear more like a real user
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        # Create context with realistic user agent and permissions
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            # viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='Asia/Kolkata'
        )
        
        page = context.new_page()
        
        # Mask automation indicators
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        try:
            # Navigate to Google with more natural behavior
            print("Opening Google...")
            page.goto("https://www.google.com", wait_until="networkidle")
            time.sleep(2)  # Human-like delay
            
            # Wait for the search box and enter the search query with typing delay
            print("Searching for the match...")
            search_box = page.locator('textarea[name="q"], input[name="q"]')
            search_box.click()
            time.sleep(0.5)
            
            # Type with delay to simulate human typing
            page.keyboard.type("India vs South Africa women's world cup final 2025 scorecard", delay=100)
            time.sleep(1)
            page.keyboard.press("Enter")
            
            # Wait for search results to load
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Additional wait for dynamic content
            
            # Check if reCAPTCHA appeared
            if "sorry/index" in page.url or page.locator('iframe[title*="reCAPTCHA"]').count() > 0:
                print("\n⚠️  reCAPTCHA detected! Please solve it manually in the browser window.")
                print("Waiting 60 seconds for you to complete the CAPTCHA...")
                time.sleep(60)
                page.wait_for_load_state("networkidle")
            
            # Find and click the first search result link
            print("Looking for first search result...")
            
            # Common selectors for Google search results
            search_result_selectors = [
                'div#search a[jsname="UWckNb"]',  # Main search result link
                'div#rso a h3',  # Result heading link
                'div.g a[href]:has(h3)',  # Generic result with heading
                'a[href][data-ved]'  # Any link with data-ved attribute
            ]
            
            first_link = None
            for selector in search_result_selectors:
                try:
                    links = page.locator(selector)
                    if links.count() > 0:
                        first_link = links.first
                        print(f"Found search results using selector: {selector}")
                        break
                except:
                    continue
            
            if first_link:
                # Get the URL before clicking (for logging)
                try:
                    link_url = first_link.get_attribute('href')
                    print(f"Clicking first result: {link_url[:100]}...")
                except:
                    print("Clicking first result...")
                
                # Scroll to the link and click
                first_link.scroll_into_view_if_needed()
                time.sleep(1)
                first_link.click()
                
                # Wait for the new page to load
                print("Waiting for page to load...")
                page.wait_for_load_state("networkidle")
                time.sleep(3)  # Wait for dynamic content
                
                print(f"Successfully navigated to: {page.url}")
            else:
                print("⚠️  Could not find any search result links!")
                print("Taking screenshot of search results page...")
            
            # Look for the scorecard section on the new page
            print("Looking for scorecard on the page...")
            
            # Try to find the sports widget/scorecard
            # Google typically shows cricket scores in a specific widget
            scorecard_selectors = [
                'div[data-attrid="SportsSingleGame"]',
                'div.imso_mh',
                'div.IhD7Ob',
                'div[class*="sports"]'
            ]
            
            scorecard_found = False
            for selector in scorecard_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        scorecard_found = True
                        print(f"Found scorecard using selector: {selector}")
                        break
                except:
                    continue
            
            if not scorecard_found:
                print("Scorecard widget not found, taking full page screenshot...")
            
            # Wait a bit for all content to load
            time.sleep(2)
            
            # Define the file path for the screenshot
            screenshot_path = r"D:\Gen AI Project\venv\RPA_Automation\Playwright\output files\screenshots\cricket_scorecard_screenshot.png"
            
            # Take screenshot
            print(f"Taking screenshot and saving to: {screenshot_path}")
            page.screenshot(path=screenshot_path, full_page=True)
            
            print(f"Screenshot saved successfully to: {screenshot_path}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            # Take a screenshot anyway to see what went wrong
            page.screenshot(path="error_screenshot.png")
            print("Error screenshot saved as error_screenshot.png")
        
        finally:
            # Close the browser
            # input("\nPress Enter to close the browser...")  # Keep browser open for review
            # context.close()
            browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    capture_cricket_scorecard()