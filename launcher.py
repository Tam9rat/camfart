import subprocess
import time
import requests
import sys
import os

os.chdir(r"C:\ProgramData\Camfart")

CREATE_NO_WINDOW = 0x08000000

def is_running():
    try:
        requests.get("http://localhost:8501", timeout=2)
        return True
    except:
        return False

def wait_for_streamlit():
    for _ in range(30):
        try:
            requests.get("http://localhost:8501", timeout=2)
            return True
        except:
            time.sleep(1)
    return False

def open_browser():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for chrome in chrome_paths:
        if os.path.exists(chrome):
            subprocess.Popen([
                chrome,
                f"--app=http://localhost:8501",
                "--start-fullscreen",
                "--window-size=1920,1080",
                "--new-window"
            ])
            return

    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for edge in edge_paths:
        if os.path.exists(edge):
            subprocess.Popen([
                edge,
                f"--app=http://localhost:8501",
                "--start-fullscreen",
                "--window-size=1920,1080",
                "--new-window"
            ])
            return

if __name__ == "__main__":
    if is_running():
        open_browser()
        sys.exit(0)

    proc = subprocess.Popen(
        [r"C:\ProgramData\Camfart\.venv\Scripts\streamlit.exe",
         "run", "query_app.py",
         "--server.port=8501",
         "--server.address=127.0.0.1"],
        cwd=r"C:\ProgramData\Camfart",
        creationflags=CREATE_NO_WINDOW
    )

    if wait_for_streamlit():
        open_browser()
        proc.wait()
    else:
        sys.exit(1)