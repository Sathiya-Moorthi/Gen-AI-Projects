# PyAutoGUI Automation Scripts

Desktop GUI automation scripts using [PyAutoGUI](https://pyautogui.readthedocs.io/).

## 📂 Scripts

| Script | Description |
|--------|-------------|
| `find_mouse_pointer_position.py` | Utility to find current mouse coordinates |
| `find_position.py` | Extended position finding utilities |
| `get_mouse_position.py` | Simple mouse position getter |
| `pyautogui_operations.py` | Common PyAutoGUI operations and examples |
| `web_search.py` | Automates web search via GUI |
| `whatsapp_auto_send.py` | Automates WhatsApp message sending |

## 🚀 Setup

1. **Install PyAutoGUI**:
   ```bash
   pip install pyautogui
   ```

2. **Run a script**:
   ```bash
   python scripts/pyautogui_operations.py
   ```

## ⚠️ Notes

- Scripts control your mouse and keyboard - don't move the mouse during execution
- Use `pyautogui.FAILSAFE = True` (move mouse to corner to abort)
- Screen resolution may affect coordinate-based scripts

## 📦 Dependencies

- `pyautogui` - Cross-platform GUI automation
- `Pillow` - For screenshot functionality
- Python 3.8+
