# playwright_search_with_captcha_pause.py
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import time

def search_and_open_first_link_with_captcha_handling(query, headless=False):
    with sync_playwright() as p:
        # Use more realistic browser settings to avoid detection
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Remove automation detection markers
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print("🌐 Navigating to Google...")
        page.goto("https://www.google.com", timeout=120000)
        
        # Accept cookie dialog if present
        try:
            accept_button = page.locator("button:has-text('Accept all'), button:has-text('I agree')")
            accept_button.click(timeout=3000)
            print("✅ Accepted cookies")
        except:
            print("ℹ️ No cookie dialog found")
        
        # Small delay to appear more human-like
        time.sleep(1)
        
        print(f"🔍 Searching for: {query}")
        page.fill("textarea[name='q'], input[name='q']", query)
        time.sleep(0.5)  # Human-like delay
        page.keyboard.press("Enter")
        
        # Check for CAPTCHA immediately
        time.sleep(2)  # Give page time to load
        
        def check_for_captcha():
            """Check if CAPTCHA is present on the page"""
            try:
                content = page.content().lower()
                page_text = page.locator("body").text_content().lower()
                
                # Multiple CAPTCHA detection methods
                captcha_indicators = [
                    "unusual traffic",
                    "i'm not a robot",
                    "recaptcha",
                    "captcha",
                    "not a robot",
                    "verify you're human"
                ]
                
                for indicator in captcha_indicators:
                    if indicator in content or indicator in page_text:
                        return True
                
                # Check for reCAPTCHA iframe
                if page.locator("iframe[src*='recaptcha']").count() > 0:
                    return True
                    
                return False
            except:
                return False
        
        # Wait for either results or CAPTCHA
        captcha_detected = check_for_captcha()
        
        if captcha_detected:
            print("\n" + "="*60)
            print("⚠️  CAPTCHA DETECTED!")
            print("="*60)
            print("Please solve the CAPTCHA in the browser window.")
            print("The script will wait for you to complete it...")
            print("="*60 + "\n")
            
            # Wait for user to solve CAPTCHA
            solved = False
            max_wait_time = 300  # 5 minutes max
            start_time = time.time()
            
            while not solved and (time.time() - start_time) < max_wait_time:
                try:
                    # Check if search results appeared (CAPTCHA solved)
                    page.wait_for_selector("h3", timeout=5000)
                    print("✅ CAPTCHA solved! Continuing...")
                    solved = True
                    break
                except PWTimeout:
                    # Check if still on CAPTCHA page
                    if not check_for_captcha():
                        print("✅ Page changed - assuming CAPTCHA solved!")
                        solved = True
                        break
                    print("⏳ Still waiting for CAPTCHA solution...")
                    time.sleep(3)
            
            if not solved:
                print("❌ Timeout waiting for CAPTCHA solution")
                browser.close()
                return
        else:
            # No CAPTCHA, wait for normal results
            try:
                page.wait_for_selector("h3", timeout=15000)
                print("✅ Search results loaded")
            except PWTimeout:
                print("❌ No search results found")
                page.screenshot(path="error_screenshot.png", full_page=True)
                browser.close()
                return
        
        # Click the first result
        try:
            time.sleep(1)  # Small delay before clicking
            first_result = page.locator("h3").first
            first_result.click()
            print("➡️  Opened first search result")
            
            # Wait for page to load
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            
            # Take screenshot
            screenshot_path = r"D:\Gen AI Project\venv\RPA_Automation\Playwright\output files\screenshots\T20_Score.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Get page info
            title = page.title()
            url = page.url
            print(f"📄 Page title: {title}")
            print(f"🔗 URL: {url}")
            
        except Exception as e:
            print(f"❌ Failed to click or capture result: {e}")
            page.screenshot(path="error_screenshot.png", full_page=True)
        
        # Keep browser open to view result
        print("\n⏸️  Browser will stay open for 10 seconds...")
        time.sleep(10)
        
        browser.close()
        print("✅ Done!")

if __name__ == "__main__":
    search_query = "India vs Australia 3rd T20 score"
    print(f"Starting search for: '{search_query}'")
    print("Note: Browser will open in visible mode to handle CAPTCHA if needed\n")
    
    # Always run headless=False for CAPTCHA handling
    search_and_open_first_link_with_captcha_handling(search_query, headless=False)