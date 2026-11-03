"""
Tactical HUD Overlay renderer for War Thunder Rangefinder v3.
Renders click-through, topmost visual overlay with localization support.
"""

from tkinter import *
import sys
import win32gui, win32api, win32con, pywintypes
import traceback
import configparser
from locales import get_text

try:
    def read_config(name="code/buttons.ini"):
        config = configparser.ConfigParser()
        config.read(name, encoding='utf-8')
        conf = {}
        conf['print_x'] = config.get("Combinations", "print_x", fallback="20")
        conf['print_y'] = config.get("Combinations", "print_y", fallback="20")
        conf['print_distance'] = config.get("Combinations", "print_distance", fallback="1")
        conf['print_azimuth'] = config.get("Combinations", "print_azimuth", fallback="1")
        conf['print_scale'] = config.get("Combinations", "print_scale", fallback="1")
        conf['print_transparent'] = config.get("Combinations", "print_transparent", fallback="0")
        conf['print_time'] = config.get("Combinations", "print_time", fallback="7")
        conf['language'] = config.get("Combinations", "Language", fallback="en")
        return conf
        
    conf = read_config("code/buttons.ini")
    
    code = sys.argv[1] if len(sys.argv) > 1 else "true"
    is_auto = sys.argv[5] if len(sys.argv) > 5 else "0"
    lang = sys.argv[6] if len(sys.argv) > 6 else conf['language']
    
    root = Tk()
    root.overrideredirect(True)
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", True)
    
    # Modern military color palette
    bg_color = "#0a0e14" if conf['print_transparent'] == "0" else "#000001"
    border_color = "#00f0ff"
    text_primary = "#00ffcc"
    text_secondary = "#e0e6ed"
    text_accent = "#ffaa00"
    text_muted = "#708090"
    
    root.configure(bg=bg_color)
    if conf['print_transparent'] == "1":
        root.wm_attributes("-transparentcolor", "#000001")
        
    geometry = f"+{conf['print_x']}+{conf['print_y']}"
    root.geometry(geometry)
    
    main_frame = Frame(root, bg=bg_color, highlightbackground=border_color, highlightthickness=1 if conf['print_transparent'] == "0" else 0, padx=12, pady=8)
    main_frame.pack()

    if code == "true":
        distance = sys.argv[2] if len(sys.argv) > 2 else "0"
        azimuth = sys.argv[3] if len(sys.argv) > 3 else "0"
        scale = sys.argv[4] if len(sys.argv) > 4 else "250"
        auto_text = get_text("hud_auto", lang) if is_auto == "1" else get_text("hud_man", lang)

        # Tactical Header
        header = Label(main_frame, text=get_text("hud_header", lang), font=('Segoe UI', 8, 'bold'), fg=text_muted, bg=bg_color)
        header.pack(anchor="w")

        # Primary Distance
        if conf['print_distance'] == "1":
            lbl_dist = Label(main_frame, text=f"{distance} m", font=('Segoe UI', 22, 'bold'), fg=text_primary, bg=bg_color)
            lbl_dist.pack(anchor="w", pady=(0, 2))

        # Secondary Details
        info_frame = Frame(main_frame, bg=bg_color)
        info_frame.pack(anchor="w")

        if conf['print_azimuth'] == "1":
            azi_label = get_text("hud_azimuth", lang)
            lbl_az = Label(info_frame, text=f"{azi_label}: {azimuth}°", font=('Segoe UI', 10, 'bold'), fg=text_secondary, bg=bg_color)
            lbl_az.pack(side="left", padx=(0, 10))

        if conf['print_scale'] == "1":
            scale_label = get_text("hud_scale", lang)
            lbl_sc = Label(info_frame, text=f"{scale_label}: {scale}m [{auto_text}]", font=('Segoe UI', 10), fg=text_accent if is_auto == "1" else text_muted, bg=bg_color)
            lbl_sc.pack(side="left")

    elif code == "errorArrow":
        scale = sys.argv[2] if len(sys.argv) > 2 else "250"
        lbl_err = Label(main_frame, text=get_text("hud_err_tank", lang), font=('Segoe UI', 11, 'bold'), fg="#ff4444", bg=bg_color)
        lbl_err.pack(anchor="w")
        lbl_sub = Label(main_frame, text=get_text("hud_err_tank_sub", lang), font=('Segoe UI', 8), fg=text_muted, bg=bg_color)
        lbl_sub.pack(anchor="w")

    elif code == "errorMarker":
        scale = sys.argv[2] if len(sys.argv) > 2 else "250"
        lbl_err = Label(main_frame, text=get_text("hud_err_marker", lang), font=('Segoe UI', 11, 'bold'), fg="#ffbb00", bg=bg_color)
        lbl_err.pack(anchor="w")
        lbl_sub = Label(main_frame, text=get_text("hud_err_marker_sub", lang), font=('Segoe UI', 8), fg=text_muted, bg=bg_color)
        lbl_sub.pack(anchor="w")
        
    elif code == "AError":
        lbl_err = Label(main_frame, text=get_text("hud_err_map", lang), font=('Segoe UI', 11, 'bold'), fg="#ff4444", bg=bg_color)
        lbl_err.pack(anchor="w")

    # Windows Click-Through Style
    try:
        hWindow = pywintypes.HANDLE(int(root.frame(), 16))
        exStyle = win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TRANSPARENT
        win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
    except Exception:
        pass

    duration_ms = int(float(conf['print_time']) * 1000)
    root.after(duration_ms, root.destroy)
    root.mainloop()

except Exception as e:
    with open('error.log', 'a', encoding='utf-8') as f:
        f.write('\n\n')
        traceback.print_exc(file=f, chain=True)
