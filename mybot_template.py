#!/usr/bin/env python3
# ============================================================
#   ORACLE AI BOT — Telegram Bot v2.1
#   Created by Sandip | github.com/sandiprout747-tech
#   Template file — run install.py to personalize
# ============================================================

import telebot, os, sys, time, subprocess, datetime, threading
import requests, json, platform, psutil, re, shutil, ctypes
from groq import Groq

# ── CONFIG (auto-filled by setup_wizard.py) ──────────────────
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN_HERE"
MY_USER_ID     = 0  # YOUR_USER_ID
GROQ_API_KEY   = "YOUR_GROQ_API_KEY_HERE"
GMAIL_ADDRESS  = "YOUR_GMAIL_HERE"
GMAIL_APP_PASS = "YOUR_APP_PASSWORD_HERE"
USER_NAME      = "YOUR_NAME_HERE"
USER_CITY      = "YOUR_CITY_HERE"

# ── MODELS ───────────────────────────────────────────────────
PRIMARY_MODEL = "llama-3.1-8b-instant"
VISION_MODEL  = "meta-llama/llama-4-scout-17b-16e-instruct"
VOICE_MODEL   = "whisper-large-v3-turbo"

# ── PATHS ────────────────────────────────────────────────────
DATA_DIR   = os.path.expanduser("~/MyDesktopAI/data")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
TODOS_FILE = os.path.join(DATA_DIR, "todos.json")
IDEAS_FILE = os.path.join(DATA_DIR, "ideas.json")

# Desktop path — works for OneDrive and normal Desktop
def get_desktop():
    d1 = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    d2 = os.path.join(os.path.expanduser("~"), "Desktop")
    return d1 if os.path.exists(d1) else d2

os.makedirs(DATA_DIR, exist_ok=True)

# ── INIT ─────────────────────────────────────────────────────
bot    = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# ── HELPERS ──────────────────────────────────────────────────
def load_json(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def auth(msg):
    return msg.from_user.id == MY_USER_ID

def deny(msg):
    bot.send_message(msg.chat.id, "⛔ Unauthorized.")

def safe_reply(chat_id, text, **kwargs):
    try:
        bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error sending reply: {e}")

# ── AI CHAT ──────────────────────────────────────────────────
conversation_history = []

def ask_ai(user_msg):
    conversation_history.append({"role": "user", "content": user_msg})
    if len(conversation_history) > 20:
        conversation_history.pop(0)
    system = (
        f"You are Oracle, a smart personal AI assistant for {USER_NAME}. "
        f"Be concise, helpful, friendly. Today: {datetime.date.today()}. "
        f"User city: {USER_CITY}."
    )
    resp = client.chat.completions.create(
        model=PRIMARY_MODEL,
        messages=[{"role": "system", "content": system}] + conversation_history,
        max_tokens=800
    )
    reply = resp.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})
    return reply

# ══════════════════════════════════════════════════════════════
#   COMMANDS
# ══════════════════════════════════════════════════════════════

# ── START / STATUS ────────────────────────────────────────────
@bot.message_handler(commands=["start", "status"])
def cmd_start(msg):
    if not auth(msg): return deny(msg)
    now = datetime.datetime.now().strftime("%d %b %Y · %H:%M")
    bot.send_message(msg.chat.id,
        f"🤖 *Oracle AI Bot v2.1*\n"
        f"👋 Hello, {USER_NAME}!\n"
        f"🕐 {now}\n\n"
        f"✅ Bot is online and ready.\n"
        f"Send /help to see all commands.",
        parse_mode="Markdown"
    )

# ── HELP ──────────────────────────────────────────────────────
@bot.message_handler(commands=["help"])
def cmd_help(msg):
    if not auth(msg): return deny(msg)
    bot.send_message(msg.chat.id,
        "📋 *Oracle Commands*\n\n"
        "💬 *AI Chat*\n"
        "Just type anything — AI replies\n\n"
        "📁 *Files*\n"
        "/writefile `name.txt your content`\n"
        "/readfile `name.txt`\n"
        "/listfiles — list all saved files\n"
        "/deletefile `name.txt`\n\n"
        "📝 *Notes*\n"
        "/savenote `your note`\n"
        "/notes — view all notes\n\n"
        "✅ *Todos*\n"
        "/todo `task` — add task\n"
        "/todos — list tasks\n"
        "/done `number` — mark complete\n"
        "/cleardone — remove completed\n\n"
        "💡 *Ideas*\n"
        "/idea `your idea`\n"
        "/ideas — list all ideas\n\n"
        "🌤 *Utilities*\n"
        "/weather — current weather\n"
        "/sysinfo — CPU, RAM, disk\n"
        "/datetime — date and time\n\n"
        "📸 *Screenshot*\n"
        "/screenshot — capture screen\n\n"
        "💻 *PC Control*\n"
        "/openapp `name` — open app or website\n"
        "/runcmd `command` — run CMD command\n"
        "/volume `0-100` — set volume\n"
        "/lock — lock PC\n"
        "/shutdown — shutdown PC\n"
        "/restart — restart PC\n\n"
        "📧 *Email*\n"
        "/sendemail `to|subject|body`\n\n"
        "🎙 *Voice* — send voice message\n"
        "📷 *Vision* — send a photo\n\n"
        "⚡ /status — bot status",
        parse_mode="Markdown"
    )

# ── NOTES ─────────────────────────────────────────────────────
@bot.message_handler(commands=["savenote"])
def cmd_savenote(msg):
    if not auth(msg): return deny(msg)
    text = msg.text.replace("/savenote", "").strip()
    if not text:
        bot.send_message(msg.chat.id, "Usage: /savenote your note here")
        return
    notes = load_json(NOTES_FILE)
    notes.append({"text": text, "time": str(datetime.datetime.now())})
    save_json(NOTES_FILE, notes)
    bot.send_message(msg.chat.id, f"📝 Note saved!\n`{text}`", parse_mode="Markdown")

@bot.message_handler(commands=["notes"])
def cmd_notes(msg):
    if not auth(msg): return deny(msg)
    notes = load_json(NOTES_FILE)
    if not notes:
        bot.send_message(msg.chat.id, "📝 No notes yet. Use /savenote to add one.")
        return
    lines = [f"{i+1}. {n['text']}" for i, n in enumerate(notes)]
    bot.send_message(msg.chat.id, "📝 *Your Notes:*\n\n" + "\n".join(lines), parse_mode="Markdown")

# ── TODOS ─────────────────────────────────────────────────────
@bot.message_handler(commands=["todo"])
def cmd_todo(msg):
    if not auth(msg): return deny(msg)
    text = msg.text.replace("/todo", "").strip()
    if not text:
        bot.send_message(msg.chat.id, "Usage: /todo your task here")
        return
    todos = load_json(TODOS_FILE)
    todos.append({"task": text, "done": False, "time": str(datetime.datetime.now())})
    save_json(TODOS_FILE, todos)
    bot.send_message(msg.chat.id, f"✅ Todo added!\n`{text}`", parse_mode="Markdown")

@bot.message_handler(commands=["todos"])
def cmd_todos(msg):
    if not auth(msg): return deny(msg)
    todos = load_json(TODOS_FILE)
    if not todos:
        bot.send_message(msg.chat.id, "✅ No todos yet. Use /todo to add one.")
        return
    lines = []
    for i, t in enumerate(todos):
        icon = "☑" if t["done"] else "☐"
        lines.append(f"{icon} {i+1}. {t['task']}")
    bot.send_message(msg.chat.id, "✅ *Your Todos:*\n\n" + "\n".join(lines), parse_mode="Markdown")

@bot.message_handler(commands=["done"])
def cmd_done(msg):
    if not auth(msg): return deny(msg)
    try:
        n = int(msg.text.replace("/done", "").strip()) - 1
        todos = load_json(TODOS_FILE)
        if n < 0 or n >= len(todos):
            bot.send_message(msg.chat.id, f"❌ Invalid number. You have {len(todos)} todos.")
            return
        todos[n]["done"] = True
        save_json(TODOS_FILE, todos)
        bot.send_message(msg.chat.id, f"☑ Done: {todos[n]['task']}")
    except:
        bot.send_message(msg.chat.id, "Usage: /done 1  (number from /todos)")

@bot.message_handler(commands=["cleardone"])
def cmd_cleardone(msg):
    if not auth(msg): return deny(msg)
    todos = load_json(TODOS_FILE)
    before = len(todos)
    todos = [t for t in todos if not t["done"]]
    save_json(TODOS_FILE, todos)
    removed = before - len(todos)
    bot.send_message(msg.chat.id, f"🗑 Removed {removed} completed todo(s). {len(todos)} remaining.")

# ── IDEAS ─────────────────────────────────────────────────────
@bot.message_handler(commands=["idea"])
def cmd_idea(msg):
    if not auth(msg): return deny(msg)
    text = msg.text.replace("/idea", "").strip()
    if not text:
        bot.send_message(msg.chat.id, "Usage: /idea your idea here")
        return
    ideas = load_json(IDEAS_FILE)
    ideas.append({"idea": text, "time": str(datetime.datetime.now())})
    save_json(IDEAS_FILE, ideas)
    bot.send_message(msg.chat.id, f"💡 Idea logged!\n`{text}`", parse_mode="Markdown")

@bot.message_handler(commands=["ideas"])
def cmd_ideas(msg):
    if not auth(msg): return deny(msg)
    ideas = load_json(IDEAS_FILE)
    if not ideas:
        bot.send_message(msg.chat.id, "💡 No ideas yet. Use /idea to log one.")
        return
    lines = [f"{i+1}. {d['idea']}" for i, d in enumerate(ideas)]
    bot.send_message(msg.chat.id, "💡 *Your Ideas:*\n\n" + "\n".join(lines), parse_mode="Markdown")

# ── FILES ─────────────────────────────────────────────────────
@bot.message_handler(commands=["writefile"])
def cmd_writefile(msg):
    if not auth(msg): return deny(msg)
    try:
        parts = msg.text.replace("/writefile", "").strip().split(" ", 1)
        if len(parts) < 2:
            bot.send_message(msg.chat.id, "Usage: /writefile filename.txt your content here")
            return
        name, content = parts[0].strip(), parts[1].strip()
        # Save to Desktop AND data folder
        desktop_path = os.path.join(get_desktop(), name)
        data_path    = os.path.join(DATA_DIR, name)
        for path in [desktop_path, data_path]:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        bot.send_message(msg.chat.id,
            f"📄 File saved!\n"
            f"📍 Desktop: `{desktop_path}`\n"
            f"📍 Data: `{data_path}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Could not save file: {e}\nUsage: /writefile filename.txt content here")

@bot.message_handler(commands=["readfile"])
def cmd_readfile(msg):
    if not auth(msg): return deny(msg)
    name = msg.text.replace("/readfile", "").strip()
    if not name:
        bot.send_message(msg.chat.id, "Usage: /readfile filename.txt")
        return
    # Check both locations
    paths = [
        os.path.join(DATA_DIR, name),
        os.path.join(get_desktop(), name),
        os.path.expanduser(f"~/{name}"),
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if len(content) > 3500:
                    content = content[:3500] + "\n...(truncated)"
                bot.send_message(msg.chat.id, f"📄 *{name}*\n\n{content}", parse_mode="Markdown")
                return
            except Exception as e:
                bot.send_message(msg.chat.id, f"❌ Could not read file: {e}")
                return
    bot.send_message(msg.chat.id, f"❌ File not found: `{name}`\nUse /listfiles to see available files.", parse_mode="Markdown")

@bot.message_handler(commands=["listfiles"])
def cmd_listfiles(msg):
    if not auth(msg): return deny(msg)
    try:
        files = os.listdir(DATA_DIR)
        files = [f for f in files if not f.endswith(".json") and not f.endswith(".png")]
        if files:
            bot.send_message(msg.chat.id, "📁 *Saved Files:*\n\n" + "\n".join(files), parse_mode="Markdown")
        else:
            bot.send_message(msg.chat.id, "📁 No files yet. Use /writefile to create one.")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Error listing files: {e}")

@bot.message_handler(commands=["deletefile"])
def cmd_deletefile(msg):
    if not auth(msg): return deny(msg)
    name = msg.text.replace("/deletefile", "").strip()
    if not name:
        bot.send_message(msg.chat.id, "Usage: /deletefile filename.txt")
        return
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        os.remove(path)
        bot.send_message(msg.chat.id, f"🗑 Deleted: `{name}`", parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, f"❌ File not found: {name}")

# ── SYSTEM INFO ───────────────────────────────────────────────
@bot.message_handler(commands=["sysinfo"])
def cmd_sysinfo(msg):
    if not auth(msg): return deny(msg)
    try:
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        bot.send_message(msg.chat.id,
            f"💻 *System Info*\n\n"
            f"🖥 OS: {platform.system()} {platform.release()}\n"
            f"⚙️ CPU: {cpu}%\n"
            f"🧠 RAM: {ram.percent}% used "
            f"({ram.used//1024//1024}MB / {ram.total//1024//1024}MB)\n"
            f"💾 Disk: {disk.percent}% used "
            f"({disk.free//1024//1024//1024}GB free)\n"
            f"🐍 Python: {sys.version.split()[0]}",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ sysinfo error: {e}")

@bot.message_handler(commands=["datetime"])
def cmd_datetime(msg):
    if not auth(msg): return deny(msg)
    now = datetime.datetime.now()
    bot.send_message(msg.chat.id,
        f"🕐 *Date & Time*\n\n"
        f"📅 {now.strftime('%A, %d %B %Y')}\n"
        f"🕐 {now.strftime('%H:%M:%S')}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["weather"])
def cmd_weather(msg):
    if not auth(msg): return deny(msg)
    try:
        r = requests.get(f"https://wttr.in/{USER_CITY}?format=3", timeout=8)
        bot.send_message(msg.chat.id, f"🌤 {r.text.strip()}")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Weather unavailable: {e}")

# ── SCREENSHOT ────────────────────────────────────────────────
@bot.message_handler(commands=["screenshot"])
def cmd_screenshot(msg):
    if not auth(msg): return deny(msg)
    try:
        import pyautogui
        path = os.path.join(DATA_DIR, "screenshot.png")
        pyautogui.screenshot(path)
        with open(path, "rb") as f:
            bot.send_photo(msg.chat.id, f, caption="📸 Screenshot taken")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Screenshot failed: {e}")

# ── PC CONTROL ────────────────────────────────────────────────
@bot.message_handler(commands=["lock"])
def cmd_lock(msg):
    if not auth(msg): return deny(msg)
    try:
        ctypes.windll.user32.LockWorkStation()
        bot.send_message(msg.chat.id, "🔒 PC Locked.")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Lock failed: {e}")

@bot.message_handler(commands=["shutdown"])
def cmd_shutdown(msg):
    if not auth(msg): return deny(msg)
    bot.send_message(msg.chat.id, "🔴 Shutting down in 10 seconds...")
    subprocess.Popen("shutdown /s /t 10", shell=True)

@bot.message_handler(commands=["restart"])
def cmd_restart(msg):
    if not auth(msg): return deny(msg)
    bot.send_message(msg.chat.id, "🔄 Restarting in 10 seconds...")
    subprocess.Popen("shutdown /r /t 10", shell=True)

# ── APP MAP ───────────────────────────────────────────────────
APP_MAP = {
    "chrome":      "start chrome",
    "firefox":     "start firefox",
    "edge":        "start msedge",
    "word":        "start winword",
    "excel":       "start excel",
    "powerpoint":  "start powerpnt",
    "notepad":     "start notepad",
    "paint":       "start mspaint",
    "calculator":  "start calc",
    "explorer":    "start explorer",
    "files":       "start explorer",
    "settings":    "start ms-settings:",
    "camera":      "start microsoft.windows.camera:",
    "youtube":     "start https://youtube.com",
    "google":      "start https://google.com",
    "gmail":       "start https://mail.google.com",
    "whatsapp":    "start https://web.whatsapp.com",
    "github":      "start https://github.com",
    "maps":        "start https://maps.google.com",
    "translate":   "start https://translate.google.com",
    "chatgpt":     "start https://chat.openai.com",
    "netflix":     "start https://netflix.com",
    "spotify":     "start https://open.spotify.com",
    "instagram":   "start https://instagram.com",
    "twitter":     "start https://twitter.com",
    "facebook":    "start https://facebook.com",
    "linkedin":    "start https://linkedin.com",
}

@bot.message_handler(commands=["openapp"])
def cmd_openapp(msg):
    if not auth(msg): return deny(msg)
    app = msg.text.replace("/openapp", "").strip().lower()
    if not app:
        bot.send_message(msg.chat.id,
            "Usage: /openapp youtube\n\n"
            "💻 Apps: chrome, firefox, edge, notepad,\n"
            "  paint, calculator, word, excel, explorer\n\n"
            "🌐 Sites: youtube, google, gmail, whatsapp,\n"
            "  github, maps, netflix, spotify, instagram"
        )
        return
    try:
        if app in APP_MAP:
            cmd = APP_MAP[app]
        elif app.startswith("http://") or app.startswith("https://"):
            cmd = f"start {app}"
        elif "." in app and " " not in app:
            cmd = f"start https://{app}"
        else:
            cmd = f"start {app}"
        subprocess.Popen(cmd, shell=True)
        bot.send_message(msg.chat.id, f"🚀 Opening: {app}")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Failed: {e}")

@bot.message_handler(commands=["runcmd"])
def cmd_runcmd(msg):
    if not auth(msg): return deny(msg)
    cmd = msg.text.replace("/runcmd", "").strip()
    if not cmd:
        bot.send_message(msg.chat.id, "Usage: /runcmd ipconfig")
        return
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=15, encoding="utf-8", errors="ignore"
        )
        output = (result.stdout or result.stderr or "Done. No output.").strip()
        if len(output) > 3000:
            output = output[:3000] + "\n...(truncated)"
        bot.send_message(msg.chat.id, f"💻 `{cmd}`\n\n{output}", parse_mode="Markdown")
    except subprocess.TimeoutExpired:
        bot.send_message(msg.chat.id, "❌ Command timed out after 15 seconds.")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=["volume"])
def cmd_volume(msg):
    if not auth(msg): return deny(msg)
    try:
        level = int(msg.text.replace("/volume", "").strip())
        if not 0 <= level <= 100:
            bot.send_message(msg.chat.id, "❌ Volume must be between 0 and 100.")
            return
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL, CoInitialize
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        CoInitialize()
        devices  = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume   = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        bot.send_message(msg.chat.id, f"🔊 Volume set to {level}%")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Volume error: {e}")

# ── EMAIL ─────────────────────────────────────────────────────
@bot.message_handler(commands=["sendemail"])
def cmd_sendemail(msg):
    if not auth(msg): return deny(msg)
    if not GMAIL_ADDRESS or GMAIL_ADDRESS == "YOUR_GMAIL_HERE":
        bot.send_message(msg.chat.id,
            "❌ Gmail not configured.\n"
            "Run setup_wizard.py and enter your Gmail details."
        )
        return
    try:
        import smtplib
        from email.mime.text import MIMEText
        raw  = msg.text.replace("/sendemail", "").strip()
        parts = raw.split("|")
        if len(parts) < 3:
            bot.send_message(msg.chat.id, "Usage: /sendemail to@email.com|Subject|Message body")
            return
        to, subject, body = parts[0].strip(), parts[1].strip(), parts[2].strip()
        m = MIMEText(body)
        m["Subject"] = subject
        m["From"]    = GMAIL_ADDRESS
        m["To"]      = to
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            s.send_message(m)
        bot.send_message(msg.chat.id, f"📧 Email sent to {to}!")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Email failed: {e}")

# ── VOICE ─────────────────────────────────────────────────────
@bot.message_handler(content_types=["voice"])
def handle_voice(msg):
    if not auth(msg): return deny(msg)
    try:
        file_info  = bot.get_file(msg.voice.file_id)
        downloaded = bot.download_file(file_info.file_path)
        oga_path   = os.path.join(DATA_DIR, "voice.oga")
        mp3_path   = os.path.join(DATA_DIR, "voice.mp3")
        with open(oga_path, "wb") as f:
            f.write(downloaded)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
        os.rename(oga_path, mp3_path)
        with open(mp3_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model=VOICE_MODEL, file=f
            )
        text = transcription.text.strip()
        bot.send_message(msg.chat.id, f"🎙 *Heard:* {text}", parse_mode="Markdown")
        reply = ask_ai(text)
        bot.send_message(msg.chat.id, reply)
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Voice error: {e}")

# ── PHOTO / VISION ────────────────────────────────────────────
@bot.message_handler(content_types=["photo"])
def handle_photo(msg):
    if not auth(msg): return deny(msg)
    try:
        import base64
        caption    = msg.caption or "Describe this image in detail."
        file_info  = bot.get_file(msg.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        b64        = base64.b64encode(downloaded).decode("utf-8")
        resp = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": caption},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }],
            max_tokens=600
        )
        bot.send_message(msg.chat.id, resp.choices[0].message.content)
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Vision error: {e}")

# ── FREE TEXT → AI ────────────────────────────────────────────
@bot.message_handler(func=lambda m: True)
def handle_text(msg):
    if not auth(msg): return deny(msg)
    try:
        bot.send_chat_action(msg.chat.id, "typing")
        reply = ask_ai(msg.text)
        bot.send_message(msg.chat.id, reply)
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ AI error: {e}")

# ── START ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🤖 Oracle Bot v2.1 starting...")
    print(f"👤 Owner : {USER_NAME}")
    print(f"🌆 City  : {USER_CITY}")
    print(f"✅ Polling Telegram...")
    bot.infinity_polling()
