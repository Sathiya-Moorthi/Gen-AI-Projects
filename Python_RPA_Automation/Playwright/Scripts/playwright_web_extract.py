from playwright.sync_api import sync_playwright
import os

def extract_web_content(url, output_path):
    """
    Opens the given URL using Playwright, extracts page content and metadata,
    and writes them to a text file in the specified output path.
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with sync_playwright() as p:
            # Launch browser (set headless=False if you want to see it)
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            print(f"🌐 Opening: {url}")
            page.goto(url, timeout=120000)  # ⏱️ Increased timeout to 120 seconds
            page.wait_for_load_state("domcontentloaded")  # ✅ More reliable for heavy sites

            # Try safe extraction of metadata
            def safe_meta(selector):
                try:
                    return page.locator(selector).first.get_attribute("content") or "N/A"
                except:
                    return "N/A"

            title = page.title() or "N/A"
            description = safe_meta('meta[name="description"]')
            keywords = safe_meta('meta[name="keywords"]')

            # Extract all visible text
            content = page.inner_text("body")

            # Combine results
            output_data = (
                f"URL: {url}\n"
                f"Title: {title}\n"
                f"Description: {description}\n"
                f"Keywords: {keywords}\n"
                f"{'-'*60}\n"
                f"Page Content:\n\n{content}"
            )
            page.screenshot(path="bbc_content.png")
            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_data)

            print(f"✅ Extraction complete! Data saved to: {output_path}")

            browser.close()

    except Exception as e:
        print(f"❌ Error: {e}")


# Example usage
if __name__ == "__main__":
    url = "https://www.bbc.com/news"
    output_path = r"D:\Gen AI Project\venv\Python_Automation\Playwright\bbc_content.txt"
    extract_web_content(url, output_path)
