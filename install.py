#!/usr/bin/env python3
# ============================================================
#   ORACLE AI BOT — Installer
#   Created by Sandip | github.com/sandiprout747-tech
# ============================================================

import sys, os, time, subprocess, urllib.request, shutil

# ── ANSI Colors ──────────────────────────────────────────────
R  = "\033[91m"
G  = "\033[92m"
Y  = "\033[93m"
B  = "\033[94m"
M  = "\033[95m"
C  = "\033[96m"
W  = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Enable ANSI on Windows
if sys.platform == "win32":
    os.system("color")
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def clear():
    os.system("cls" if sys.platform == "win32" else "clear")

def typewrite(text, delay=0.018):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ── PENGUIN ───────────────────────────────────────────────────
PENGUIN = f"""
{W}        .88888888:.
{W}       88888888.88888.
{W}     .8888888888888888.
{W}     888888888888888888
{W}     88' {Y}_{W} `88{Y}88{W}` {Y}_{W} `88
{W}     88 {Y}(O){W} 8888 {Y}(O){W} 88
{W}     `8{C}8{W}      88      {C}8{W}8'
{W}      `888   {M}___{W}   888'
{W}       `88  {M}|___|{W}  88'
{W}        `8{B}8888888{W}8'
{W}          `8888888'
{W}           `88888'
{W}            `888'
{W}             `8'        {RESET}
"""

BANNER = f"""
{C}╔══════════════════════════════════════════════════════════╗
{C}║   {W}{BOLD}  ██████╗ ██████╗  █████╗  ██████╗██╗     ███████╗  {RESET}{C}   ║
{C}║   {W}{BOLD} ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║     ██╔════╝  {RESET}{C}   ║
{C}║   {W}{BOLD} ██║   ██║██████╔╝███████║██║     ██║     █████╗    {RESET}{C}   ║
{C}║   {W}{BOLD} ██║   ██║██╔══██╗██╔══██║██║     ██║     ██╔══╝    {RESET}{C}   ║
{C}║   {W}{BOLD} ╚██████╔╝██║  ██║██║  ██║╚██████╗███████╗███████╗  {RESET}{C}   ║
{C}║   {W}{BOLD}  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝  {RESET}{C}   ║
{C}║                                                          ║
{C}║         {Y}✦  Telegram AI Bot Installer  ✦{C}                  ║
{C}║         {DIM}Created by {W}Sandip{RESET}{DIM} · github.com/sandiprout747-tech{RESET}{C}   ║
{C}╚══════════════════════════════════════════════════════════╝{RESET}
"""

def penguin_say(msg, color=C):
    lines = msg.strip().split("\n")
    width = max(len(l) for l in lines) + 4
    border = f"{color}┌{'─'*width}┐{RESET}"
    bottom = f"{color}└{'─'*width}┘{RESET}"
    print(border)
    for l in lines:
        pad = width - len(l) - 2
        print(f"{color}│ {W}{l}{' '*pad}{color} │{RESET}")
    print(bottom)
    print(f"{W}        \\{RESET}")
    print(f"{W}         \\{RESET}")

def step_banner(n, total, title):
    print(f"\n{C}{'─'*60}{RESET}")
    print(f"  {Y}[{n}/{total}]{RESET}  {BOLD}{W}{title}{RESET}")
    print(f"{C}{'─'*60}{RESET}\n")

def ok(msg):    print(f"  {G}✔  {W}{msg}{RESET}")
def warn(msg):  print(f"  {Y}⚠  {Y}{msg}{RESET}")
def err(msg):   print(f"  {R}✘  {R}{msg}{RESET}")
def info(msg):  print(f"  {C}➤  {DIM}{msg}{RESET}")

def progress_bar(label, duration=1.5, steps=30):
    sys.stdout.write(f"  {C}{label}  [{RESET}")
    for i in range(steps):
        time.sleep(duration / steps)
        sys.stdout.write(f"{G}█{RESET}")
        sys.stdout.flush()
    sys.stdout.write(f"{C}] {G}Done!{RESET}\n")
    sys.stdout.flush()

# ── CHECKS ────────────────────────────────────────────────────
def check_python():
    step_banner(1, 6, "Checking Python Version")
    v = sys.version_info
    info(f"Detected Python {v.major}.{v.minor}.{v.micro}")
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        err("Python 3.8+ required!")
        err("Download from https://python.org/downloads")
        sys.exit(1)
    ok(f"Python {v.major}.{v.minor} — OK")

def install_packages():
    step_banner(2, 6, "Installing Required Packages")
    packages = [
        "requests", "pyTelegramBotAPI", "fpdf2", "groq",
        "Flask", "Pillow", "pyautogui", "pyperclip",
        "beautifulsoup4", "pycaw", "comtypes", "psutil"
    ]
    penguin_say("Installing packages...\nThis may take a minute ☕")
    for pkg in packages:
        info(f"Installing {pkg}...")
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "-q"],
            capture_output=True
        )
        if r.returncode == 0:
            ok(pkg)
        else:
            warn(f"{pkg} had issues — continuing anyway")
    progress_bar("Packages", 2.0)

def create_folders():
    step_banner(3, 6, "Creating Bot Folders")
    folders = [
        os.path.expanduser("~/MyTelegramAI"),
        os.path.expanduser("~/MyDesktopAI"),
        os.path.expanduser("~/MyDesktopAI/data"),
    ]
    for f in folders:
        os.makedirs(f, exist_ok=True)
        ok(f"Created: {f}")

def download_templates():
    step_banner(4, 6, "Downloading Bot Templates from GitHub")
    base = "https://raw.githubusercontent.com/sandiprout747-tech/oracle-ai-bot/main/"
    files = {
        "mybot_template.py":     os.path.expanduser("~/MyTelegramAI/mybot.py"),
        "deskagent_template.py": os.path.expanduser("~/MyDesktopAI/deskagent.py"),
    }
    penguin_say("Fetching files from GitHub...")
    for src, dst in files.items():
        try:
            urllib.request.urlretrieve(base + src, dst)
            ok(f"Downloaded → {dst}")
        except Exception as e:
            err(f"Failed to download {src}: {e}")
            err("Check your internet connection and try again.")
            sys.exit(1)

def run_wizard():
    step_banner(5, 6, "Personalization Setup")
    # Download and run setup wizard
    wizard_path = os.path.expanduser("~/setup_wizard.py")
    base = "https://raw.githubusercontent.com/sandiprout747-tech/oracle-ai-bot/main/"
    try:
        urllib.request.urlretrieve(base + "setup_wizard.py", wizard_path)
    except Exception as e:
        err(f"Could not download setup wizard: {e}")
        sys.exit(1)
    subprocess.run([sys.executable, wizard_path], check=True)

def create_launcher():
    step_banner(6, 6, "Creating Desktop Launcher")
    # Find Desktop
    desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    if not os.path.exists(desktop):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    os.makedirs(desktop, exist_ok=True)

    bat_path = os.path.join(desktop, "StartAI.bat")
    bat = f"""@echo off
title Oracle AI Bot
color 0B
echo.
echo   Starting Oracle AI Bot...
echo.
start "" python "%USERPROFILE%\\MyTelegramAI\\mybot.py"
timeout /t 2 /nobreak >nul
start "" python "%USERPROFILE%\\MyDesktopAI\\deskagent.py"
echo.
echo   Both bots are running!
echo   Open Telegram and send /status
echo.
pause
"""
    with open(bat_path, "w") as f:
        f.write(bat)
    ok(f"Launcher created: {bat_path}")
    return bat_path

# ── MAIN ─────────────────────────────────────────────────────
def main():
    clear()
    print(PENGUIN)
    print(BANNER)
    time.sleep(0.5)

    penguin_say(
        "Hi! I'm PenguBot 🐧\n"
        "I'll set up your personal Oracle AI Bot\n"
        "Created by Sandip · Let's go!",
        color=C
    )
    print()
    input(f"  {Y}Press ENTER to begin installation...{RESET}")
    print()

    check_python()
    time.sleep(0.3)
    install_packages()
    time.sleep(0.3)
    create_folders()
    time.sleep(0.3)
    download_templates()
    time.sleep(0.3)
    run_wizard()
    time.sleep(0.3)
    bat = create_launcher()

    # ── SUCCESS ──
    clear()
    print(PENGUIN)
    print(f"""
{G}╔══════════════════════════════════════════════════════════╗
{G}║                                                          ║
{G}║   {W}{BOLD}  ✦  ORACLE AI BOT IS READY!  ✦               {RESET}{G}          ║
{G}║                                                          ║
{G}║   {W}➤  Double-click StartAI.bat on your Desktop{G}          ║
{G}║   {W}➤  Open Telegram → send /status{G}                    ║
{G}║   {W}➤  Your bot will respond!{G}                          ║
{G}║                                                          ║
{G}║   {DIM}Created by {W}Sandip{RESET}{DIM} · github.com/sandiprout747-tech{RESET}{G}   ║
{G}╚══════════════════════════════════════════════════════════╝{RESET}
""")
    penguin_say("All done! Enjoy your AI bot 🐧\nSend /help in Telegram to explore commands.", color=G)
    print()

if __name__ == "__main__":
    main()
