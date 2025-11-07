import pyautogui
import time
import pyperclip
import webbrowser

def send_whatsapp_message(message):
    print("Opening WhatsApp Web...")
    webbrowser.open("https://web.whatsapp.com/")
    time.sleep(30)  # Wait for WhatsApp Web to fully load

    pyautogui.click(x=255, y=746)  # Example coordinates for search bar
    
    time.sleep(5)

    # Press Enter to open chat
    pyautogui.press("enter")
    time.sleep(5)

    print("Typing message...")
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(5)

    # Press Enter to send the message
    pyautogui.press("enter")
    print("✅ Message sent successfully!")

if __name__ == "__main__":
    msg = "One week Completed - Pyautogui"
    send_whatsapp_message(msg)
