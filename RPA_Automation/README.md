# RPA Automation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green.svg)](https://playwright.dev/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-orange.svg)](https://selenium.dev/)

Robotic Process Automation scripts using various Python libraries for web and desktop automation.

## Project Structure

```
RPA_Automation/
├── Playwright/          # Modern web automation scripts
├── PyAutoGui/           # Desktop GUI automation scripts
├── Selenium/            # Browser automation scripts
├── .gitignore
└── README.md
```

## Tool Comparison

| Feature | Playwright | Selenium | PyAutoGUI |
|---------|------------|----------|-----------|
| **Type** | Web Automation | Web Automation | Desktop Automation |
| **Browser Support** | Chromium, Firefox, WebKit | Chrome, Firefox, Edge, Safari | N/A |
| **Speed** | Fast | Moderate | Varies |
| **Auto-wait** | Built-in | Manual | N/A |
| **Screenshots** | Yes | Yes | Yes |
| **Use Case** | Modern web apps | Cross-browser testing | Desktop apps, legacy systems |

## Prerequisites

- Python 3.8 or higher
- For Playwright: Chromium/Firefox/WebKit browsers (auto-installed)
- For Selenium: WebDriver for your browser
- For PyAutoGUI: Display server (GUI environment)

## Installation

1. Navigate to this directory:
   ```bash
   cd RPA_Automation
   ```

2. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For Playwright, install browsers:
   ```bash
   playwright install
   ```

## Usage

### Playwright Scripts
```bash
cd Playwright
python your_script.py
```

### Selenium Scripts
```bash
cd Selenium
python your_script.py
```

### PyAutoGUI Scripts
```bash
cd PyAutoGui
python your_script.py
```

## Use Cases

| Tool | Best For |
|------|----------|
| **Playwright** | E2E testing, scraping SPAs, form automation |
| **Selenium** | Cross-browser testing, legacy web apps |
| **PyAutoGUI** | Desktop automation, image recognition, keyboard/mouse control |

## Best Practices

1. **Error Handling**: Always wrap automation in try-except blocks
2. **Timeouts**: Set appropriate timeouts for page loads
3. **Screenshots**: Capture screenshots on failures for debugging
4. **Headless Mode**: Use headless browsers for CI/CD pipelines

## Security Note

- Never hardcode credentials in scripts
- Use environment variables for sensitive data
- Be mindful of rate limiting when automating web interactions

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.
