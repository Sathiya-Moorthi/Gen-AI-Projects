from playwright.async_api import async_playwright
import asyncio

async def playwright_function():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        #navigation
        await page.goto("https://google.com")


        await page.wait_for_timeout(5000)  # Wait for 5 seconds to see the page
        await browser.close()

if __name__ == "__main__":
    asyncio.run(playwright_function())