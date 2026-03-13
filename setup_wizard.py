#!/usr/bin/env python3
# ============================================================
#   ORACLE AI BOT — Smart Setup Wizard v2.0
#   Created by Sandip | github.com/sandiprout747-tech
#   Penguin validates every input in real-time
# ============================================================

import sys, os, time, re, json, subprocess

# ── ANSI Colors ──────────────────────────────────────────────
R="\033[91m"; G="\033[92m"; Y="\033[93m"; B="\033[94m"
M="\033[95m"; C="\033[96m"; W="\033[97m"; DIM="\033[2m"
BOLD="\033[1m"; RESET="\033[0m"

if sys.platform == "win32":
    os.system("color")

def clear(): os.system("cls" if sys.platform == "win32" else "clear")

# ── PENGUIN ───────────────────────────────────────────────────
PENG = f"""
{W}   .---.
{W}  /{Y}o{W} {Y}o{W}\\   {C}PenguBot{RESET}
{W}  \\ w /   {DIM}by Sandip{RESET}
{W}   ---{RESET}"""

def penguin_say(msg, color=C, mood="normal"):
    moods = {
        "happy": f"{G}^w^{RESET}",
        "think": f"{C}~w~{RESET}",
        "warn":  f"{Y}>w<{RESET}",
        "error": f"{R}XwX{RESET}",
        "check": f"{G}*w*{RESET}",
        "normal":f"{W}OwO{RESET}",
    }
    face = moods.get(mood, moods["normal"])
    lines = msg.strip().split("\n")
    width = max(len(l) for l in lines) + 4
    print(f"\n{color}┌{'─'*width}┐{RESET}")
    for l in lines:
        pad = width - len(l) - 2
        print(f"{color}│ {W}{l}{' '*pad}{color} │{RESET}")
    print(f"{color}└{'─'*width}┘{RESET}")
    print(f"   {W}\\  {face} PenguBot says:{RESET}")
    print(PENG)

def section(n, title, subtitle=""):
    print(f"\n{C}{'═'*55}{RESET}")
    print(f"  {Y}[{n}/6]{RESET}  {BOLD}{W}{title}{RESET}")
    if subtitle: print(f"  {DIM}{subtitle}{RESET}")
    print(f"{C}{'═'*55}{RESET}\n")

def ok(m):   print(f"  {G}✔  {W}{m}{RESET}")
def err(m):  print(f"  {R}✘  {R}{m}{RESET}")
def info(m): print(f"  {C}➤  {DIM}{m}{RESET}")
def hint(m): print(f"  {Y}💡 {DIM}{m}{RESET}")

# ── VALIDATORS ────────────────────────────────────────────────

def validate_name(name):
    if len(name) < 2:
        return False, "Name too short. Enter at least 2 characters."
    if len(name) > 30:
        return False, "Name too long. Keep it under 30 characters."
    if any(c.isdigit() for c in name):
        return False, "Name should not contain numbers."
    return True, ""

def validate_groq_key(key):
    if not key.startswith("gsk_"):
        return False, (
            "❌ Invalid Groq API key format!\n\n"
            "Problem: Groq keys always start with 'gsk_'\n"
            "Your input: '" + key[:15] + "...'\n\n"
            "Fix:\n"
            "1. Go to https://console.groq.com\n"
            "2. Sign in → API Keys → Create new key\n"
            "3. Copy the full key starting with gsk_"
        )
    if len(key) < 40:
        return False, (
            "❌ Key too short!\n\n"
            "Groq keys are usually 50+ characters.\n"
            "Make sure you copied the full key."
        )
    return True, ""

def validate_telegram_token(token):
    parts = token.split(":")
    if len(parts) != 2:
        return False, (
            "❌ Invalid Telegram token format!\n\n"
            "Problem: Token must have format: 1234567890:ABCdef...\n"
            "It needs a colon (:) separating two parts.\n\n"
            "Fix:\n"
            "1. Open Telegram → search @BotFather\n"
            "2. Send /mybots → select your bot\n"
            "3. Click 'API Token' → copy the full token"
        )
    if not parts[0].isdigit():
        return False, (
            "❌ Token format wrong!\n\n"
            "The part before the colon must be numbers only.\n"
            "Example: 1234567890:ABCdefGHIjkl...\n\n"
            "Get correct token from @BotFather on Telegram."
        )
    if len(parts[1]) < 30:
        return False, (
            "❌ Token seems incomplete!\n\n"
            "Make sure you copied the complete token.\n"
            "It should be about 45 characters total."
        )
    return True, ""

def validate_user_id(uid):
    if not uid.isdigit():
        return False, (
            "❌ User ID must be numbers only!\n\n"
            "Problem: You entered non-numeric characters.\n\n"
            "Fix:\n"
            "1. Open Telegram → search @userinfobot\n"
            "2. Send /start\n"
            "3. It shows: 'Your ID: 1234567890'\n"
            "4. Copy only the numbers"
        )
    if len(uid) < 5 or len(uid) > 12:
        return False, (
            "❌ User ID length looks wrong!\n\n"
            "Telegram IDs are usually 9-10 digits.\n"
            "Get yours from @userinfobot on Telegram."
        )
    return True, ""

def validate_gmail(email):
    if not email:
        return True, ""  # optional
    if "@" not in email or "." not in email:
        return False, (
            "❌ Invalid email format!\n\n"
            "Email must contain @ and a domain.\n"
            "Example: yourname@gmail.com\n\n"
            "Or press ENTER to skip email setup."
        )
    if not email.endswith("@gmail.com"):
        return False, (
            "❌ Only Gmail is supported!\n\n"
            "Your email must end with @gmail.com\n"
            "Example: yourname@gmail.com\n\n"
            "Or press ENTER to skip."
        )
    return True, ""

def validate_app_password(pwd):
    clean = pwd.replace(" ", "")
    if len(clean) != 16:
        return False, (
            "❌ App Password must be 16 characters!\n\n"
            f"You entered {len(clean)} characters.\n\n"
            "Fix:\n"
            "1. Go to myaccount.google.com\n"
            "2. Security → 2-Step Verification → App Passwords\n"
            "3. Create new → copy the 16-char password\n"
            "Format: abcd efgh ijkl mnop"
        )
    return True, ""

def validate_city(city):
    if len(city) < 2:
        return False, "City name too short."
    if any(c.isdigit() for c in city):
        return False, "City name should not contain numbers."
    return True, ""

def validate_groq_key_live(key):
    """Actually test the Groq key with a real API call"""
    info("Testing your Groq API key with a real request...")
    try:
        import urllib.request, json
        data = json.dumps({
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": "say ok"}],
            "max_tokens": 5
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("choices"):
                return True, ""
    except Exception as e:
        errmsg = str(e)
        if "401" in errmsg or "invalid_api_key" in errmsg.lower():
            return False, (
                "❌ Groq API key is INVALID!\n\n"
                "This key was rejected by Groq servers.\n\n"
                "Fix:\n"
                "1. Go to https://console.groq.com\n"
                "2. Delete old key → Create new key\n"
                "3. Copy the complete new key"
            )
        elif "429" in errmsg:
            return True, ""  # rate limit = key is valid
        else:
            return False, (
                f"❌ Could not verify Groq key.\n\n"
                "Possible causes:\n"
                "• No internet connection\n"
                "• Groq servers temporarily down\n\n"
                "Try again or check your connection."
            )
    return False, "Verification failed. Try again."

def validate_telegram_token_live(token):
    """Test Telegram token with real API call"""
    info("Testing your Telegram Bot Token...")
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        req = urllib.request.Request(url)
        import urllib.request, json
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("ok"):
                bot_name = data["result"].get("username", "Unknown")
                return True, bot_name
    except Exception as e:
        errmsg = str(e)
        if "401" in errmsg or "Unauthorized" in errmsg:
            return False, (
                "❌ Telegram token is INVALID!\n\n"
                "This token was rejected by Telegram.\n\n"
                "Fix:\n"
                "1. Open Telegram → @BotFather\n"
                "2. Send /mybots → select your bot\n"
                "3. API Token → copy fresh token\n"
                "4. Make sure no spaces at start/end"
            )
        else:
            return False, (
                "❌ Could not verify Telegram token.\n\n"
                "Check your internet connection\n"
                "and try again."
            )
    return False, "Verification failed."

# ── ASK WITH VALIDATION ───────────────────────────────────────
import urllib.request

def smart_ask(prompt, validator, required=True, hint_text="", live_check=None):
    while True:
        if hint_text:
            print(f"  {DIM}{hint_text}{RESET}")
        val = input(f"  {Y}▶ {W}{prompt}: {C}").strip()

        if not val:
            if not required:
                return ""
            penguin_say("❌ This field is required!\nPlease enter a value.", color=R, mood="error")
            continue

        valid, msg = validator(val)
        if not valid:
            penguin_say(msg, color=R, mood="error")
            print(f"\n  {Y}Try again:{RESET}")
            continue

        # Live API check if provided
        if live_check:
            result = live_check(val)
            if isinstance(result, tuple) and len(result) == 2:
                live_ok, live_msg = result
            else:
                live_ok, live_msg = result, ""

            if not live_ok:
                penguin_say(live_msg, color=R, mood="error")
                print(f"\n  {Y}Try again:{RESET}")
                continue
            elif isinstance(live_msg, str) and live_msg and not live_msg.startswith("❌"):
                # Success with extra info (like bot username)
                penguin_say(f"✅ Verified! Bot username: @{live_msg}", color=G, mood="check")
                return val

        penguin_say(f"✅ Looks good!", color=G, mood="check")
        return val

# ── COLLECT INFO ──────────────────────────────────────────────
def collect_info():
    clear()
    print(f"\n{C}╔══════════════════════════════════════════════════╗")
    print(f"{C}║  {W}{BOLD} 🐧 Oracle Smart Setup Wizard v2.0          {RESET}{C}   ║")
    print(f"{C}║  {DIM}   Created by Sandip · I validate everything!{RESET}{C}  ║")
    print(f"{C}╚══════════════════════════════════════════════════╝{RESET}")

    penguin_say(
        "Welcome! I'm PenguBot 🐧\n"
        "I check every input you give me.\n"
        "Wrong key? I'll tell you exactly why.\n"
        "Let's set up your Oracle AI Bot!",
        mood="happy"
    )

    config = {}

    # ── 1. Name ──
    section(1, "Your Name", "What should Oracle call you?")
    hint("Must be 2-30 letters, no numbers")
    config["USER_NAME"] = smart_ask(
        "Your name (e.g. Alex)",
        validate_name,
        hint_text="→ Used in greetings and daily briefing"
    )

    # ── 2. Groq API Key ──
    section(2, "Groq API Key", "Free AI brain — get it from console.groq.com")
    penguin_say(
        "Getting your FREE Groq API key:\n"
        "1. Go to https://console.groq.com\n"
        "2. Sign up (free — no credit card)\n"
        "3. Click 'API Keys' → 'Create API Key'\n"
        "4. Copy the key starting with gsk_\n\n"
        "I will test it live to make sure it works!",
        mood="think"
    )
    config["GROQ_API_KEY"] = smart_ask(
        "Groq API Key",
        validate_groq_key,
        hint_text="→ Starts with: gsk_",
        live_check=validate_groq_key_live
    )

    # ── 3. Telegram Token ──
    section(3, "Telegram Bot Token", "Get from @BotFather on Telegram")
    penguin_say(
        "Getting your Telegram Bot Token:\n"
        "1. Open Telegram app\n"
        "2. Search: @BotFather\n"
        "3. Send: /newbot\n"
        "4. Enter a bot name (e.g. MyOracle)\n"
        "5. Enter username ending in 'bot'\n"
        "6. Copy the token BotFather gives you\n\n"
        "I will verify it live with Telegram!",
        mood="think"
    )
    config["TELEGRAM_TOKEN"] = smart_ask(
        "Telegram Bot Token",
        validate_telegram_token,
        hint_text="→ Format: 1234567890:ABCdefGHIjklMNOpqrSTUvwx",
        live_check=validate_telegram_token_live
    )

    # ── 4. User ID ──
    section(4, "Your Telegram User ID", "So bot only responds to you")
    penguin_say(
        "Getting your Telegram User ID:\n"
        "1. Open Telegram\n"
        "2. Search: @userinfobot\n"
        "3. Send: /start\n"
        "4. Copy the number next to 'Id:'\n\n"
        "This is a security lock —\n"
        "only YOU can control your bot!",
        mood="think"
    )
    config["MY_USER_ID"] = smart_ask(
        "Your Telegram User ID",
        validate_user_id,
        hint_text="→ Numbers only, e.g: 6148435580"
    )

    # ── 5. Gmail (optional) ──
    section(5, "Gmail (Optional)", "Press ENTER to skip email features")
    penguin_say(
        "Email setup is OPTIONAL.\n"
        "Press ENTER to skip both fields.\n\n"
        "If you want email features:\n"
        "• You need a Gmail App Password\n"
        "• Go to myaccount.google.com\n"
        "• Security → App Passwords → Create",
        mood="normal"
    )
    config["GMAIL_ADDRESS"] = smart_ask(
        "Gmail address (ENTER to skip)",
        validate_gmail,
        required=False,
        hint_text="→ yourname@gmail.com"
    )
    if config["GMAIL_ADDRESS"]:
        config["GMAIL_APP_PASS"] = smart_ask(
            "Gmail App Password",
            validate_app_password,
            hint_text="→ 16 chars: abcd efgh ijkl mnop"
        )
    else:
        config["GMAIL_APP_PASS"] = ""
        penguin_say("OK! Skipping email setup.\nYou can add it later.", mood="normal", color=Y)

    # ── 6. City ──
    section(6, "Your City", "For weather reports")
    config["USER_CITY"] = smart_ask(
        "Your city name",
        validate_city,
        hint_text="→ e.g. Mumbai, London, New York, Delhi"
    )

    return config

# ── PATCH FILES ───────────────────────────────────────────────
def patch_and_save(config):
    print(f"\n{C}{'═'*55}{RESET}")
    print(f"  {BOLD}{W}Applying your settings to bot files...{RESET}")
    print(f"{C}{'═'*55}{RESET}\n")

    replacements = {
        "YOUR_GROQ_API_KEY_HERE":    config["GROQ_API_KEY"],
        "YOUR_TELEGRAM_TOKEN_HERE":  config["TELEGRAM_TOKEN"],
        "YOUR_GMAIL_HERE":           config["GMAIL_ADDRESS"] or "",
        "YOUR_APP_PASSWORD_HERE":    config["GMAIL_APP_PASS"] or "",
        "YOUR_NAME_HERE":            config["USER_NAME"],
        "YOUR_CITY_HERE":            config["USER_CITY"],
        "0  # YOUR_USER_ID":         config["MY_USER_ID"],
    }

    files = [
        os.path.expanduser("~/MyTelegramAI/mybot.py"),
        os.path.expanduser("~/MyDesktopAI/deskagent.py"),
    ]

    for filepath in files:
        if not os.path.exists(filepath):
            print(f"  {Y}⚠ Not found: {filepath} — skipping{RESET}")
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        ok(f"Patched: {os.path.basename(filepath)}")

    # Save config
    config_path = os.path.expanduser("~/MyTelegramAI/config.py")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("# Oracle AI Bot Config — DO NOT share this file\n")
        for k, v in config.items():
            f.write(f'{k} = "{v}"\n')
    ok("Config saved securely")

# ── SUMMARY ───────────────────────────────────────────────────
def show_summary(config):
    clear()
    print(f"\n{G}╔══════════════════════════════════════════════════╗")
    print(f"{G}║  {W}{BOLD}  ✅ Setup Complete! Here's your config:     {RESET}{G}   ║")
    print(f"{G}╚══════════════════════════════════════════════════╝{RESET}\n")

    rows = [
        ("Name",   config["USER_NAME"]),
        ("Groq",   config["GROQ_API_KEY"][:16] + "..."),
        ("Token",  config["TELEGRAM_TOKEN"][:16] + "..."),
        ("UserID", config["MY_USER_ID"]),
        ("Gmail",  config["GMAIL_ADDRESS"] or "(skipped)"),
        ("City",   config["USER_CITY"]),
    ]
    for label, val in rows:
        print(f"  {C}{label:<8}{W}{val}{RESET}")

    print()
    penguin_say(
        f"All verified and saved, {config['USER_NAME']}! 🎉\n"
        "Every setting was checked by me.\n"
        "Your Oracle Bot is ready to launch!\n"
        "— PenguBot by Sandip ✦",
        color=G, mood="happy"
    )

# ── MAIN ─────────────────────────────────────────────────────
def main():
    try:
        config = collect_info()
        patch_and_save(config)
        show_summary(config)
    except KeyboardInterrupt:
        print(f"\n\n  {Y}Setup cancelled. Run install.py again.{RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
