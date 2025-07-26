import pyautogui
import pygetwindow as gw
import time

# Replace this with part of the window title you're looking for
TARGET_TITLE = "main.py"

# Find all open windows
windows = gw.getWindowsWithTitle(TARGET_TITLE)

if windows:
    win = windows[0]
    win.activate()
    time.sleep(0.5)  # wait for focus
    pyautogui.press('f5')
else:
    print(f"No window with title containing '{TARGET_TITLE}' found.")
