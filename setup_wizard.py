#!/usr/bin/env python3
# ============================================================
#   ORACLE AI BOT — Setup Wizard
#   Created by Sandip | github.com/sandiprout747-tech
# ============================================================

import sys, os, time, re

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

if sys.platform == "win32":
    os.system("color")

def clear():
    os.system("cls" if sys.platform == "win32" else "clear")

PENGUIN_SMALL = f"""
{W}    .---.
{W}   / {Y}o {Y}o{W} \\
{W}   \\  v  /
{W}  __|___|__
{W} /  ORACLE  \\
{W}/____________\\{RESET}
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
    print(f"{W}     \\{RESET}")
    print(f"{W}      \\{RESET}")
    print(PENGUIN_SMALL)

def ask(prompt, required=True, hint=""):
    if hint:
        print(f"  {DIM}{hint}{RESET}")
    while True:
        val = input(f"  {Y}▶ {W}{prompt}: {C}").strip()
        if val:
            return val
        if not required:
            return ""
        print(f"  {R}This field is required. Please enter a value.{RESET}")

def ok(msg):   print(f"  {G}✔  {W}{msg}{RESET}")
def info(msg): print(f"  {C}➤  {DIM}{msg}{RESET}")
def err(msg):  print(f"  {R}✘  {R}{msg}{RESET}")

def section(title):
    print(f"\n{C}{'─'*55}{RESET}")
    print(f"  {BOLD}{Y}{title}{RESET}")
    print(f"{C}{'─'*55}{RESET}\n")

# ── COLLECT USER INFO ─────────────────────────────────────────
def collect_info():
    clear()
    print(f"\n{C}╔══════════════════════════════════════════════════╗")
    print(f"{C}║  {W}{BOLD} 🐧 Oracle Setup Wizard — by Sandip {RESET}{C}           ║")
    print(f"{C}╚══════════════════════════════════════════════════╝{RESET}\n")

    penguin_say(
        "Hello! I'm PenguBot 🐧\n"
        "I'll ask you a few questions to\n"
        "personalize your Oracle AI Bot.\n"
        "Takes about 2 minutes!"
    )

    config = {}

    # ── Name ──
    section("1 · Your Name")
    penguin_say("What should your bot call you?\nThis personalizes all responses.")
    config["USER_NAME"] = ask("Your name (e.g. Alex)", hint="→ Used in greetings and daily briefing")

    # ── Groq API ──
    section("2 · Groq API Key")
    penguin_say(
        "Get your FREE Groq API key from:\n"
        "https://console.groq.com\n"
        "Sign up → API Keys → Create key"
    )
    config["GROQ_API_KEY"] = ask(
        "Groq API Key",
        hint="→ Looks like: gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )

    # ── Telegram Token ──
    section("3 · Telegram Bot Token")
    penguin_say(
        "Get your Bot Token from Telegram:\n"
        "1. Open Telegram\n"
        "2. Search @BotFather\n"
        "3. Send /newbot\n"
        "4. Follow instructions\n"
        "5. Copy the token it gives you"
    )
    config["TELEGRAM_TOKEN"] = ask(
        "Telegram Bot Token",
        hint="→ Looks like: 1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"
    )

    # ── User ID ──
    section("4 · Your Telegram User ID")
    penguin_say(
        "Get your Telegram User ID:\n"
        "1. Open Telegram\n"
        "2. Search @userinfobot\n"
        "3. Send /start\n"
        "4. It shows your ID number"
    )
    while True:
        uid = ask("Your Telegram User ID", hint="→ A number like: 6148435580")
        if uid.isdigit():
            config["MY_USER_ID"] = uid
            break
        print(f"  {R}Must be numbers only. Try again.{RESET}")

    # ── Gmail (optional) ──
    section("5 · Gmail (Optional — press ENTER to skip)")
    penguin_say(
        "For email features (optional):\n"
        "Gmail + App Password required.\n"
        "Press ENTER to skip both."
    )
    config["GMAIL_ADDRESS"] = ask("Gmail address (or ENTER to skip)", required=False,
                                   hint="→ example@gmail.com")
    if config["GMAIL_ADDRESS"]:
        config["GMAIL_APP_PASS"] = ask("Gmail App Password",
                                        hint="→ 16 chars like: abcd efgh ijkl mnop")
    else:
        config["GMAIL_APP_PASS"] = ""

    # ── City ──
    section("6 · Your City (for weather)")
    penguin_say("What city should weather\nreports be based on?")
    config["USER_CITY"] = ask("Your city", hint="→ e.g. Mumbai, London, New York")

    return config

# ── PATCH FILES ───────────────────────────────────────────────
def patch_file(filepath, replacements):
    if not os.path.exists(filepath):
        err(f"File not found: {filepath}")
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    ok(f"Patched: {filepath}")
    return True

def write_config(config):
    config_path = os.path.expanduser("~/MyTelegramAI/config.py")
    lines = [
        "# Oracle AI Bot — User Config",
        "# Auto-generated by Setup Wizard — DO NOT share this file",
        "",
        f'USER_NAME      = "{config["USER_NAME"]}"',
        f'GROQ_API_KEY   = "{config["GROQ_API_KEY"]}"',
        f'TELEGRAM_TOKEN = "{config["TELEGRAM_TOKEN"]}"',
        f'MY_USER_ID     = {config["MY_USER_ID"]}',
        f'GMAIL_ADDRESS  = "{config["GMAIL_ADDRESS"]}"',
        f'GMAIL_APP_PASS = "{config["GMAIL_APP_PASS"]}"',
        f'USER_CITY      = "{config["USER_CITY"]}"',
    ]
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    ok(f"Config saved: {config_path}")

def apply_patches(config):
    section("Applying Your Settings")
    info("Patching bot files with your details...")

    replacements = {
        "YOUR_GROQ_API_KEY_HERE":    config["GROQ_API_KEY"],
        "YOUR_TELEGRAM_TOKEN_HERE":  config["TELEGRAM_TOKEN"],
        "YOUR_GMAIL_HERE":           config["GMAIL_ADDRESS"],
        "YOUR_APP_PASSWORD_HERE":    config["GMAIL_APP_PASS"],
        "YOUR_NAME_HERE":            config["USER_NAME"],
        "YOUR_CITY_HERE":            config["USER_CITY"],
        "0  # YOUR_USER_ID":         config["MY_USER_ID"],
    }

    patch_file(os.path.expanduser("~/MyTelegramAI/mybot.py"), replacements)
    patch_file(os.path.expanduser("~/MyDesktopAI/deskagent.py"), replacements)
    write_config(config)

# ── SUMMARY ───────────────────────────────────────────────────
def print_summary(config):
    clear()
    print(f"\n{G}╔══════════════════════════════════════════════════╗")
    print(f"{G}║    {W}{BOLD}Setup Complete! Here's your config:  {RESET}{G}          ║")
    print(f"{G}╚══════════════════════════════════════════════════╝{RESET}\n")
    print(f"  {C}Name   : {W}{config['USER_NAME']}{RESET}")
    print(f"  {C}Groq   : {W}{config['GROQ_API_KEY'][:12]}...{RESET}")
    print(f"  {C}Token  : {W}{config['TELEGRAM_TOKEN'][:12]}...{RESET}")
    print(f"  {C}UserID : {W}{config['MY_USER_ID']}{RESET}")
    print(f"  {C}Gmail  : {W}{config['GMAIL_ADDRESS'] or '(skipped)'}{RESET}")
    print(f"  {C}City   : {W}{config['USER_CITY']}{RESET}")
    print()
    penguin_say(
        f"All set, {config['USER_NAME']}! 🎉\n"
        "Your Oracle AI Bot is personalized.\n"
        "Double-click StartAI.bat on Desktop\n"
        "then send /status in Telegram!",
        color=G
    )

# ── MAIN ─────────────────────────────────────────────────────
def main():
    try:
        config = collect_info()
        apply_patches(config)
        print_summary(config)
    except KeyboardInterrupt:
        print(f"\n\n  {Y}Setup cancelled. Run install.py again to restart.{RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
