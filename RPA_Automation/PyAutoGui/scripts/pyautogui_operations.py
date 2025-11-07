import pyautogui
import time

# Mouse operations


pyautogui.click(100, 100)  # Move to (100, 100) and click

time.sleep(2)               # Wait for 2 seconds

pyautogui.rightClick(100, 100)  # Move to (100, 100) and right-click

time.sleep(4)               # Wait for 4 seconds

pyautogui.click(1361, 15)     # Move to (1361, 15) and click

pyautogui.doubleClick(100, 100)  # Move to (1361, 15) and double-click

pyautogui.scrollup(500)      # Scroll up 500 units

pyautogui.scrolldown(500)    # Scroll down 500 units

pyautogui.moveTo(500, 500, duration=1)  # Move mouse to (500, 500) over 1 second



# Keyboard operations


pyautogui.write('Hello World!')
pyautogui.write('Hello, World!', interval=0.1)  # Type 'Hello, World!' with a delay of 0.1 seconds between each character

time.sleep(5)  # Wait for 5 seconds to switch to the target application

pyautogui.typewrite('python rpa_demo_1.py')

pyautogui.press('enter')  # Press the Enter key

time.sleep(5)  # Wait for 5 seconds to switch to the target application

pyautogui.click(1195, 393)  # Click to focus the text area

pyautogui.hotkey('ctrl', 'a')  # Simulate pressing Ctrl+A to select all 



# image operations


location = pyautogui.locateOnScreen(r'D:\Gen AI Project\venv\RPA_Automation\PyAutoGui\input files\copilot.png')  # Locate the image on the screen
print(location)

time.sleep(2)

pyautogui.click(pyautogui.center(location))  # Click on the located image

print(pyautogui.size())  # Get the screen size

pyautogui.screenshot(r'D:\Gen AI Project\venv\RPA_Automation\PyAutoGui\output files\screenshots\screenshot_pyautogui_operations.png')  # Take a screenshot and save it to the specified path
