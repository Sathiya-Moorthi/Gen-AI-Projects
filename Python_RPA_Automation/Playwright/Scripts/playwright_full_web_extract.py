from playwright.sync_api import sync_playwright
import os

def extract_web_content(url, output_path, screenshot_path):
    """
    Opens a webpage using Playwright, extracts metadata, text, hyperlinks, and image URLs,
    saves them into a text file, and captures a full-page screenshot.
    """
    try:
        # Ensure output directories exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

        with sync_playwright() as p:
            # Launch browser (headless=False if you want to see it)
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            print(f"🌐 Opening: {url}")
            page.goto(url, timeout=120000)  # Increased timeout to 2 minutes
            page.wait_for_load_state("domcontentloaded")

            # ---------- Extract Metadata ----------
            def safe_meta(selector):
                try:
                    return page.locator(selector).first.get_attribute("content") or "N/A"
                except:
                    return "N/A"

            title = page.title() or "N/A"
            description = safe_meta('meta[name="description"]')
            keywords = safe_meta('meta[name="keywords"]')

            # ---------- Extract Text Content ----------
            content = page.inner_text("body")

            # ---------- Extract All Hyperlinks ----------
            links = page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
            links = [link for link in links if link]  # remove empty links

            # ---------- Extract All Image URLs ----------
            images = page.eval_on_selector_all("img", "elements => elements.map(e => e.src)")
            images = [img for img in images if img]  # remove empty image links

            # ---------- Take Full Page Screenshot ----------
            print("📸 Taking full-page screenshot...")
            page.screenshot(path=screenshot_path, full_page=True)

            # ---------- Combine Results ----------
            output_data = (
                f"URL: {url}\n"
                f"Title: {title}\n"
                f"Description: {description}\n"
                f"Keywords: {keywords}\n"
                f"{'-'*80}\n\n"
                f"📄 PAGE TEXT CONTENT:\n\n{content}\n\n"
                f"{'-'*80}\n\n"
                f"🔗 HYPERLINKS FOUND ({len(links)}):\n"
                + "\n".join(links)
                + f"\n\n{'-'*80}\n\n"
                f"🖼️ IMAGE URLS FOUND ({len(images)}):\n"
                + "\n".join(images)
            )

            # ---------- Write Everything to File ----------
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_data)

            print(f"✅ Extraction complete!")
            print(f"📝 Data saved to: {output_path}")
            print(f"📸 Screenshot saved to: {screenshot_path}")

            browser.close()

    except Exception as e:
        print(f"❌ Error: {e}")


# Example usage
if __name__ == "__main__":
    url = "https://www.bbc.com/news"  # Change this to any webpage
    output_path = r"D:\Gen AI Project\venv\Python_Automation\Playwright\bbc_full_extract.txt"
    screenshot_path = r"D:\Gen AI Project\venv\Python_Automation\Playwright\bbc_full_page.png"

    extract_web_content(url, output_path, screenshot_path)
