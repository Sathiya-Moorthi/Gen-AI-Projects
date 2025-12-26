import pyautogui
import subprocess
import time
import sys
import os

def main():
    # 1. Handle command line arguments
    if len(sys.argv) < 2:
        print("Usage: python notepad_automation.py <date_time_string>")
        sys.exit(1)
    
    date_time_input = sys.argv[1]
    filename = "notepad_automation.txt"
    
    # 2. Check if file exists, create if not to avoid "New File" dialog
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            pass # Create empty file
        print(f"Created new file: {filename}")
    else:
        print(f"File exists: {filename}")

    # 3. Launch Notepad
    print(f"Opening {filename} with Notepad...")
    try:
        subprocess.Popen(['notepad.exe', filename])
    except FileNotFoundError:
        print("Error: notepad.exe not found in PATH.")
        sys.exit(1)

    # 4. Wait for Notepad to open
    time.sleep(2) 
    
    # 5. Automate with PyAutoGUI
    # Move to end of file
    pyautogui.hotkey('ctrl', 'end')
    
    # New line
    pyautogui.press('enter')
    
    # Type the date time
    pyautogui.write(f"Input received: {date_time_input}")
    
    # Save
    pyautogui.hotkey('ctrl', 's')
    time.sleep(0.5) # Wait for save
    
    # Close
    pyautogui.hotkey('alt', 'f4')
    
    print("Automation complete.")

if __name__ == "__main__":
    main()
