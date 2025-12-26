from flask import Flask, request, jsonify
import pyautogui
import subprocess
import time
import os

app = Flask(__name__)

@app.route('/update-notepad', methods=['POST'])
def update_notepad():
    print("Headers:", request.headers)
    print("Body:", request.get_data(as_text=True))
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON or Content-Type not application/json"}), 400
        
    if 'date_time' not in data:
        return jsonify({"error": "Missing 'date_time' in request body"}), 400

    date_time_input = data['date_time']
    filename = "notepad_automation.txt"

    # 1. Check/Create file
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            pass
        print(f"Created new file: {filename}")

    # 2. Launch Notepad
    print(f"Opening {filename} with Notepad...")
    try:
        proc = subprocess.Popen(['notepad.exe', filename])
    except FileNotFoundError:
        return jsonify({"error": "notepad.exe not found"}), 500

    # 3. Wait for Notepad to open
    time.sleep(3) # Increased wait time

    # 4. Automate with PyAutoGUI
    try:
        # Move to end of file
        pyautogui.hotkey('ctrl', 'end')
        time.sleep(0.5)
        
        # New line
        pyautogui.press('enter')
        time.sleep(0.5)
        
        # Type the date time with interval
        pyautogui.write(f"Input received: {date_time_input}", interval=0.05)
        time.sleep(0.5)
        
        # Save
        pyautogui.hotkey('ctrl', 's')
        time.sleep(2) # Increased wait for save
        
        # Close
        print("Closing Notepad...")
        pyautogui.hotkey('alt', 'f4')
        time.sleep(1)
        
        # Fallback: Terminate process if still running (and if it's the same process)
        if proc.poll() is None:
            print("Terminating Notepad process...")
            proc.terminate()
        
        return jsonify({"message": "Notepad updated successfully", "input": date_time_input}), 200
        
        return jsonify({"message": "Notepad updated successfully", "input": date_time_input}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
