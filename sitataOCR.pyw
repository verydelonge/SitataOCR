# ==================== ENVIRONMENT ====================
import sys
import os
import threading
import collections
import re
import gc
import json
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Tuple, Optional
import logging
from datetime import datetime

# ==================== LOGGING SETUP ====================
LOG_FILE = "sitataOCR.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("="*80)
logging.info(f"SitataOCR MAIN APP STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logging.info("="*80)

# ==================== IMPORT ====================
import customtkinter as ctk
import mss
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont

import ddddocr
import pytesseract
import easyocr
from paddleocr import PaddleOCR

# ==================== PATH & KONSTANTA ====================
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
_tess_path = os.path.join(BASE_DIR, "Tesseract-OCR", "tesseract.exe")
if os.path.exists(_tess_path):
    pytesseract.pytesseract.tesseract_cmd = _tess_path

REGION_FILE = "captcha_region.json"
HOTKEY_TRIGGER = "`"
MAX_ATTEMPTS = 2
SCAN_INTERVAL_MS = 120

# ==================== REGION SELECTOR (MERAH) ====================
class RegionSelector:
    def __init__(self, root, on_complete):
        self.on_complete = on_complete
        self.window = tk.Toplevel(root)
        self.window.attributes("-fullscreen", True, "-alpha", 0.35)
        self.window.configure(bg='black')
        self.window.overrideredirect(True)
        self.window.config(cursor="crosshair")

        self.canvas = tk.Canvas(self.window, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        try:
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[0])
                self.bg_image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor=tk.NW)
        except Exception as e:
            logging.error(f"Region selector screenshot error: {e}")

        self.start_x = self.start_y = None
        self.rect = None
        self.overlay = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Escape>", lambda e: self.window.destroy())

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect: self.canvas.delete(self.rect)
        if self.overlay: self.canvas.delete(self.overlay)

    def on_drag(self, event):
        if self.start_x is None: return
        if self.rect: self.canvas.delete(self.rect)
        if self.overlay: self.canvas.delete(self.overlay)

        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y

        # Garis putus-putus merah
        self.rect = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                 outline="#ff0000", 
                                                 width=3, 
                                                 dash=(8, 4))

        # Area merah transparan
        self.overlay = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                    fill="#ff0000", 
                                                    stipple="gray50", 
                                                    outline="")

    def on_release(self, event):
        if self.start_x is None: return
        x = min(self.start_x, event.x)
        y = min(self.start_y, event.y)
        w = abs(event.x - self.start_x)
        h = abs(event.y - self.start_y)

        self.window.destroy()

        if w > 15 and h > 15:
            self.on_complete((x, y, w, h))
        else:
            logging.warning("Region terlalu kecil")

# ==================== SPLASH WINDOW ====================
class SplashWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#0a0a14")

        w, h = 300, 100
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = screen_w - w - 10
        y = screen_h - h - 50
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.frame = tk.Frame(self, bg="#151520", bd=1, relief="solid", highlightbackground="#00d17a", highlightthickness=1)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="🛡️", font=("Segoe UI", 18), fg="#00d17a", bg="#151520").place(x=8, y=8)
        tk.Label(self.frame, text="SitataOCR", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#151520").place(x=40, y=8)
        tk.Label(self.frame, text="Fast OCR", font=("Segoe UI", 7), fg="#8888aa", bg="#151520").place(x=40, y=28)

        self.lbl_status = tk.Label(self.frame, text="Memulai...", font=("Segoe UI", 8, "italic"), fg="#ffaa00", bg="#151520", anchor="w")
        self.lbl_status.place(x=8, y=50, width=280)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Green.Horizontal.TProgressbar", troughcolor="#2a2a3e", background="#00d17a", thickness=8)
        self.progress = ttk.Progressbar(self.frame, style="Green.Horizontal.TProgressbar", length=284, mode="indeterminate")
        self.progress.place(x=8, y=78)
        self.progress.start(12)
        self.lift()

    def update_status(self, text: str):
        self.lbl_status.config(text=text)
        self.update()

    def close(self):
        self.progress.stop()
        self.destroy()

# ==================== MAIN APP ====================
class MiniCaptchaApp:
    def __init__(self, root: ctk.CTk, splash_window: SplashWindow):
        self.root = root
        self.splash = splash_window
        self.root.title("⚡ SitataOCR")
        
        # ==================== POSISI MAIN APP ====================
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        window_width = 300
        window_height = 590
        
        x_pos = screen_w - window_width - 10
        y_pos = screen_h - 48 - window_height - 35   # 80px di atas taskbar

        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        
        self.root.resizable(width=False, height=True)
        self.root.minsize(300, 400)
        self.root.maxsize(300, screen_h - 100)

        self.root.attributes("-topmost", True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.scanning_active = False
        self.current_attempt = 0
        self.last_success_result = ""
        self.region: Optional[Tuple[int, int, int, int]] = None
        self.scan_timer_id = None
        self.img_cache = {}

        self.dddd = None
        self.easy = None
        self.paddle = None
        self.tess_available = True

        self._build_ui()
        threading.Thread(target=self._init_engines, daemon=True).start()

    def _init_engines(self):
        try:
            self._update_splash("Memuat DdddOCR...")
            self.dddd = ddddocr.DdddOcr(show_ad=False)

            self._update_splash("Memuat EasyOCR...")
            self.easy = easyocr.Reader(['en'], gpu=False, verbose=False)

            self._update_splash("Memeriksa Tesseract...")
            try:
                pytesseract.get_tesseract_version()
            except:
                self.tess_available = False

            self._update_splash("✅ Siap!")
            self.root.after(600, self._finish_initialization)
        except Exception as e:
            logging.error(f"Error init engines: {e}")

    def _update_splash(self, text):
        if self.splash and self.splash.winfo_exists():
            self.root.after(0, lambda: self.splash.update_status(text))

    def _finish_initialization(self):
        if self.splash:
            self.splash.close()
        self.root.deiconify()
        self.load_region()
        self.register_hotkey()
        self.update_status("✅ Siap! Tekan ` untuk mulai", "green")

    def _create_vertical_text(self, text: str, color: str):
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        img = Image.new("RGBA", (80, 30), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), text, fill=color, font=font)
        rotated = img.rotate(90, expand=True, resample=Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(rotated)

    def _build_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_frame.grid(row=0, column=0, pady=(15,10), padx=15, sticky="ew")
        btn_frame.grid_columnconfigure((0,1), weight=1)

        self.btn_region = ctk.CTkButton(btn_frame, text="🎯 Pilih Area", command=self.select_region, height=40)
        self.btn_region.grid(row=0, column=0, padx=4, sticky="ew")

        self.btn_run = ctk.CTkButton(btn_frame, text=f"🚀 Run (`)", command=self.start_scanning, 
                                    height=40, fg_color="#00d17a", font=ctk.CTkFont(weight="bold"))
        self.btn_run.grid(row=0, column=1, padx=4, sticky="ew")

        preview_frame = ctk.CTkFrame(self.root, fg_color="#1a1a24")
        preview_frame.grid(row=1, column=0, pady=8, padx=15, sticky="nsew")
        preview_frame.grid_columnconfigure(0, weight=1)

        self.preview_labels = {}
        self.text_cache = {}

        configs = [("Original", "#e0e0e0"), ("Terang", "#7dff7d"), ("Adaptive", "#5eb3ff")]

        for idx, (title, color) in enumerate(configs):
            row = ctk.CTkFrame(preview_frame, fg_color="transparent", height=85)
            row.grid(row=idx, column=0, pady=5, padx=10, sticky="ew")
            row.grid_propagate(False)

            vert_img = self._create_vertical_text(title, color)
            self.text_cache[title] = vert_img
            
            lbl_text = tk.Label(row, image=vert_img, bg="#1a1a24", bd=0)
            lbl_text.pack(side="left", padx=(8, 6))

            lbl_img = ctk.CTkLabel(row, text="", fg_color="#0f0f17", corner_radius=8)
            lbl_img.pack(side="right", fill="both", expand=True, padx=(0,8))
            self.preview_labels[f"prev{idx}"] = lbl_img

        result_frame = ctk.CTkFrame(self.root, fg_color="#16213e")
        result_frame.grid(row=2, column=0, pady=12, padx=15, sticky="ew")
        ctk.CTkLabel(result_frame, text="👑 HASIL (Auto Copy)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(8,4))
        
        self.txt_result = ctk.CTkEntry(result_frame, height=58, font=ctk.CTkFont(size=26, weight="bold"), 
                                     justify="center", corner_radius=10)
        self.txt_result.pack(pady=8, padx=15, fill="x")

        self.lbl_status = ctk.CTkLabel(self.root, text="Siap", height=40, corner_radius=10, 
                                     font=ctk.CTkFont(size=13))
        self.lbl_status.grid(row=3, column=0, padx=15, pady=12, sticky="ew")

    # ==================== METHOD LAIN ====================
    def register_hotkey(self):
        try:
            import keyboard
            keyboard.add_hotkey(HOTKEY_TRIGGER, self.start_scanning)
        except: pass

    def select_region(self):
        self.root.attributes("-alpha", 0.1)
        RegionSelector(self.root, self.on_region_selected)

    def on_region_selected(self, region):
        self.region = region
        self.save_region()
        self.root.attributes("-alpha", 1.0)
        self.update_status("✅ Area tersimpan", "green")

    def start_scanning(self):
        if self.scanning_active: return
        if not self.region:
            self.update_status("❌ Pilih area dulu!", "red")
            return
        self.scanning_active = True
        self.current_attempt = 0
        self.do_scan_attempt()

    def do_scan_attempt(self):
        if not self.scanning_active: return
        self.current_attempt += 1
        self.update_status(f"Percobaan {self.current_attempt}/{MAX_ATTEMPTS}...", "orange")
        threading.Thread(target=self._fast_ocr_worker, daemon=True).start()

    def _fast_ocr_worker(self):
        try:
            x, y, w, h = self.region
            with mss.mss() as sct:
                screenshot = sct.grab({"left": x, "top": y, "width": w, "height": h})
                img_np = np.array(Image.frombytes("RGB", screenshot.size, screenshot.rgb))

            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            _, light = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)
            dark = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

            light_rgb = cv2.cvtColor(light, cv2.COLOR_GRAY2RGB)
            dark_rgb = cv2.cvtColor(dark, cv2.COLOR_GRAY2RGB)

            self.root.after(0, lambda: self._render_previews(img_np, light_rgb, dark_rgb))

            candidates = []
            for img_var in [dark, light]:
                try:
                    _, enc = cv2.imencode('.png', img_var)
                    res = self.dddd.classification(enc.tobytes())
                    candidates.append(res)
                except: pass

                if self.tess_available:
                    try:
                        config = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                        res = pytesseract.image_to_string(img_var, config=config).strip()
                        candidates.append(res)
                    except: pass

            result = self._process_candidates(candidates)
            if len(result) == 6:
                self.root.after(0, lambda: self._on_scan_complete(True, result))
                return

            try:
                res = "".join(self.easy.readtext(dark, detail=0))
                candidates.append(res)
            except: pass

            try:
                if not self.paddle:
                    self.paddle = PaddleOCR(use_angle_cls=False, lang='en', show_log=False)
                res_list = self.paddle.ocr(dark, cls=False)
                if res_list and res_list[0]:
                    txt = "".join([line[1][0] for line in res_list[0]])
                    candidates.append(txt)
            except: pass

            final = self._process_candidates(candidates)
            success = len(final) == 6
            self.root.after(0, lambda: self._on_scan_complete(success, final or "[GAGAL]"))

        except Exception as e:
            logging.error(f"OCR Error: {e}")
            self.root.after(0, lambda: self._on_scan_complete(False, "[GAGAL]"))
        finally:
            gc.collect()

    def _render_previews(self, raw, light, dark):
        try:
            max_w = 210
            imgs = [raw, light, dark]
            labels = list(self.preview_labels.values())
            for i, (img_np, label) in enumerate(zip(imgs, labels)):
                h, w = img_np.shape[:2]
                scale = max_w / w
                new_size = (max_w, max(55, int(h * scale)))
                pil = Image.fromarray(img_np).resize(new_size, Image.Resampling.LANCZOS)
                tkimg = ImageTk.PhotoImage(pil)
                self.img_cache[id(label)] = tkimg
                label.configure(image=tkimg)
        except: pass

    def _process_candidates(self, candidates):
        cleaned = [re.sub(r'[^A-Z0-9]', '', c.upper()) for c in candidates if c]
        if not cleaned: return ""
        for text, _ in collections.Counter(cleaned).most_common():
            if len(text) == 6:
                return text
        return cleaned[0]

    def _on_scan_complete(self, success: bool, result_text: str):
        if not self.scanning_active: return
        if success:
            self.scanning_active = False
            self._update_result(result_text)
        else:
            if self.current_attempt >= MAX_ATTEMPTS:
                self.scanning_active = False
                self._update_result("[GAGAL]")
            else:
                self.scan_timer_id = self.root.after(SCAN_INTERVAL_MS, self.do_scan_attempt)

    def _update_result(self, text: str):
        self.txt_result.delete(0, "end")
        self.txt_result.insert(0, text)
        if text != "[GAGAL]":
            self.txt_result.configure(fg_color="#00d17a", text_color="white")
            if text != self.last_success_result:
                self.last_success_result = text
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                self.update_status(f"✅ {text} (Tercopy)", "green")
            else:
                self.update_status(f"📋 {text}", "green")
        else:
            self.txt_result.configure(fg_color="#ff3366", text_color="white")
            self.update_status("❌ Gagal", "red")

    def update_status(self, message: str, color: str = "blue"):
        colors = {"green":"#00d17a", "red":"#ff3366", "orange":"#ffaa00", "blue":"#3388ff"}
        self.lbl_status.configure(text=message, fg_color=colors.get(color, "#3388ff"))

    def save_region(self):
        if self.region:
            with open(REGION_FILE, "w") as f:
                json.dump({"left": self.region[0], "top": self.region[1], "width": self.region[2], "height": self.region[3]}, f)

    def load_region(self):
        if os.path.exists(REGION_FILE):
            try:
                with open(REGION_FILE) as f:
                    d = json.load(f)
                self.region = (d["left"], d["top"], d["width"], d["height"])
            except: pass

    def on_closing(self):
        self.scanning_active = False
        try:
            import keyboard
            keyboard.unhook_all()
        except: pass
        logging.info("Aplikasi ditutup")
        self.root.destroy()


if __name__ == "__main__":
    try:
        root = ctk.CTk()
        root.withdraw()
        splash = SplashWindow()
        app = MiniCaptchaApp(root, splash)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        logging.critical(f"CRITICAL ERROR: {e}", exc_info=True)
        messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")