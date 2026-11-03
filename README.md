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

## 🌟 Key Features in v3.0.1

* ⏱️ **Configurable Detection Delay & Ping Retry:** Solves the issue where pressing `T` captured the minimap before the squad ping animation completed. Users can now adjust delay (default: 350 ms) in the dashboard, and a 150 ms micro-retry automatically recovers slow-rendering markers.
* 🎯 **Crosshair / Reticle-Adjacent HUD Preset:** Choose between **Next to Crosshair** (`Center-X + 55, Center-Y - 25`), classic **Top-Left**, or custom screen coordinates. Target distance is displayed right in your peripheral sightline without cluttering center aim.
* ⚡ **Ultra-Fast ONNX Engine:** Native **ONNX Runtime (CPU)** execution. Fast initialization with zero PyTorch bloat.
* 🚀 **Zero-Disk In-Memory Processing:** Screenshots are processed directly in RAM without writing temporary PNG files to disk.
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
1. Ensure Python 3.10+ (Python 3.11 recommended) is installed on your computer.
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   * Double-click **`run.bat`** (or execute `python app.pyw`).

### Option 2: Compiling to Standalone `.exe`
To package the application into a single portable `.exe` that runs without installing Python:
1. Double-click **`build_exe.bat`**.
2. When the build finishes, find your standalone binary at:
   ```
   dist/WarThunderRangefinder_v3.exe
   ```

---

## 🕹️ Controls & Hotkeys

* **`T`** (Default): Set squad marker in War Thunder. Rangefinder automatically waits for ping animation, analyzes the minimap, and renders range/azimuth on your HUD.
* **`Ctrl + N`**: Manual map scale override prompt (fallback in case game telemetry is offline in custom lobbies).
* **`Alt + Q`**: Emergency instant quit.

---

## 📁 Repository Layout

```
WarThunder_Rangefinder_v3/
├── app.pyw                  # Main application, GUI dashboard, and HUD controller
├── requirements.txt         # Consolidated Python dependencies
├── run.bat                  # Safe launcher with error reporting
├── build_exe.bat            # PyInstaller one-file compilation script
├── data/                    # ONNX neural network weights & visual templates
├── distance/                # Core computer vision & telemetry logic
│   └── code/
│       ├── buttons.ini      # Persistent user settings and hotkey configuration
│       ├── locales.py       # English and Turkish localization strings
│       ├── distance_onnx.py # ONNX detection & distance calculation engine
│       └── web.py           # War Thunder 8111 telemetry client
└── dist/                    # Compiled standalone binary (when built)
```

---

## ⚖️ License & Fair Play Notice

This software is distributed under the **MIT License**.  
It operates strictly as an external accessibility overlay reading your local screen and localhost telemetry port (8111) provided natively by Gaijin Entertainment. It does **not** inject code, hook game memory, or modify game files. However, users are always responsible for compliance with War Thunder's Terms of Service.
