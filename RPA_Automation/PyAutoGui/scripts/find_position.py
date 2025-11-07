import pyautogui
import time

print("Move your mouse to the desired position.")
print("The program will display the current coordinates.")
print("Press Ctrl+C to stop when you find the right position.")

try:
    while True:
        # Get the current mouse position
        x, y = pyautogui.position()
        # Get the color of the pixel under the mouse
        pixel_color = pyautogui.screenshot().getpixel((x, y))
        
        # Clear the previous line
        print(f"X: {x}, Y: {y}, RGB: {pixel_color}      ", end='\r')
        time.sleep(0.1)  # Add a small delay to prevent high CPU usage
        
except KeyboardInterrupt:
    print(f"\n\nFinal position:")
    print(f"X: {x}, Y: {y}")
    print("\nYou can use these coordinates in your script like this:")
    print(f"pyautogui.click({x}, {y})")
    print(f"pyautogui.moveTo({x}, {y})")