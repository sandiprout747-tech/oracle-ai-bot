#!/usr/bin/env python3
# ============================================================
#   ORACLE AI BOT — Desktop Agent
#   Created by Sandip | github.com/sandiprout747-tech
#   Template file — run install.py to personalize
# ============================================================

import os, sys, time, json, datetime, threading, platform
import psutil, subprocess
from flask import Flask

# ── CONFIG (auto-filled by setup_wizard.py) ──────────────────
USER_NAME  = "YOUR_NAME_HERE"
USER_CITY  = "YOUR_CITY_HERE"
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"

# ── FLASK APP ─────────────────────────────────────────────────
app = Flask(__name__)

DATA_DIR = os.path.expanduser("~/MyDesktopAI/data")
os.makedirs(DATA_DIR, exist_ok=True)

LOG_FILE = os.path.join(DATA_DIR, "agent_log.txt")

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

@app.route("/status")
def status():
    return json.dumps({
        "status": "online",
        "agent": "Oracle Desktop Agent",
        "owner": USER_NAME,
        "city": USER_CITY,
        "time": str(datetime.datetime.now()),
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent
    })

@app.route("/sysinfo")
def sysinfo():
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return json.dumps({
        "os": platform.system(),
        "release": platform.release(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_total_mb": ram.total // 1024 // 1024,
        "ram_used_mb": ram.used // 1024 // 1024,
        "ram_percent": ram.percent,
        "disk_percent": disk.percent,
        "python": sys.version.split()[0]
    })

@app.route("/running_apps")
def running_apps():
    apps = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            apps.append({"pid": proc.info["pid"], "name": proc.info["name"]})
        except:
            pass
    return json.dumps(apps[:50])

@app.route("/ping")
def ping():
    return json.dumps({"pong": True, "owner": USER_NAME})

# ── STARTUP ───────────────────────────────────────────────────
def startup_banner():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║   Oracle Desktop Agent — Online      ║")
    print(f"  ║   Owner : {USER_NAME:<28}║")
    print(f"  ║   City  : {USER_CITY:<28}║")
    print("  ║   Created by Sandip                  ║")
    print("  ╚══════════════════════════════════════╝")
    print()

if __name__ == "__main__":
    startup_banner()
    log(f"Desktop Agent started for {USER_NAME}")
    # pycaw needs COM init in Flask thread
    def run_flask():
        try:
            from comtypes import CoInitialize
            CoInitialize()
        except:
            pass
        app.run(host="127.0.0.1", port=5050, debug=False, use_reloader=False)
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    log("Flask server running on http://127.0.0.1:5050")
    try:
        while True:
            time.sleep(60)
            log(f"Heartbeat — CPU: {psutil.cpu_percent()}% RAM: {psutil.virtual_memory().percent}%")
    except KeyboardInterrupt:
        log("Desktop Agent stopped.")
