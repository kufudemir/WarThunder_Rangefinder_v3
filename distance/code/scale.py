"""
Minimap grid scale adjustment window for War Thunder Rangefinder v3.
Allows manual grid distance entry and live one-click synchronization with
War Thunder localhost 8111 telemetry API.
"""

from tkinter import *
from tkinter import ttk
import traceback
import configparser
import urllib.request
import json
from locales import get_text

try: 
    def read_config(name="code/buttons.ini"):
        config = configparser.ConfigParser()
        config.read(name, encoding='utf-8')
        conf = {}
        conf['scale_x'] = config.get("Combinations", "scale_x", fallback="20")
        conf['scale_y'] = config.get("Combinations", "scale_y", fallback="100")
        conf['language'] = config.get("Combinations", "Language", fallback="en")
        return conf
        
    conf = read_config("code/buttons.ini")
    lang = conf['language']

    def get_live_wt_scale():
        try:
            req = urllib.request.Request("http://127.0.0.1:8111/map_info.json", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=0.2) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if 'grid_steps' in data and len(data['grid_steps']) > 0:
                    val = float(data['grid_steps'][0])
                    if val > 0:
                        return int(val)
        except Exception:
            pass
        return None

    try:
        with open('code/scale.txt', 'r') as f:
            scale = f.read().strip()
        if not scale or scale == "0":
            scale = "250"
    except Exception:
        scale = "250"

    root = Tk()
    root.title(get_text("scale_title", lang))
    root.geometry(f"300x160+{conf['scale_x']}+{conf['scale_y']}")
    root.configure(bg="#11161d")
    root.wm_attributes("-topmost", True)
    root.resizable(False, False)

    lbl_title = Label(root, text=get_text("scale_title", lang), font=('Segoe UI', 10, 'bold'), fg="#00ffcc", bg="#11161d")
    lbl_title.pack(pady=(8, 4))

    lbl_status = Label(root, text=get_text("scale_current", lang, scale=scale), font=('Segoe UI', 10), fg="#ffffff", bg="#11161d")
    lbl_status.pack(pady=2)

    entry_frame = Frame(root, bg="#11161d")
    entry_frame.pack(pady=6)

    entry = Entry(entry_frame, width=8, font=('Segoe UI', 12, 'bold'), justify='center', bg="#1e2632", fg="#00ffcc", insertbackground="#00ffcc")
    entry.pack(side="left", padx=5)

    def set_scale_val(val_str):
        try:
            with open('code/scale.txt', 'w') as f:
                f.write(val_str)
            lbl_status.config(text=get_text("scale_current", lang, scale=val_str))
            entry.delete(0, END)
        except Exception:
            pass

    def apply_manual():
        val = entry.get().strip()
        if val.isdigit() and int(val) > 0:
            set_scale_val(val)

    btn_apply = Button(entry_frame, text=get_text("scale_save", lang), command=apply_manual, bg="#008060", fg="#ffffff", font=('Segoe UI', 9, 'bold'), relief="flat", padx=8)
    btn_apply.pack(side="left", padx=2)

    live = get_live_wt_scale()
    btn_frame = Frame(root, bg="#11161d")
    btn_frame.pack(pady=4)

    if live is not None:
        def use_live():
            set_scale_val(str(live))
        btn_live = Button(btn_frame, text=get_text("scale_live", lang, scale=live), command=use_live, bg="#0066cc", fg="#ffffff", font=('Segoe UI', 9), relief="flat")
        btn_live.pack(side="left", padx=4)
    else:
        lbl_wt = Label(btn_frame, text=get_text("wt_api_waiting", lang), font=('Segoe UI', 8), fg="#708090", bg="#11161d")
        lbl_wt.pack(side="left")

    root.mainloop()

except Exception as e:
    with open('error.log', 'a', encoding='utf-8') as f:
        f.write('\n\n')
        traceback.print_exc(file=f, chain=True)
