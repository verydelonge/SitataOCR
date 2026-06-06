"""
SitataOCR Launcher - X Dark Theme + Logging
"""
import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime

# ==================== LOGGING SETUP ====================
LOG_FILE = "sitataOCR.log"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),  # overwrite setiap launcher start
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("="*70)
    logging.info(f"SitataOCR LAUNCHER STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("="*70)

setup_logging()

# ==================== CONFIG ====================
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(BASE_DIR, "sitataOCR.pyw")
if not os.path.exists(SCRIPT):
    SCRIPT = os.path.join(BASE_DIR, "sitataOCR.py")

TESS_DIR = os.path.join(BASE_DIR, "Tesseract-OCR")
TESS_EXE = os.path.join(TESS_DIR, "tesseract.exe")

REQUIRED_PACKAGES = [
    ("mss", "mss"), ("PIL", "pillow"), ("psutil", "psutil"), ("keyboard", "keyboard"),
    ("cv2", "opencv-python"), ("ddddocr", "ddddocr"), ("pytesseract", "pytesseract"),
    ("easyocr", "easyocr"), ("paddleocr", "paddleocr"), ("customtkinter", "customtkinter"),
]

class LauncherShield(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#000000")

        w, h = 300, 110
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = screen_w - w - 12
        y = screen_h - h - 55
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.frame = tk.Frame(self, bg="#0a0a0a", bd=0)
        self.frame.pack(fill="both", expand=True)

        tk.Frame(self.frame, bg="#00d17a", height=2).pack(fill="x")

        header = tk.Frame(self.frame, bg="#0a0a0a")
        header.pack(pady=12, padx=16, fill="x")

        tk.Label(header, text="🛡️", font=("Segoe UI", 24), fg="#00d17a", bg="#0a0a0a").pack(side="left")
        
        title_frame = tk.Frame(header, bg="#0a0a0a")
        title_frame.pack(side="left", padx=12)
        tk.Label(title_frame, text="SitataOCR", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#0a0a0a").pack(anchor="w")
        tk.Label(title_frame, text="Launcher", font=("Segoe UI", 9), fg="#888888", bg="#0a0a0a").pack(anchor="w")

        self.lbl_status = tk.Label(self.frame, text="Memeriksa komponen...", 
                                   font=("Segoe UI", 9), fg="#aaaaaa", bg="#0a0a0a", anchor="w")
        self.lbl_status.pack(pady=(0,8), padx=20, fill="x")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("X.Horizontal.TProgressbar", troughcolor="#1f1f1f", background="#00d17a", thickness=6)

        self.progress = ttk.Progressbar(self.frame, style="X.Horizontal.TProgressbar", length=260, mode="indeterminate")
        self.progress.pack(pady=8, padx=20)
        self.progress.start(15)

        self.lift()

    def set_status(self, text):
        self.lbl_status.config(text=text)
        logging.info(text)
        self.update()

    def close(self):
        self.progress.stop()
        self.destroy()


def is_tesseract_available():
    paths = [TESS_EXE, r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]
    if any(os.path.exists(p) for p in paths):
        return True
    try:
        return subprocess.call(["where", "tesseract"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except:
        return False


def run_setup(win):
    try:
        win.set_status("Mengecek library...")
        missing = []
        for mod_name, pip_name in REQUIRED_PACKAGES:
            try:
                __import__(mod_name.split('.')[0])
            except ImportError:
                missing.append(pip_name)

        if missing:
            win.set_status(f"Menginstall {len(missing)} library...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + missing, 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            win.set_status("✅ Library selesai")
        else:
            win.set_status("✅ Library sudah lengkap")

        win.set_status("Mengecek Tesseract...")
        if not is_tesseract_available():
            win.set_status("⚠️ Tesseract tidak ditemukan")
        else:
            win.set_status("✅ Tesseract ditemukan")

        win.set_status("Menjalankan SitataOCR...")
        logging.info("Meluncurkan sitataOCR.pyw")
        subprocess.Popen([sys.executable, SCRIPT], creationflags=subprocess.CREATE_NO_WINDOW)
        
    except Exception as e:
        logging.error(f"Error di Launcher: {e}", exc_info=True)
        win.set_status(f"❌ Error: {str(e)}")

    win.after(1500, win.close)


def main():
    win = LauncherShield()
    threading.Thread(target=run_setup, args=(win,), daemon=True).start()
    win.mainloop()


if __name__ == "__main__":
    main()