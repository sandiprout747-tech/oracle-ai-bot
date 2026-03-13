#!/usr/bin/env python3
# ============================================================
#   ORACLE AI BOT — Smart Installer v2.0
#   Created by Sandip | github.com/sandiprout747-tech
# ============================================================

import sys, os, time, subprocess, urllib.request, shutil, json

# ── ANSI Colors ──────────────────────────────────────────────
R="\033[91m"; G="\033[92m"; Y="\033[93m"; B="\033[94m"
M="\033[95m"; C="\033[96m"; W="\033[97m"; DIM="\033[2m"
BOLD="\033[1m"; RESET="\033[0m"

if sys.platform == "win32":
    os.system("color")
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except: pass

def clear(): os.system("cls" if sys.platform == "win32" else "clear")

# ── PENGUIN FRAMES (animation) ────────────────────────────────
PENGUIN = f"""
{W}      .88888888:.
{W}     88888888.88888.
{W}   .8888888888888888.
{W}   888888888888888888
{W}   88' {Y}_{W} `88{Y}88{W}` {Y}_{W} `88
{W}   88 {Y}(O){W} 8888 {Y}(O){W} 88
{W}   `8{C}8{W}      88      {C}8{W}8'
{W}    `888   {M}____{W}   888'
{W}     `88  {M}|    |{W}  88'
{W}      `8{B}88888888{W}8'
{W}        `8888888'
{W}         `88888'          {RESET}"""

def penguin_say(msg, color=C, mood="normal"):
    face = {
        "normal": f"{Y}(O){W}v{Y}(O){RESET}",
        "happy":  f"{G}^{W}v{G}^{RESET}  ",
        "think":  f"{C}~{W}v{C}~{RESET}  ",
        "warn":   f"{Y}>{W}v{Y}<{RESET}  ",
        "error":  f"{R}X{W}v{R}X{RESET}  ",
        "check":  f"{G}*{W}v{G}*{RESET}  ",
    }.get(mood, f"{Y}(O){W}v{Y}(O){RESET}")

    lines = msg.strip().split("\n")
    width = max(len(l) for l in lines) + 4
    print(f"\n{color}┌{'─'*width}┐{RESET}")
    for l in lines:
        pad = width - len(l) - 2
        print(f"{color}│ {W}{l}{' '*pad}{color} │{RESET}")
    print(f"{color}└{'─'*width}┘{RESET}")
    print(f"  {W}  \\ {face}")
    print(f"   {W}   |{RESET}")

def ok(m):   print(f"  {G}✔  {W}{m}{RESET}")
def warn(m): print(f"  {Y}⚠  {Y}{m}{RESET}")
def err(m):  print(f"  {R}✘  {R}{m}{RESET}")
def info(m): print(f"  {C}➤  {DIM}{m}{RESET}")

def step_banner(n, total, title):
    print(f"\n{C}{'═'*58}{RESET}")
    print(f"  {Y}[STEP {n}/{total}]{RESET}  {BOLD}{W}{title}{RESET}")
    print(f"{C}{'═'*58}{RESET}\n")

def progress(label, steps=25, delay=0.06):
    sys.stdout.write(f"\n  {C}{label}  {W}[{RESET}")
    for i in range(steps):
        time.sleep(delay)
        pct = int((i/steps)*100)
        bar = f"{G}{'█'*i}{'░'*(steps-i-1)}{RESET}"
        sys.stdout.write(f"\r  {C}{label}  {W}[{bar}{W}] {Y}{pct}%{RESET}  ")
        sys.stdout.flush()
    print(f"\r  {C}{label}  {W}[{G}{'█'*steps}{W}] {G}100% Done!{RESET}  ")

def typewrite(text, delay=0.015):
    for ch in text:
        sys.stdout.write(ch); sys.stdout.flush(); time.sleep(delay)
    print()

# ── INTRO SCREEN ──────────────────────────────────────────────
def show_intro():
    clear()
    print(PENGUIN)
    print(f"""
{C}╔══════════════════════════════════════════════════════════╗
{C}║  {W}{BOLD}  ██████╗ ██████╗  █████╗  ██████╗██╗     ███████╗  {RESET}{C}  ║
{C}║  {W}{BOLD} ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║     ██╔════╝  {RESET}{C}  ║
{C}║  {W}{BOLD} ██║   ██║██████╔╝███████║██║     ██║     █████╗    {RESET}{C}  ║
{C}║  {W}{BOLD} ██║   ██║██╔══██╗██╔══██║██║     ██║     ██╔══╝    {RESET}{C}  ║
{C}║  {W}{BOLD} ╚██████╔╝██║  ██║██║  ██║╚██████╗███████╗███████╗  {RESET}{C}  ║
{C}║  {W}{BOLD}  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝ {RESET}{C}  ║
{C}║                                                          ║
{C}║      {Y}✦  Smart Installer v2.0  ✦  by Sandip  ✦{C}          ║
{C}║      {DIM}github.com/sandiprout747-tech/oracle-ai-bot{RESET}{C}        ║
{C}╚══════════════════════════════════════════════════════════╝{RESET}
""")
    penguin_say(
        "Hi! I'm PenguBot 🐧 — your setup guide!\n"
        "I'll validate everything as you go.\n"
        "No wrong inputs get through me!\n"
        "Created by Sandip ✦ Let's go!",
        mood="happy"
    )
    print()
    input(f"  {Y}Press ENTER to begin...{RESET} ")

# ── STEP 1: PYTHON CHECK ──────────────────────────────────────
def check_python():
    step_banner(1, 6, "Checking Python")
    v = sys.version_info
    info(f"Python {v.major}.{v.minor}.{v.micro} detected")
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        penguin_say(
            f"❌ Python {v.major}.{v.minor} is too old!\n"
            "Need Python 3.8 or newer.\n\n"
            "Fix: Go to https://python.org/downloads\n"
            "Download latest → Install → tick 'Add to PATH'\n"
            "Then run this installer again.",
            color=R, mood="error"
        )
        sys.exit(1)
    penguin_say(f"✅ Python {v.major}.{v.minor} — Perfect!", mood="happy", color=G)

# ── STEP 2: INSTALL PACKAGES ──────────────────────────────────
def install_packages():
    step_banner(2, 6, "Installing Packages")
    packages = [
        "requests", "pyTelegramBotAPI", "fpdf2", "groq",
        "Flask", "Pillow", "pyautogui", "pyperclip",
        "beautifulsoup4", "pycaw", "comtypes", "psutil"
    ]
    penguin_say("Installing all required packages...\nThis takes 1-2 minutes ☕", mood="think")
    failed = []
    for pkg in packages:
        sys.stdout.write(f"  {C}Installing {W}{pkg:<20}{RESET}")
        sys.stdout.flush()
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "-q", "--no-warn-script-location"],
            capture_output=True
        )
        if r.returncode == 0:
            print(f"{G}✔{RESET}")
        else:
            print(f"{Y}⚠ (skipped){RESET}")
            failed.append(pkg)

    if failed:
        penguin_say(
            f"⚠ Some packages had issues:\n{', '.join(failed)}\n\n"
            "These are optional features.\n"
            "Core bot will still work fine!",
            color=Y, mood="warn"
        )
    else:
        penguin_say("✅ All packages installed perfectly!", mood="happy", color=G)

# ── STEP 3: CREATE FOLDERS ────────────────────────────────────
def create_folders():
    step_banner(3, 6, "Creating Folders")
    folders = [
        os.path.expanduser("~/MyTelegramAI"),
        os.path.expanduser("~/MyDesktopAI"),
        os.path.expanduser("~/MyDesktopAI/data"),
    ]
    for f in folders:
        os.makedirs(f, exist_ok=True)
        ok(f"Ready: {f}")
    penguin_say("✅ All folders created!", mood="happy", color=G)

# ── STEP 4: DOWNLOAD TEMPLATES ────────────────────────────────
def download_templates():
    step_banner(4, 6, "Downloading Bot Files")
    base = "https://raw.githubusercontent.com/sandiprout747-tech/oracle-ai-bot/main/"
    files = {
        "mybot_template.py":     os.path.expanduser("~/MyTelegramAI/mybot.py"),
        "deskagent_template.py": os.path.expanduser("~/MyDesktopAI/deskagent.py"),
        "setup_wizard.py":       os.path.expanduser("~/setup_wizard.py"),
    }
    penguin_say("Fetching files from GitHub...", mood="think")
    for src, dst in files.items():
        sys.stdout.write(f"  {C}Downloading {W}{src:<30}{RESET}")
        sys.stdout.flush()
        try:
            urllib.request.urlretrieve(base + src, dst)
            print(f"{G}✔{RESET}")
        except Exception as e:
            print(f"{R}✘{RESET}")
            penguin_say(
                f"❌ Download failed: {src}\n\n"
                "Possible causes:\n"
                "• No internet connection\n"
                "• GitHub is down\n"
                "• Firewall blocking\n\n"
                "Fix: Check internet and run installer again.",
                color=R, mood="error"
            )
            sys.exit(1)
    penguin_say("✅ All files downloaded!", mood="happy", color=G)

# ── STEP 5: RUN WIZARD ────────────────────────────────────────
def run_wizard():
    step_banner(5, 6, "Personalization Setup")
    wizard = os.path.expanduser("~/setup_wizard.py")
    if not os.path.exists(wizard):
        err("setup_wizard.py not found!")
        sys.exit(1)
    result = subprocess.run([sys.executable, wizard])
    if result.returncode != 0:
        penguin_say("❌ Setup wizard failed!\nRun installer again.", color=R, mood="error")
        sys.exit(1)

# ── STEP 6: CREATE LAUNCHER ───────────────────────────────────
def create_launcher():
    step_banner(6, 6, "Creating Desktop Launcher")
    # Try OneDrive Desktop first, then normal Desktop
    desktops = [
        os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
    ]
    desktop = next((d for d in desktops if os.path.exists(d)), desktops[1])
    os.makedirs(desktop, exist_ok=True)

    bat = os.path.join(desktop, "StartAI.bat")
    content = f"""@echo off
title Oracle AI Bot — by Sandip
color 0B
cls
echo.
echo  ╔══════════════════════════════════╗
echo  ║   Oracle AI Bot — Starting...   ║
echo  ║   Created by Sandip             ║
echo  ╚══════════════════════════════════╝
echo.
echo  Starting Telegram Bot...
start "" python "%USERPROFILE%\\MyTelegramAI\\mybot.py"
timeout /t 3 /nobreak >nul
echo  Starting Desktop Agent...
start "" python "%USERPROFILE%\\MyDesktopAI\\deskagent.py"
echo.
echo  ✔ Both bots are running!
echo  ✔ Open Telegram and send /status
echo.
pause
"""
    with open(bat, "w", encoding="utf-8") as f:
        f.write(content)
    ok(f"Launcher created: {bat}")
    penguin_say(f"✅ StartAI.bat is on your Desktop!\nDouble-click it anytime to start.", mood="happy", color=G)
    return bat

# ── SUCCESS SCREEN ────────────────────────────────────────────
def success_screen():
    clear()
    print(PENGUIN)
    print(f"""
{G}╔══════════════════════════════════════════════════════════╗
{G}║                                                          ║
{G}║    {W}{BOLD}  🎉  ORACLE AI BOT IS READY!  🎉            {RESET}{G}        ║
{G}║                                                          ║
{G}║    {W}  1. Double-click StartAI.bat on Desktop  {G}          ║
{G}║    {W}  2. Open Telegram                        {G}          ║
{G}║    {W}  3. Send /status to your bot             {G}          ║
{G}║    {W}  4. Send /help to see all commands       {G}          ║
{G}║                                                          ║
{G}║    {DIM}Created by {W}Sandip{RESET}{DIM} · sandiprout747-tech         {RESET}{G}    ║
{G}╚══════════════════════════════════════════════════════════╝{RESET}
""")
    penguin_say(
        "All done! Your Oracle AI Bot is live! 🎉\n"
        "Send /help in Telegram to explore.\n"
        "Enjoy your personal AI assistant!\n"
        "— Made with ❤ by Sandip",
        color=G, mood="happy"
    )

# ── MAIN ─────────────────────────────────────────────────────
def main():
    show_intro()
    check_python()
    install_packages()
    create_folders()
    download_templates()
    run_wizard()
    create_launcher()
    success_screen()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Y}Installation cancelled. Run again to restart.{RESET}\n")
        sys.exit(0)
