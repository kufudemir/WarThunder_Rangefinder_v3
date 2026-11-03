"""
Core Optical Distance Calculator for War Thunder Tactical Rangefinder v3.
Processes in-memory minimap screen captures, performs YOLOv5 ONNX inference,
queries War Thunder localhost 8111 telemetry for grid scale, and calculates
target range and azimuth.
"""

import cv2
import numpy as np
import math
from subprocess import Popen
try:
    import pyautogui
except Exception:
    pyautogui = None
from PIL import ImageGrab
import configparser
import urllib.request
import json
import os
import sys

def get_pythonw():
    """Returns pythonw executable to prevent opening console windows."""
    py = sys.executable
    if py.lower().endswith("python.exe"):
        pw = py[:-4] + "w.exe"
        if os.path.exists(pw):
            return pw
    return py

NO_WINDOW_FLAG = 0x08000000

def get_resource_path(relative_path):
    """Resolves resource paths for PyInstaller bundle and source execution."""
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, relative_path),
        os.path.join(base_dir, "code", relative_path),
        os.path.join(base_dir, "distance", "code", relative_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", relative_path)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join(base_dir, relative_path)

def read_config(name=None):
    if name is None:
        name = get_resource_path("buttons.ini")
    config = configparser.ConfigParser()
    config.read(name, encoding='utf-8')
    res = config.get("Combinations", "Resolution", fallback="3")
    lang = config.get("Combinations", "Language", fallback="en")
    return res, lang

# Resolution definitions: [x, y, w, h, size, sizeReal, default_cell_px]
RESOLUTION_PROFILES = {
    '0': [1034, 436, 329, 329, 329, 329, 44.0],   # 1366x768
    '1': [1054, 514, 384, 384, 384, 384, 51.5],   # 1440x900
    '2': [1234, 604, 444, 444, 444, 444, 59.5],   # 1680x1050
    '3': [1462, 622, 456, 456, 456, 456, 61.25],  # 1920x1080 (Full HD)
    '4': [1952, 832, 605, 605, 465, 605, 81.5],   # 2560x1440 (2K QHD)
    '5': [2940, 1260, 900, 900, 480, 900, 121.0], # 3840x2160 (4K UHD)
    '6': [3924, 1684, 1196, 1196, 460, 1196, 160.0] # 5120x2280
}

def get_live_wt_scale():
    """
    Connects to the War Thunder internal web map service (http://127.0.0.1:8111/map_info.json)
    to automatically retrieve the grid step size in meters.
    """
    try:
        req = urllib.request.Request("http://127.0.0.1:8111/map_info.json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=0.15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'grid_steps' in data and len(data['grid_steps']) > 0:
                val = float(data['grid_steps'][0])
                if val > 0:
                    return int(val)
    except Exception:
        pass
    return None

def calculate_distance(detector):
    """
    Direct in-memory calculation without subprocess overhead.
    Returns: (status, distance, angle, scale, is_auto, language)
    status: 'ok', 'error_tank', 'error_marker'
    """
    try:
        resolution, language = read_config()
        if resolution not in RESOLUTION_PROFILES:
            resolution = '3'
            
        res_info = RESOLUTION_PROFILES[resolution]
        res_x, res_y, res_w, res_h = res_info[0], res_info[1], res_info[2], res_info[3]
        size, size_real = res_info[4], res_info[5]
        default_cell_px = res_info[6]
        size_k = size / size_real
        
        # 1. Pure RAM Screen Capture
        if pyautogui is not None:
            try:
                screen_pil = pyautogui.screenshot(region=(res_x, res_y, res_w, res_h))
            except Exception:
                screen_pil = ImageGrab.grab(bbox=(res_x, res_y, res_x + res_w, res_y + res_h))
        else:
            screen_pil = ImageGrab.grab(bbox=(res_x, res_y, res_x + res_w, res_y + res_h))
        minimap_bgr = cv2.cvtColor(np.array(screen_pil), cv2.COLOR_RGB2BGR)
        
        # 2. Map Scale: Auto-detect via 8111 API with fallback to scale.txt
        live_scale = get_live_wt_scale()
        is_auto = "0"
        scale_txt_path = get_resource_path("scale.txt")
        if live_scale is not None and live_scale > 0:
            scale = live_scale
            is_auto = "1"
            try:
                with open(scale_txt_path, 'w') as f:
                    f.write(str(scale))
            except Exception:
                pass
        else:
            try:
                with open(scale_txt_path, 'r') as f:
                    scale_str = f.read().strip()
                scale = int(scale_str) if scale_str and scale_str != "0" else 250
            except Exception:
                scale = 250
                
        # 3. ONNX Inference
        tank_pos, marker_pos, tank_conf, marker_conf = detector.detect(minimap_bgr)
        
        if tank_pos is None:
            return ("error_tank", 0, 0, scale, is_auto, language)
            
        if marker_pos is None:
            return ("error_marker", 0, 0, scale, is_auto, language)
            
        if int(resolution) > 3:
            tank_pos = (tank_pos[0] / size_k, tank_pos[1] / size_k)
            marker_pos = (marker_pos[0] / size_k, marker_pos[1] / size_k)
            
        print(f"[+] Detected Tank: {tank_pos} ({tank_conf:.2f}), Marker: {marker_pos} ({marker_conf:.2f})")
        
        # 4. Geometry and Azimuth
        dx = abs(tank_pos[0] - marker_pos[0])
        dy = abs(tank_pos[1] - marker_pos[1])
        hypotenuse_px = np.hypot(dx, dy)
        
        if dx == 0:
            angle = 90.0
        else:
            angle = math.degrees(math.atan(dy / dx))
            
        if marker_pos[0] >= tank_pos[0] and marker_pos[1] <= tank_pos[1]:
            angle = 90 - angle
        elif marker_pos[0] >= tank_pos[0] and marker_pos[1] > tank_pos[1]:
            angle = 90 + angle
        elif marker_pos[0] < tank_pos[0] and marker_pos[1] >= tank_pos[1]:
            angle = 270 - angle
        elif marker_pos[0] < tank_pos[0] and marker_pos[1] < tank_pos[1]:
            angle = 270 + angle
            
        angle = (angle + 360) % 360
        
        # 5. Grid Cell Pixel Length via Template Matching with Fallback
        line_px = default_cell_px
        try:
            base_data_dir = getattr(sys, '_MEIPASS', os.path.join(os.path.dirname(__file__), "..", ".."))
            cand1 = os.path.join(base_data_dir, "data", f"resolution_{resolution}")
            cand2 = os.path.join(os.path.dirname(__file__), "..", "..", "data", f"resolution_{resolution}")
            cand3 = os.path.join(os.path.dirname(__file__), "data", f"resolution_{resolution}")
            data_folder = cand1 if os.path.exists(cand1) else (cand2 if os.path.exists(cand2) else cand3)

            letter_a_path = os.path.join(data_folder, "aletter.png")
            letter_e_path = os.path.join(data_folder, "eletter.png")
            
            if os.path.exists(letter_a_path) and os.path.exists(letter_e_path):
                img_a = cv2.imread(letter_a_path)
                img_e = cv2.imread(letter_e_path)
                
                res_a = cv2.matchTemplate(minimap_bgr, img_a, cv2.TM_CCOEFF_NORMED)
                _, val_a, _, pt_a = cv2.minMaxLoc(res_a)
                
                res_e = cv2.matchTemplate(minimap_bgr, img_e, cv2.TM_CCOEFF_NORMED)
                _, val_e, _, pt_e = cv2.minMaxLoc(res_e)
                
                if val_a > 0.55 and val_e > 0.55:
                    calc_line = abs(pt_a[1] - pt_e[1]) / 4.0
                    if calc_line > 10:
                        line_px = calc_line
        except Exception as e:
            print(f"[!] Template matching notice: {e}, using default fallback.")
            
        # 6. Distance in meters
        distance_meters = (hypotenuse_px / line_px) * scale
        print(f"[OK] Range: {round(distance_meters)}m | Azimuth: {round(angle, 1)} deg | Scale: {scale}m ({'AUTO' if is_auto == '1' else 'MAN'})")
        
        return ("ok", round(distance_meters), round(angle, 1), scale, is_auto, language)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ("error", 0, 0, 250, "0", "en")

def checkDistance(detector):
    """Backwards-compatible wrapper."""
    res = calculate_distance(detector)
    status, dist, angle, scale, is_auto, language = res
    python_bin = get_pythonw()
    print_res_path = get_resource_path("printResults.py")
    
    if status == "ok":
        cmd = [python_bin, print_res_path, "true", str(dist), str(angle), str(scale), is_auto, language]
    elif status == "error_tank":
        cmd = [python_bin, print_res_path, "errorArrow", str(scale), is_auto, language]
    elif status == "error_marker":
        cmd = [python_bin, print_res_path, "errorMarker", str(scale), is_auto, language]
    else:
        cmd = [python_bin, print_res_path, "AError", str(scale), is_auto, language]
        
    try:
        return Popen(cmd, creationflags=NO_WINDOW_FLAG)
    except Exception:
        return None
