"""
Command-line runner for War Thunder Rangefinder.
Initializes the ONNX detection engine and listens for distance and scale hotkeys.
"""

import traceback
import sys
import os
import time

sys.path.append('code/')

try:
    def signal1(queue):
        try:
            import signal1
            with open('code/pid1.txt', 'w') as f:
                f.write(str(os.getpid()))
            signal1.signal1(queue)
        except Exception as e:
            with open('error.log', 'a', encoding='utf-8') as f:
                f.write('\n\n')
                traceback.print_exc(file=f, chain=True)
            traceback.print_exc()

    def signal3(queue):
        try:
            import signal3
            with open('code/pid3.txt', 'w') as f:
                f.write(str(os.getpid()))
            signal3.signal3(queue)
        except Exception as e:
            with open('error.log', 'a', encoding='utf-8') as f:
                f.write('\n\n')
                traceback.print_exc(file=f, chain=True)
            traceback.print_exc()

    if __name__ == "__main__":
        import distanceFinder
        from detector import FastYoloDetector
        from subprocess import Popen
        from multiprocessing import Queue, Process 
        from threading import Timer
        
        with open('code/pid.txt', 'w') as f:
            f.write(str(os.getpid()))

        print("======================================================")
        print("    War Thunder Tactical Rangefinder v3 PRO")
        print("======================================================")
        print("[*] Initializing ONNX detection engine...")

        detector = FastYoloDetector('code/models/best.onnx')
        print("[OK] Model loaded successfully (High-performance mode).")

        queue = Queue()
        process1 = Process(target=signal1, args=(queue,))
        process1.start()
        process3 = Process(target=signal3, args=(queue,))
        process3.start()

        def checkSignals():
            global process1, process3
            if (process1.exitcode is not None and process1.exitcode != 0) or (process3.exitcode is not None and process3.exitcode != 0):
                process1 = Process(target=signal1, args=(queue,))
                process1.start()
                process3 = Process(target=signal3, args=(queue,))
                process3.start()
            Timer(0.5, checkSignals).start()
        
        checkSignals()

        print("\n[>>] Waiting for hotkey trigger...")
        print("[>>] Default keys: Distance: 't', Scale window: 'Ctrl+N'\n")

        current_overlay = None

        while True:
            msg = queue.get()
            if msg == "distance":
                if current_overlay is not None:
                    try:
                        current_overlay.terminate()
                    except Exception:
                        pass
                time.sleep(0.12)
                current_overlay = distanceFinder.checkDistance(detector)
            elif msg == "scale":
                py = sys.executable
                if py.lower().endswith("python.exe"):
                    pw = py[:-4] + "w.exe"
                    if os.path.exists(pw):
                        py = pw
                cmd = [py, 'code/scale.py']
                Popen(cmd, creationflags=0x08000000)

except Exception as e:
    with open('error.log', 'a', encoding='utf-8') as f:
        f.write('\n\n')
        traceback.print_exc(file=f, chain=True)
    traceback.print_exc()
