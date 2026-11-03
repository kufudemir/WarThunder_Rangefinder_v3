"""
War Thunder Tactical Rangefinder v3 - Master Application
Standalone and PyInstaller-ready single-process architecture.
Features:
- Native in-process click-through Tactical HUD overlay (zero console windows, zero subprocess latency).
- Real-time War Thunder localhost 8111 telemetry monitoring.
- Windows System Tray integration with silent background execution.
- Dynamic bilingual localization (English default / Turkish).
- Pure ONNX Runtime AI inference (No PyTorch).
"""

import sys
import os
import threading
import time
import configparser
import traceback
import urllib.request
import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageGrab
import pystray
from pynput.keyboard import GlobalHotKeys
from pynput import mouse
import win32gui, win32api, win32con, pywintypes
try:
    import pyautogui
except Exception:
    pass

# Resolve absolute paths for both PyInstaller bundle and direct source execution
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Ensure search paths include local and distance/code directories
for p in [BASE_DIR, os.path.join(BASE_DIR, "distance"), os.path.join(BASE_DIR, "distance", "code"), os.path.join(BASE_DIR, "code")]:
    if p not in sys.path and os.path.exists(p):
        sys.path.insert(0, p)

from locales import get_text
from detector import FastYoloDetector
import distanceFinder

def resolve_path(rel_path):
    """Finds resource file across standard source and bundled locations."""
    candidates = [
        os.path.join(BASE_DIR, rel_path),
        os.path.join(BASE_DIR, "distance", rel_path),
        os.path.join(BASE_DIR, "distance", "code", rel_path),
        os.path.join(BASE_DIR, "code", rel_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join(BASE_DIR, rel_path)

CONFIG_PATH = resolve_path("code/buttons.ini")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = resolve_path("buttons.ini")

MODEL_PATH = resolve_path("code/models/best.onnx")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = resolve_path("models/best.onnx")

class TacticalHUD:
    """Native in-process click-through HUD overlay."""
    def __init__(self, parent, get_lang_callback):
        self.parent = parent
        self.get_lang = get_lang_callback
        self.hide_timer = None
        
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.lift()
        self.win.wm_attributes("-topmost", True)
        self.win.wm_attributes("-disabled", True)
        
        self.bg_color = "#0a0e14"
        self.border_color = "#00f0ff"
        self.text_primary = "#00ffcc"
        self.text_secondary = "#e0e6ed"
        self.text_accent = "#ffaa00"
        self.text_muted = "#708090"
        
        self.frame = tk.Frame(self.win, bg=self.bg_color, highlightbackground=self.border_color, highlightthickness=1, padx=12, pady=8)
        self.frame.pack()
        
        self.lbl_hdr = tk.Label(self.frame, text="WT RANGEFINDER PRO", font=('Segoe UI', 8, 'bold'), fg=self.text_muted, bg=self.bg_color)
        self.lbl_hdr.pack(anchor="w")
        
        self.lbl_dist = tk.Label(self.frame, text="", font=('Segoe UI', 22, 'bold'), fg=self.text_primary, bg=self.bg_color)
        self.lbl_dist.pack(anchor="w", pady=(0, 2))
        
        self.sub_frame = tk.Frame(self.frame, bg=self.bg_color)
        self.sub_frame.pack(anchor="w")
        
        self.lbl_azi = tk.Label(self.sub_frame, text="", font=('Segoe UI', 10, 'bold'), fg=self.text_secondary, bg=self.bg_color)
        self.lbl_azi.pack(side="left", padx=(0, 10))
        
        self.lbl_scale = tk.Label(self.sub_frame, text="", font=('Segoe UI', 10), fg=self.text_accent, bg=self.bg_color)
        self.lbl_scale.pack(side="left")
        
        self.lbl_error = tk.Label(self.frame, text="", font=('Segoe UI', 11, 'bold'), fg="#ff4444", bg=self.bg_color)
        self.lbl_error_sub = tk.Label(self.frame, text="", font=('Segoe UI', 8), fg=self.text_muted, bg=self.bg_color)

        # Apply Windows click-through style
        try:
            hWindow = pywintypes.HANDLE(int(self.win.frame(), 16))
            exStyle = win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TRANSPARENT
            win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
        except Exception:
            pass

        self.win.withdraw()

    def show(self, status, distance, azimuth, scale, is_auto, x, y, duration_s, show_d, show_a, show_s, transparent):
        if self.hide_timer is not None:
            self.parent.after_cancel(self.hide_timer)
            self.hide_timer = None
            
        lang = self.get_lang()
        bg = "#000001" if transparent else "#0a0e14"
        self.win.configure(bg=bg)
        if transparent:
            self.win.wm_attributes("-transparentcolor", "#000001")
            self.frame.config(bg=bg, highlightthickness=0)
        else:
            self.frame.config(bg=bg, highlightthickness=1)
            
        for w in [self.lbl_hdr, self.lbl_dist, self.sub_frame, self.lbl_azi, self.lbl_scale, self.lbl_error, self.lbl_error_sub]:
            w.config(bg=bg)

        self.lbl_error.pack_forget()
        self.lbl_error_sub.pack_forget()

        if status == "ok":
            self.lbl_dist.pack(anchor="w", pady=(0, 2))
            self.sub_frame.pack(anchor="w")
            
            auto_lbl = get_text("hud_auto", lang) if is_auto == "1" else get_text("hud_man", lang)
            self.lbl_dist.config(text=f"{distance} m" if show_d else "")
            self.lbl_azi.config(text=f"{get_text('hud_azimuth', lang)}: {azimuth}°" if show_a else "")
            self.lbl_scale.config(text=f"{get_text('hud_scale', lang)}: {scale}m [{auto_lbl}]" if show_s else "")
        elif status == "error_tank":
            self.lbl_dist.pack_forget()
            self.sub_frame.pack_forget()
            self.lbl_error.config(text=get_text("hud_err_tank", lang), fg="#ff4444")
            self.lbl_error_sub.config(text=get_text("hud_err_tank_sub", lang))
            self.lbl_error.pack(anchor="w")
            self.lbl_error_sub.pack(anchor="w")
        elif status == "error_marker":
            self.lbl_dist.pack_forget()
            self.sub_frame.pack_forget()
            self.lbl_error.config(text=get_text("hud_err_marker", lang), fg="#ffaa00")
            self.lbl_error_sub.config(text=get_text("hud_err_marker_sub", lang))
            self.lbl_error.pack(anchor="w")
            self.lbl_error_sub.pack(anchor="w")

        self.win.geometry(f"+{x}+{y}")
        self.win.deiconify()
        self.win.lift()
        self.hide_timer = self.parent.after(int(duration_s * 1000), self.win.withdraw)

class ScaleDialog:
    """Native in-process grid scale popup."""
    def __init__(self, parent, get_lang_callback, on_saved_callback):
        self.parent = parent
        self.get_lang = get_lang_callback
        self.on_saved = on_saved_callback
        self.win = None

    def open(self, x=20, y=100):
        if self.win is not None and self.win.winfo_exists():
            self.win.lift()
            self.win.focus_force()
            return
            
        lang = self.get_lang()
        self.win = tk.Toplevel(self.parent)
        self.win.title(get_text("scale_title", lang))
        self.win.geometry(f"300x160+{x}+{y}")
        self.win.configure(bg="#11161d")
        self.win.wm_attributes("-topmost", True)
        self.win.resizable(False, False)

        lbl_title = tk.Label(self.win, text=get_text("scale_title", lang), font=('Segoe UI', 10, 'bold'), fg="#00ffcc", bg="#11161d")
        lbl_title.pack(pady=(8, 4))

        scale_txt = resolve_path("code/scale.txt")
        current_val = "250"
        try:
            if os.path.exists(scale_txt):
                with open(scale_txt, 'r') as f:
                    current_val = f.read().strip() or "250"
        except Exception:
            pass

        lbl_status = tk.Label(self.win, text=get_text("scale_current", lang, scale=current_val), font=('Segoe UI', 10), fg="#ffffff", bg="#11161d")
        lbl_status.pack(pady=2)

        entry_frame = tk.Frame(self.win, bg="#11161d")
        entry_frame.pack(pady=6)

        entry = tk.Entry(entry_frame, width=8, font=('Segoe UI', 12, 'bold'), justify='center', bg="#1e2632", fg="#00ffcc", insertbackground="#00ffcc")
        entry.pack(side="left", padx=5)

        def apply_val():
            v = entry.get().strip()
            if v.isdigit() and int(v) > 0:
                try:
                    with open(scale_txt, 'w') as f:
                        f.write(v)
                    lbl_status.config(text=get_text("scale_current", lang, scale=v))
                    entry.delete(0, "end")
                    self.on_saved(v)
                except Exception:
                    pass

        btn_apply = tk.Button(entry_frame, text=get_text("scale_save", lang), command=apply_val, bg="#008060", fg="#ffffff", font=('Segoe UI', 9, 'bold'), relief="flat", padx=8)
        btn_apply.pack(side="left", padx=2)

        btn_frame = tk.Frame(self.win, bg="#11161d")
        btn_frame.pack(pady=4)

        live = distanceFinder.get_live_wt_scale()
        if live is not None:
            def use_live():
                apply_v = str(live)
                try:
                    with open(scale_txt, 'w') as f:
                        f.write(apply_v)
                    lbl_status.config(text=get_text("scale_current", lang, scale=apply_v))
                    self.on_saved(apply_v)
                except Exception:
                    pass
            btn_live = tk.Button(btn_frame, text=get_text("scale_live", lang, scale=live), command=use_live, bg="#0066cc", fg="#ffffff", font=('Segoe UI', 9), relief="flat")
            btn_live.pack(side="left", padx=4)
        else:
            lbl_wt = tk.Label(btn_frame, text=get_text("wt_api_waiting", lang), font=('Segoe UI', 8), fg="#708090", bg="#11161d")
            lbl_wt.pack(side="left")

class RangefinderApp:
    def __init__(self, root):
        self.root = root
        self.load_config()
        
        self.is_running = True
        self.hotkey_listener = None
        self.mouse_listener = None
        self.detector = None
        self.wt_connected = False
        self.wt_grid_scale = None
        
        # Load ONNX detector
        try:
            self.detector = FastYoloDetector(MODEL_PATH)
            print("[OK] ONNX Tactical Engine initialized successfully.")
        except Exception as e:
            print(f"[!] Warning: Could not initialize detector: {e}")

        # Native HUD and Scale dialog
        self.hud = TacticalHUD(self.root, lambda: self.lang)
        self.scale_dialog = ScaleDialog(self.root, lambda: self.lang, lambda val: None)

        # Setup Master GUI
        self.setup_ui()
        self.update_ui_texts()
        
        # Background services
        self.start_hotkeys()
        self.start_telemetry_monitor()
        self.setup_system_tray()
        
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def load_config(self):
        self.config = configparser.ConfigParser()
        if os.path.exists(CONFIG_PATH):
            self.config.read(CONFIG_PATH, encoding='utf-8')
        
        self.lang = self.config.get("Combinations", "Language", fallback="en")
        self.dist_key = self.config.get("Combinations", "Distance measurement", fallback="t")
        self.scale_key = self.config.get("Combinations", "Scale setting", fallback="<ctrl>+n")
        self.mouse_key = self.config.get("Combinations", "Distance measurement mouse", fallback="")
        self.resolution = self.config.get("Combinations", "Resolution", fallback="3")
        self.print_x = self.config.get("Combinations", "print_x", fallback="20")
        self.print_y = self.config.get("Combinations", "print_y", fallback="20")
        self.print_time = self.config.get("Combinations", "print_time", fallback="7")
        self.print_dist = self.config.get("Combinations", "print_distance", fallback="1")
        self.print_azimuth = self.config.get("Combinations", "print_azimuth", fallback="1")
        self.print_scale = self.config.get("Combinations", "print_scale", fallback="1")
        self.print_transparent = self.config.get("Combinations", "print_transparent", fallback="0")
        self.scale_x = self.config.get("Combinations", "scale_x", fallback="20")
        self.scale_y = self.config.get("Combinations", "scale_y", fallback="100")

    def save_config(self):
        try:
            if not self.config.has_section("Combinations"):
                self.config.add_section("Combinations")
                
            self.config.set("Combinations", "Language", self.lang_var.get())
            self.config.set("Combinations", "Distance measurement", self.ent_dist_key.get().strip())
            self.config.set("Combinations", "Scale setting", self.ent_scale_key.get().strip())
            self.config.set("Combinations", "Distance measurement mouse", self.ent_mouse_key.get().strip())
            self.config.set("Combinations", "Resolution", self.res_var.get())
            self.config.set("Combinations", "print_x", self.ent_px.get().strip())
            self.config.set("Combinations", "print_y", self.ent_py.get().strip())
            self.config.set("Combinations", "print_time", self.ent_time.get().strip())
            self.config.set("Combinations", "print_distance", str(self.chk_dist_var.get()))
            self.config.set("Combinations", "print_azimuth", str(self.chk_az_var.get()))
            self.config.set("Combinations", "print_scale", str(self.chk_sc_var.get()))
            self.config.set("Combinations", "print_transparent", str(self.chk_trans_var.get()))
            self.config.set("Combinations", "scale_x", self.scale_x)
            self.config.set("Combinations", "scale_y", self.scale_y)
            
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                self.config.write(f)
                
            self.lang = self.lang_var.get()
            self.load_config()
            self.restart_hotkeys()
            self.update_ui_texts()
            messagebox.showinfo("Saved", get_text("msg_saved", self.lang))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")

    def setup_ui(self):
        self.root.title("War Thunder Tactical Rangefinder v3")
        self.root.configure(bg="#0c1017")
        
        win_w, win_h = 680, 620
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        pos_x = int((scr_w - win_w) / 2)
        pos_y = int((scr_h - win_h) / 2)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.resizable(False, False)

        # Header Bar
        top_bar = tk.Frame(self.root, bg="#141a24", padx=16, pady=10)
        top_bar.pack(fill="x")

        title_frame = tk.Frame(top_bar, bg="#141a24")
        title_frame.pack(side="left")

        self.lbl_title = tk.Label(title_frame, text="WT RANGEFINDER v3 PRO", font=('Segoe UI', 13, 'bold'), fg="#00ffcc", bg="#141a24")
        self.lbl_title.pack(anchor="w")

        self.lbl_status = tk.Label(title_frame, text="", font=('Segoe UI', 9, 'bold'), fg="#39ff14", bg="#141a24")
        self.lbl_status.pack(anchor="w")

        # Language Switcher
        lang_frame = tk.Frame(top_bar, bg="#141a24")
        lang_frame.pack(side="right")

        tk.Label(lang_frame, text="🌐 Language:", font=('Segoe UI', 9), fg="#a0b0c0", bg="#141a24").pack(side="left", padx=4)
        
        self.lang_var = tk.StringVar(value=self.lang)
        self.btn_lang_en = tk.Radiobutton(lang_frame, text="English", variable=self.lang_var, value="en", command=self.on_language_change,
                                          fg="#ffffff", bg="#141a24", selectcolor="#1e2632", activebackground="#141a24", activeforeground="#00ffcc")
        self.btn_lang_en.pack(side="left", padx=2)

        self.btn_lang_tr = tk.Radiobutton(lang_frame, text="Türkçe", variable=self.lang_var, value="tr", command=self.on_language_change,
                                          fg="#ffffff", bg="#141a24", selectcolor="#1e2632", activebackground="#141a24", activeforeground="#00ffcc")
        self.btn_lang_tr.pack(side="left", padx=2)

        # Telemetry Banner
        self.telemetry_banner = tk.Frame(self.root, bg="#111722", padx=16, pady=6)
        self.telemetry_banner.pack(fill="x")

        self.lbl_telemetry = tk.Label(self.telemetry_banner, text="", font=('Segoe UI', 9), fg="#708090", bg="#111722")
        self.lbl_telemetry.pack(side="left")

        # Action Buttons
        btn_action_bar = tk.Frame(self.root, bg="#0c1017", padx=16, pady=8)
        btn_action_bar.pack(fill="x")

        self.btn_toggle_engine = tk.Button(btn_action_bar, text="", font=('Segoe UI', 10, 'bold'),
                                           command=self.toggle_engine, bg="#008060", fg="#ffffff", relief="flat", padx=12, pady=4)
        self.btn_toggle_engine.pack(side="left")

        self.btn_open_scale = tk.Button(btn_action_bar, text="📐 Scale (Ctrl+N)", font=('Segoe UI', 9),
                                        command=self.open_scale_window, bg="#1e2632", fg="#00ffcc", relief="flat", padx=10, pady=4)
        self.btn_open_scale.pack(side="left", padx=8)

        self.btn_tray = tk.Button(btn_action_bar, text="", font=('Segoe UI', 9),
                                  command=self.hide_to_tray, bg="#1e2632", fg="#a0b0c0", relief="flat", padx=10, pady=4)
        self.btn_tray.pack(side="right")

        body = tk.Frame(self.root, bg="#0c1017", padx=16, pady=4)
        body.pack(fill="both", expand=True)

        # Controls Section
        self.grp_controls = tk.LabelFrame(body, text="", font=('Segoe UI', 9, 'bold'), fg="#00ffcc", bg="#0c1017", padx=10, pady=6)
        self.grp_controls.pack(fill="x", pady=4)

        self.lbl_dist_key = tk.Label(self.grp_controls, text="", fg="#ffffff", bg="#0c1017", font=('Segoe UI', 9))
        self.lbl_dist_key.grid(row=0, column=0, sticky="w", pady=3)
        self.ent_dist_key = tk.Entry(self.grp_controls, width=12, font=('Segoe UI', 9, 'bold'), bg="#161f2e", fg="#00ffcc", insertbackground="#00ffcc")
        self.ent_dist_key.grid(row=0, column=1, sticky="w", padx=10)
        self.ent_dist_key.insert(0, self.dist_key)

        self.lbl_scale_key = tk.Label(self.grp_controls, text="", fg="#ffffff", bg="#0c1017", font=('Segoe UI', 9))
        self.lbl_scale_key.grid(row=1, column=0, sticky="w", pady=3)
        self.ent_scale_key = tk.Entry(self.grp_controls, width=12, font=('Segoe UI', 9, 'bold'), bg="#161f2e", fg="#00ffcc", insertbackground="#00ffcc")
        self.ent_scale_key.grid(row=1, column=1, sticky="w", padx=10)
        self.ent_scale_key.insert(0, self.scale_key)

        self.lbl_mouse_key = tk.Label(self.grp_controls, text="", fg="#a0b0c0", bg="#0c1017", font=('Segoe UI', 9))
        self.lbl_mouse_key.grid(row=2, column=0, sticky="w", pady=3)
        self.ent_mouse_key = tk.Entry(self.grp_controls, width=12, font=('Segoe UI', 9), bg="#161f2e", fg="#ffffff", insertbackground="#ffffff")
        self.ent_mouse_key.grid(row=2, column=1, sticky="w", padx=10)
        self.ent_mouse_key.insert(0, self.mouse_key)

        # Resolution Section
        self.grp_resolution = tk.LabelFrame(body, text="", font=('Segoe UI', 9, 'bold'), fg="#00ffcc", bg="#0c1017", padx=10, pady=6)
        self.grp_resolution.pack(fill="x", pady=4)

        self.res_var = tk.StringVar(value=self.resolution)
        resolutions = [
            ('0', '1366 x 768 (HD)'),
            ('1', '1440 x 900'),
            ('2', '1680 x 1050'),
            ('3', '1920 x 1080 (Full HD)'),
            ('4', '2560 x 1440 (2K QHD)'),
            ('5', '3840 x 2160 (4K UHD)')
        ]

        r_row, r_col = 0, 0
        for code, r_label in resolutions:
            rb = tk.Radiobutton(self.grp_resolution, text=r_label, variable=self.res_var, value=code,
                                fg="#ffffff", bg="#0c1017", selectcolor="#161f2e", activebackground="#0c1017", activeforeground="#00ffcc")
            rb.grid(row=r_row, column=r_col, sticky="w", padx=10, pady=2)
            r_col += 1
            if r_col > 1:
                r_col = 0
                r_row += 1

        # HUD Customization
        self.grp_hud = tk.LabelFrame(body, text="", font=('Segoe UI', 9, 'bold'), fg="#00ffcc", bg="#0c1017", padx=10, pady=6)
        self.grp_hud.pack(fill="x", pady=4)

        pos_f = tk.Frame(self.grp_hud, bg="#0c1017")
        pos_f.pack(fill="x", pady=2)

        self.lbl_pos_x = tk.Label(pos_f, text="", fg="#ffffff", bg="#0c1017", font=('Segoe UI', 9))
        self.lbl_pos_x.pack(side="left")
        self.ent_px = tk.Entry(pos_f, width=5, bg="#161f2e", fg="#00ffcc", insertbackground="#00ffcc")
        self.ent_px.pack(side="left", padx=4)
        self.ent_px.insert(0, self.print_x)

        self.lbl_pos_y = tk.Label(pos_f, text="", fg="#ffffff", bg="#0c1017", font=('Segoe UI', 9))
        self.lbl_pos_y.pack(side="left", padx=(10, 0))
        self.ent_py = tk.Entry(pos_f, width=5, bg="#161f2e", fg="#00ffcc", insertbackground="#00ffcc")
        self.ent_py.pack(side="left", padx=4)
        self.ent_py.insert(0, self.print_y)

        self.lbl_duration = tk.Label(pos_f, text="", fg="#ffffff", bg="#0c1017", font=('Segoe UI', 9))
        self.lbl_duration.pack(side="left", padx=(12, 0))
        self.ent_time = tk.Entry(pos_f, width=5, bg="#161f2e", fg="#00ffcc", insertbackground="#00ffcc")
        self.ent_time.pack(side="left", padx=4)
        self.ent_time.insert(0, self.print_time)

        chk_f = tk.Frame(self.grp_hud, bg="#0c1017")
        chk_f.pack(fill="x", pady=4)

        self.chk_dist_var = tk.IntVar(value=int(self.print_dist))
        self.chk_dist = tk.Checkbutton(chk_f, text="", variable=self.chk_dist_var, fg="#ffffff", bg="#0c1017",
                                       selectcolor="#161f2e", activebackground="#0c1017", activeforeground="#00ffcc")
        self.chk_dist.pack(side="left", padx=4)

        self.chk_az_var = tk.IntVar(value=int(self.print_azimuth))
        self.chk_az = tk.Checkbutton(chk_f, text="", variable=self.chk_az_var, fg="#ffffff", bg="#0c1017",
                                     selectcolor="#161f2e", activebackground="#0c1017", activeforeground="#00ffcc")
        self.chk_az.pack(side="left", padx=4)

        self.chk_sc_var = tk.IntVar(value=int(self.print_scale))
        self.chk_sc = tk.Checkbutton(chk_f, text="", variable=self.chk_sc_var, fg="#ffffff", bg="#0c1017",
                                     selectcolor="#161f2e", activebackground="#0c1017", activeforeground="#00ffcc")
        self.chk_sc.pack(side="left", padx=4)

        self.chk_trans_var = tk.IntVar(value=int(self.print_transparent))
        self.chk_trans = tk.Checkbutton(chk_f, text="", variable=self.chk_trans_var, fg="#ffaa00", bg="#0c1017",
                                       selectcolor="#161f2e", activebackground="#0c1017", activeforeground="#ffaa00")
        self.chk_trans.pack(side="left", padx=8)

        # Bottom Bar
        bottom_bar = tk.Frame(self.root, bg="#0c1017", padx=16, pady=8)
        bottom_bar.pack(fill="x")

        self.btn_reset = tk.Button(bottom_bar, text="", font=('Segoe UI', 9), command=self.reset_defaults,
                                   bg="#232d3d", fg="#ffffff", relief="flat", padx=10, pady=4)
        self.btn_reset.pack(side="left")

        self.btn_save = tk.Button(bottom_bar, text="", font=('Segoe UI', 10, 'bold'), command=self.save_config,
                                  bg="#008060", fg="#ffffff", relief="flat", padx=14, pady=4)
        self.btn_save.pack(side="right")

    def update_ui_texts(self):
        lang = self.lang
        self.lbl_title.config(text=get_text("app_title", lang))
        
        if self.is_running:
            self.lbl_status.config(text=get_text("status_running", lang), fg="#39ff14")
            self.btn_toggle_engine.config(text=get_text("btn_stop", lang), bg="#992222")
        else:
            self.lbl_status.config(text=get_text("status_stopped", lang), fg="#ffaa00")
            self.btn_toggle_engine.config(text=get_text("btn_start", lang), bg="#008060")

        self.btn_tray.config(text=get_text("btn_minimize", lang))
        self.grp_controls.config(text=get_text("grp_controls", lang))
        self.lbl_dist_key.config(text=get_text("lbl_dist_key", lang))
        self.lbl_scale_key.config(text=get_text("lbl_scale_key", lang))
        self.lbl_mouse_key.config(text=get_text("lbl_mouse_key", lang))

        self.grp_resolution.config(text=get_text("grp_resolution", lang))
        self.grp_hud.config(text=get_text("grp_hud", lang))
        self.lbl_pos_x.config(text=get_text("lbl_hud_pos_x", lang))
        self.lbl_pos_y.config(text=get_text("lbl_hud_pos_y", lang))
        self.lbl_duration.config(text=get_text("lbl_hud_time", lang))

        self.chk_dist.config(text=get_text("chk_dist", lang))
        self.chk_az.config(text=get_text("chk_azimuth", lang))
        self.chk_sc.config(text=get_text("chk_scale", lang))
        self.chk_trans.config(text=get_text("chk_transparent", lang))

        self.btn_save.config(text=get_text("btn_save", lang))
        self.btn_reset.config(text=get_text("btn_reset", lang))

        self.update_telemetry_label()

    def on_language_change(self):
        self.lang = self.lang_var.get()
        self.update_ui_texts()
        self.update_tray_menu()

    def update_telemetry_label(self):
        if self.wt_connected:
            self.lbl_telemetry.config(text=get_text("wt_api_connected", self.lang, scale=self.wt_grid_scale), fg="#00ffcc")
        else:
            self.lbl_telemetry.config(text=get_text("wt_api_waiting", self.lang), fg="#708090")

    def toggle_engine(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_hotkeys()
        else:
            self.stop_hotkeys()
        self.update_ui_texts()
        self.update_tray_menu()

    def open_scale_window(self):
        """Opens native in-process scale dialog (zero subprocesses)."""
        x = int(self.scale_x) if self.scale_x.isdigit() else 20
        y = int(self.scale_y) if self.scale_y.isdigit() else 100
        self.root.after(0, lambda: self.scale_dialog.open(x, y))

    def trigger_distance_measurement(self):
        """Called upon distance hotkey trigger."""
        if not self.is_running or self.detector is None:
            return
            
        time.sleep(0.12)
        res = distanceFinder.calculate_distance(self.detector)
        status, dist, angle, scale, is_auto, _ = res
        
        # Display native HUD overlay on UI thread
        x = int(self.print_x) if self.print_x.isdigit() else 20
        y = int(self.print_y) if self.print_y.isdigit() else 20
        dur = float(self.print_time) if self.print_time else 7.0
        s_d = self.chk_dist_var.get() == 1
        s_a = self.chk_az_var.get() == 1
        s_s = self.chk_sc_var.get() == 1
        trans = self.chk_trans_var.get() == 1
        
        self.root.after(0, lambda: self.hud.show(status, dist, angle, scale, is_auto, x, y, dur, s_d, s_a, s_s, trans))

    def start_hotkeys(self):
        self.stop_hotkeys()
        
        hotkeys = {}
        if self.dist_key:
            hotkeys[self.dist_key] = self.trigger_distance_measurement
        if self.scale_key:
            hotkeys[self.scale_key] = self.open_scale_window
            
        def run_keyboard():
            try:
                with GlobalHotKeys(hotkeys) as listener:
                    self.hotkey_listener = listener
                    listener.join()
            except Exception as e:
                print(f"[!] Keyboard listener error: {e}")

        threading.Thread(target=run_keyboard, daemon=True).start()

        if self.mouse_key:
            def on_mouse_click(x, y, button, pressed):
                if not pressed or not self.is_running:
                    return
                if button.name == self.mouse_key:
                    self.trigger_distance_measurement()
                    
            def run_mouse():
                try:
                    with mouse.Listener(on_click=on_mouse_click) as listener:
                        self.mouse_listener = listener
                        listener.join()
                except Exception as e:
                    print(f"[!] Mouse listener error: {e}")

            threading.Thread(target=run_mouse, daemon=True).start()

    def stop_hotkeys(self):
        if self.hotkey_listener is not None:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
            self.hotkey_listener = None
            
        if self.mouse_listener is not None:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
            self.mouse_listener = None

    def restart_hotkeys(self):
        if self.is_running:
            self.start_hotkeys()

    def start_telemetry_monitor(self):
        def poll():
            while True:
                try:
                    req = urllib.request.Request("http://127.0.0.1:8111/map_info.json", headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=0.25) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        if 'grid_steps' in data and len(data['grid_steps']) > 0:
                            scale = int(data['grid_steps'][0])
                            self.wt_connected = True
                            self.wt_grid_scale = scale
                        else:
                            self.wt_connected = False
                except Exception:
                    self.wt_connected = False
                    
                self.root.after(0, self.update_telemetry_label)
                time.sleep(2.5)

        threading.Thread(target=poll, daemon=True).start()

    def reset_defaults(self):
        self.ent_dist_key.delete(0, "end")
        self.ent_dist_key.insert(0, "t")
        self.ent_scale_key.delete(0, "end")
        self.ent_scale_key.insert(0, "<ctrl>+n")
        self.ent_mouse_key.delete(0, "end")
        self.res_var.set("3")
        self.ent_px.delete(0, "end")
        self.ent_px.insert(0, "20")
        self.ent_py.delete(0, "end")
        self.ent_py.insert(0, "20")
        self.ent_time.delete(0, "end")
        self.ent_time.insert(0, "7")
        self.chk_dist_var.set(1)
        self.chk_az_var.set(1)
        self.chk_sc_var.set(1)
        self.chk_trans_var.set(0)

    # --- System Tray Integration ---
    def create_tray_image(self):
        img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((6, 6, 58, 58), outline=(0, 255, 204), width=4)
        d.ellipse((18, 18, 46, 46), outline=(0, 240, 255), width=2)
        d.line((32, 2, 32, 62), fill=(255, 170, 0), width=3)
        d.line((2, 32, 62, 32), fill=(255, 170, 0), width=3)
        return img

    def setup_system_tray(self):
        tray_image = self.create_tray_image()
        
        def on_open(icon, item):
            self.root.after(0, self.restore_from_tray)
            
        def on_toggle(icon, item):
            self.root.after(0, self.toggle_engine)
            
        def on_scale(icon, item):
            self.root.after(0, self.open_scale_window)
            
        def on_lang_en(icon, item):
            self.lang_var.set("en")
            self.root.after(0, self.on_language_change)
            
        def on_lang_tr(icon, item):
            self.lang_var.set("tr")
            self.root.after(0, self.on_language_change)
            
        def on_exit(icon, item):
            self.stop_hotkeys()
            icon.stop()
            self.root.after(0, self.root.destroy)

        self.tray_icon = pystray.Icon("WTRangefinder", tray_image, "WT Rangefinder v3", menu=pystray.Menu(
            pystray.MenuItem(lambda text: get_text("tray_open", self.lang), on_open, default=True),
            pystray.MenuItem(lambda text: get_text("tray_pause" if self.is_running else "tray_resume", self.lang), on_toggle),
            pystray.MenuItem(lambda text: get_text("tray_scale", self.lang), on_scale),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda text: f"{get_text('tray_language', self.lang)}: English", on_lang_en, checked=lambda item: self.lang == "en"),
            pystray.MenuItem(lambda text: f"{get_text('tray_language', self.lang)}: Türkçe", on_lang_tr, checked=lambda item: self.lang == "tr"),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda text: get_text("tray_exit", self.lang), on_exit)
        ))

        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def update_tray_menu(self):
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.update_menu()

    def hide_to_tray(self):
        self.root.withdraw()

    def restore_from_tray(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

if __name__ == "__main__":
    tk_root = tk.Tk()
    app = RangefinderApp(tk_root)
    tk_root.mainloop()
