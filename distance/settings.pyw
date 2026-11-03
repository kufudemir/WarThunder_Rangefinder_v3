"""
Settings launcher for War Thunder Rangefinder v3.
Starts the unified master control panel (app.pyw).
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(__file__), "app.pyw")
    subprocess.Popen([sys.executable, app_path])
