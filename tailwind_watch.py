import subprocess
import threading
import time

def run_tailwind():
    subprocess.call([
        "npx", "tailwindcss",
        "-i", "./static/css/tailwind.css",
        "-o", "./static/css/tailwind-build.css",
        "--watch"
    ])

threading.Thread(target=run_tailwind, daemon=True).start()
time.sleep(1)
