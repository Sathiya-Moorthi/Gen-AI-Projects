# playwright_search_with_captcha_pause.py
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import time

def search_and_open_first_link_with_captcha_handling(query, headless=False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)   # headful recommended to solve CAPTCHA
        context = browser.new_context(viewport={"width":1280, "height":800})
        page = context.new_page()

        page.goto("https://www.google.com", timeout=120000)
        # Accept cookie dialog if present (regional text may vary)
        try:
            page.locator("button:has-text('Accept all')").click(timeout=3000)
        except:
            pass

        page.fill("textarea[name='q']", query)
        page.keyboard.press("Enter")

        # wait for results or detect captcha text
        try:
            # Wait for either search results h3 or a captcha indicator text on the page
            page.wait_for_selector("h3", timeout=15000)
        except PWTimeout:
            # If normal results didn't appear, check for CAPTCHA / unusual traffic text
            content = page.content().lower()
            if "unusual traffic" in content or "i'm not a robot" in content or "recaptcha" in content:
                print("⚠️ CAPTCHA / 'unusual traffic' detected. Please solve the CAPTCHA in the opened browser window.")
                # poll until the user resolves CAPTCHA and h3 appears
                while True:
                    try:
                        page.wait_for_selector("h3", timeout=5000)
                        print("✅ CAPTCHA solved (or results loaded). Continuing...")
                        break
                    except PWTimeout:
                        print("...still waiting for manual CAPTCHA solve. Press Ctrl+C to abort.")
                        time.sleep(3)
            else:
                # unknown issue: raise or exit
                raise

        # Click the first result's headline (h3)
        try:
            first_result = page.locator("h3").first
            first_result.click()
            print("➡️ Opened first search result.")
            page.screenshot(path="T20_Score.png", full_page=True)
        except Exception as e:
            print("❌ Failed to click the first result:", e)

        # Optionally extract some content from the opened page
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            title = page.title()
            print("Page title:", title)
        except:
            pass

        # keep browser open a bit so user can see it (optional)
        time.sleep(5)
        browser.close()


if __name__ == "__main__":
    search_query = "India vs Australia 3rd T20 score"
    # Run headless=False so you can manually solve CAPTCHA if it appears
    search_and_open_first_link_with_captcha_handling(search_query, headless=False)
