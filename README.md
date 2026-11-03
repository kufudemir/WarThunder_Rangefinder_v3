# War Thunder Tactical Rangefinder v3 PRO 🎯

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-lightgrey.svg)](https://www.microsoft.com/windows)
[![Original Project](https://img.shields.io/badge/Original%20Repo-Yonisen-orange.svg)](https://github.com/Yonisen/WarThunder_Yellow_Mark_Rangefinder)

> [!NOTE]  
> 🇹🇷 **Türkçe dokümantasyon için [README_TR.md](README_TR.md) dosyasını inceleyebilirsiniz.**

An ultra-fast, AI-driven optical rangefinder for **War Thunder Ground Realistic / Simulator Battles**.  
Measures distance to any target point placed with your squad target marker (yellow mark) using real-time minimap computer vision and War Thunder's internal telemetry API.

Based on the original project [WarThunder_Yellow_Mark_Rangefinder](https://github.com/Yonisen/WarThunder_Yellow_Mark_Rangefinder) by **@Yonisen**, heavily refactored, modernized, and expanded with high-performance architectures.

---

## 🌟 Key Features in v3 PRO

* ⚡ **Ultra-Fast ONNX Engine:** Replaced heavy PyTorch hub runtime with native **ONNX Runtime (CPU)**. Startup time drops from ~10 seconds to **< 0.3s** with zero `pkg_resources` or dependency conflicts.
* 🚀 **Zero-Disk In-Memory Processing:** Screenshots are processed directly in RAM without writing temporary PNG files to disk, eliminating drive latency and wear.
* 🌐 **War Thunder Localhost Telemetry (8111) Auto-Scale:** Automatically queries `http://127.0.0.1:8111/map_info.json` during matches to retrieve the precise map grid step (e.g. 250m, 350m). **No more manual `Ctrl+N` scale entry required!**
* 🎛️ **Modern Tactical Dashboard & System Tray:** Clean dark-mode control panel with live telemetry status and Windows Notification Area (System Tray) support with silent background operation.
* 🌍 **Bilingual Support (English / Türkçe):** Instant on-the-fly language switching from the dashboard and system tray. All HUD notifications and error messages are localized.
* 📦 **Standalone Executable Ready:** Can be compiled into a single self-contained `.exe` via `build_exe.bat`—no Python installation required on the target machine.
* 🖥️ **Non-Intrusive Click-Through HUD:** Translucent HUD overlay that never steals focus or interrupts in-game keyboard/mouse inputs.

---

## ⚙️ In-Game War Thunder Configuration

To ensure accurate minimap coordinate detection, adjust the following settings in War Thunder:

1. **Display Mode:**
   * Go to **Options** -> **Graphics** -> Set **Mode** to `Fullscreen Window`.
2. **Tactical Minimap Size:**
   * Go to **Options** -> **Main Parameters** -> **Ground Vehicle Battle Settings** -> Set **Tactical Map Scale** to `133%` (Maximum).
3. **Squad Target Marker Key:**
   * Go to **Controls** -> **Common** -> Set **"Set target for squad"** to a key of your choice (Default recommended: `T`).

---

## 🚀 Getting Started

### Option 1: Running from Source
1. Ensure Python 3.10+ is installed on your computer.
2. Install required dependencies:
   ```bash
   pip install -r distance/code/yolo5/requirements.txt
   pip install pystray pyinstaller
   ```
3. Run the application:
   * Double-click **`run.bat`** (or execute `pythonw app.pyw`).

### Option 2: Compiling to Standalone `.exe`
To package the application into a single portable `.exe` that runs without installing Python:
1. Double-click **`build_exe.bat`**.
2. When the build finishes, find your standalone binary at:
   ```
   dist/WarThunderRangefinder_v3.exe
   ```

---

## 🎮 How to Use in Combat

1. Launch **War Thunder Tactical Rangefinder** before or during your match.
2. The app will sit quietly in your Windows system tray (near the clock).
3. In battle, aim at an enemy or landmark through your gunsight, binoculars, or third-person camera.
4. Press your designated distance key (Default: **`T`**).
5. The tactical HUD overlay will immediately display:
   * 🎯 **Range** (Target distance in meters)
   * 🧭 **Azimuth** (Compass heading in degrees)
   * 📐 **Grid Scale** (`[AUTO]` if retrieved from WT API or `[MAN]` if manual)

---

## ⌨️ Default Hotkeys

| Action | Default Key | Configurable in Settings |
| :--- | :--- | :--- |
| **Measure Distance** | `T` | Yes (Keyboard / Mouse) |
| **Manual Scale Window** | `Ctrl + N` | Yes |
| **Language Switch** | Dashboard / Tray | `English` / `Türkçe` |

---

## 👥 Credits & Acknowledgments

* **Original Author & Model Training:** [Yonisen](https://github.com/Yonisen) — Creator of [WarThunder_Yellow_Mark_Rangefinder](https://github.com/Yonisen/WarThunder_Yellow_Mark_Rangefinder).
* **Ultralytics YOLOv5:** [Ultralytics](https://github.com/ultralytics/yolov5) for the object detection architecture.
* **War Thunder Telemetry API:** Gaijin Entertainment for the local web server endpoint.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
