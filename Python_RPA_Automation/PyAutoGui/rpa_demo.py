import pyautogui
import time
import webbrowser

# Step 1: Open browser (Chrome in this case)
webbrowser.open("https://www.google.com")
time.sleep(3)  # Wait for the browser to open fully

# Step 2: Type the search query
pyautogui.typewrite("India vs Australia 3rd T20 score", interval=0.05)
pyautogui.press("enter")
time.sleep(4)  # Wait for results to load

# Step 3: Move the mouse to the first link and click
# (Adjust coordinates based on your screen resolution)
# You can find coordinates using: pyautogui.position()
# Hover over the link and run: print(pyautogui.position())

pyautogui.moveTo(419, 239, duration=0.5)  # Example coordinates
pyautogui.click()

print("✅ Search completed and first result clicked!")
