#!/usr/bin/env python3
# ============================================================
#   ORACLE AI BOT — Telegram Bot
#   Created by Sandip | github.com/sandiprout747-tech
#   Template file — run install.py to personalize
# ============================================================

import telebot, os, sys, time, subprocess, datetime, threading
import requests, json, platform, psutil, re
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

# ── INIT ─────────────────────────────────────────────────────
bot    = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

DATA_DIR  = os.path.expanduser("~/MyDesktopAI/data")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
TODOS_FILE = os.path.join(DATA_DIR, "todos.json")
IDEAS_FILE = os.path.join(DATA_DIR, "ideas.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── AUTH ─────────────────────────────────────────────────────
def auth(msg):
    return msg.from_user.id == MY_USER_ID

def deny(msg):
    bot.send_message(msg.chat.id, "⛔ Unauthorized.")

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

# ── HANDLERS ─────────────────────────────────────────────────

@bot.message_handler(commands=["start", "status"])
def cmd_start(msg):
    if not auth(msg): return deny(msg)
    now = datetime.datetime.now().strftime("%d %b %Y · %H:%M")
    bot.send_message(msg.chat.id,
        f"🤖 *Oracle AI Bot*\n"
        f"👋 Hello, {USER_NAME}!\n"
        f"🕐 {now}\n\n"
        f"✅ Bot is online and ready.\n"
        f"Send /help to see all commands.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["help"])
def cmd_help(msg):
    if not auth(msg): return deny(msg)
    help_text = (
        "📋 *Oracle Commands*\n\n"
        "💬 *Chat*\n"
        "Just type anything — I'll reply with AI\n\n"
        "📁 *Files*\n"
        "/writefile `name content` — create a file\n"
        "/readfile `name` — read a file\n"
        "/listfiles — list all files\n\n"
        "📝 *Notes*\n"
        "/savenote `text` — save a note\n"
        "/notes — list all notes\n\n"
        "✅ *Todos*\n"
        "/todo `task` — add task\n"
        "/todos — list tasks\n"
        "/done `number` — complete task\n\n"
        "💡 *Ideas*\n"
        "/idea `text` — log an idea\n"
        "/ideas — list ideas\n\n"
        "🌤 *Utils*\n"
        "/weather — current weather\n"
        "/sysinfo — system stats\n"
        "/datetime — date and time\n"
        "/screenshot — take screenshot\n\n"
        "💻 *PC Control*\n"
        "/openapp `name` — open an app\n"
        "/runcmd `command` — run terminal command\n"
        "/lock — lock PC\n"
        "/volume `0-100` — set volume\n\n"
        "📧 *Email*\n"
        "/sendemail `to|subject|body`\n"
        "/lastemail — read last email\n\n"
        "⚡ /status — bot status\n"
        "🗑 /cleardone — clear completed todos"
    )
    bot.send_message(msg.chat.id, help_text, parse_mode="Markdown")

# ── NOTES ────────────────────────────────────────────────────
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
        bot.send_message(msg.chat.id, "📝 No notes yet.")
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
        bot.send_message(msg.chat.id, "✅ No todos yet.")
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
        todos[n]["done"] = True
        save_json(TODOS_FILE, todos)
        bot.send_message(msg.chat.id, f"☑ Marked done: {todos[n]['task']}")
    except:
        bot.send_message(msg.chat.id, "Usage: /done 1  (use number from /todos)")

@bot.message_handler(commands=["cleardone"])
def cmd_cleardone(msg):
    if not auth(msg): return deny(msg)
    todos = load_json(TODOS_FILE)
    todos = [t for t in todos if not t["done"]]
    save_json(TODOS_FILE, todos)
    bot.send_message(msg.chat.id, "🗑 Cleared all completed todos.")

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
        bot.send_message(msg.chat.id, "💡 No ideas yet.")
        return
    lines = [f"{i+1}. {d['idea']}" for i, d in enumerate(ideas)]
    bot.send_message(msg.chat.id, "💡 *Your Ideas:*\n\n" + "\n".join(lines), parse_mode="Markdown")

# ── FILES ─────────────────────────────────────────────────────
@bot.message_handler(commands=["writefile"])
def cmd_writefile(msg):
    if not auth(msg): return deny(msg)
    try:
        parts = msg.text.replace("/writefile", "").strip().split(" ", 1)
        name, content = parts[0], parts[1]
        path = os.path.expanduser(f"~/MyDesktopAI/data/{name}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        bot.send_message(msg.chat.id, f"📄 File saved: `{name}`", parse_mode="Markdown")
    except:
        bot.send_message(msg.chat.id, "Usage: /writefile filename.txt content here")

@bot.message_handler(commands=["readfile"])
def cmd_readfile(msg):
    if not auth(msg): return deny(msg)
    name = msg.text.replace("/readfile", "").strip()
    path = os.path.expanduser(f"~/MyDesktopAI/data/{name}")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        bot.send_message(msg.chat.id, f"📄 *{name}*\n\n{content}", parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, f"❌ File not found: {name}")

@bot.message_handler(commands=["listfiles"])
def cmd_listfiles(msg):
    if not auth(msg): return deny(msg)
    path = os.path.expanduser("~/MyDesktopAI/data/")
    files = os.listdir(path)
    if files:
        bot.send_message(msg.chat.id, "📁 *Files:*\n\n" + "\n".join(files), parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, "📁 No files yet.")

# ── SYSTEM ───────────────────────────────────────────────────
@bot.message_handler(commands=["sysinfo"])
def cmd_sysinfo(msg):
    if not auth(msg): return deny(msg)
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    info = (
        f"💻 *System Info*\n\n"
        f"🖥 OS: {platform.system()} {platform.release()}\n"
        f"⚙️ CPU: {cpu}%\n"
        f"🧠 RAM: {ram.percent}% ({ram.used//1024//1024}MB / {ram.total//1024//1024}MB)\n"
        f"💾 Disk: {disk.percent}% used\n"
        f"🐍 Python: {sys.version.split()[0]}"
    )
    bot.send_message(msg.chat.id, info, parse_mode="Markdown")

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
        url = f"https://wttr.in/{USER_CITY}?format=3"
        r = requests.get(url, timeout=5)
        bot.send_message(msg.chat.id, f"🌤 {r.text.strip()}")
    except:
        bot.send_message(msg.chat.id, "❌ Could not fetch weather. Check your internet.")

@bot.message_handler(commands=["screenshot"])
def cmd_screenshot(msg):
    if not auth(msg): return deny(msg)
    try:
        import pyautogui
        from PIL import Image
        path = os.path.expanduser("~/MyDesktopAI/data/screenshot.png")
        pyautogui.screenshot(path)
        with open(path, "rb") as f:
            bot.send_photo(msg.chat.id, f, caption="📸 Screenshot taken")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Screenshot failed: {e}")

# ── PC CONTROL ────────────────────────────────────────────────
@bot.message_handler(commands=["lock"])
def cmd_lock(msg):
    if not auth(msg): return deny(msg)
    import ctypes
    ctypes.windll.user32.LockWorkStation()
    bot.send_message(msg.chat.id, "🔒 PC Locked.")

# ── SMART APP MAP ─────────────────────────────────────────────
APP_MAP = {
    "chrome":     "start chrome",
    "firefox":    "start firefox",
    "edge":       "start msedge",
    "word":       "start winword",
    "excel":      "start excel",
    "powerpoint": "start powerpnt",
    "notepad":    "start notepad",
    "paint":      "start mspaint",
    "calculator": "start calc",
    "explorer":   "start explorer",
    "files":      "start explorer",
    "settings":   "start ms-settings:",
    "youtube":    "start https://youtube.com",
    "google":     "start https://google.com",
    "gmail":      "start https://mail.google.com",
    "whatsapp":   "start https://web.whatsapp.com",
    "github":     "start https://github.com",
    "maps":       "start https://maps.google.com",
    "translate":  "start https://translate.google.com",
    "chatgpt":    "start https://chat.openai.com",
    "netflix":    "start https://netflix.com",
    "spotify":    "start https://open.spotify.com",
}

@bot.message_handler(commands=["openapp"])
def cmd_openapp(msg):
    if not auth(msg): return deny(msg)
    app = msg.text.replace("/openapp", "").strip().lower()
    if not app:
        bot.send_message(msg.chat.id,
            "Usage: /openapp youtube\n\n"
            "Apps: chrome, firefox, edge, notepad, paint,\n"
            "      calculator, word, excel, explorer\n\n"
            "Sites: youtube, google, gmail, whatsapp,\n"
            "       github, maps, netflix, spotify"
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
        bot.send_message(msg.chat.id, f"❌ Failed to open {app}: {e}")

@bot.message_handler(commands=["runcmd"])
def cmd_runcmd(msg):
    if not auth(msg): return deny(msg)
    cmd = msg.text.replace("/runcmd", "").strip()
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout or result.stderr or "Done."
        bot.send_message(msg.chat.id, f"💻 `{cmd}`\n\n{output[:3000]}", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=["volume"])
def cmd_volume(msg):
    if not auth(msg): return deny(msg)
    try:
        level = int(msg.text.replace("/volume", "").strip())
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        bot.send_message(msg.chat.id, f"🔊 Volume set to {level}%")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Volume error: {e}")

# ── EMAIL ─────────────────────────────────────────────────────
@bot.message_handler(commands=["sendemail"])
def cmd_sendemail(msg):
    if not auth(msg): return deny(msg)
    if not GMAIL_ADDRESS or GMAIL_ADDRESS == "YOUR_GMAIL_HERE":
        bot.send_message(msg.chat.id, "❌ Gmail not configured. Re-run setup_wizard.py")
        return
    try:
        import smtplib
        from email.mime.text import MIMEText
        parts = msg.text.replace("/sendemail", "").strip().split("|")
        to, subject, body = parts[0].strip(), parts[1].strip(), parts[2].strip()
        m = MIMEText(body)
        m["Subject"] = subject
        m["From"] = GMAIL_ADDRESS
        m["To"] = to
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
        file_info = bot.get_file(msg.voice.file_id)
        downloaded = bot.download_file(file_info.file_path)
        oga_path = os.path.expanduser("~/MyDesktopAI/data/voice.oga")
        mp3_path = os.path.expanduser("~/MyDesktopAI/data/voice.mp3")
        with open(oga_path, "wb") as f:
            f.write(downloaded)
        os.rename(oga_path, mp3_path)
        with open(mp3_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model=VOICE_MODEL, file=f
            )
        text = transcription.text
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
        caption = msg.caption or "Describe this image in detail."
        file_info = bot.get_file(msg.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        import base64
        b64 = base64.b64encode(downloaded).decode("utf-8")
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
        reply = ask_ai(msg.text)
        bot.send_message(msg.chat.id, reply)
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ AI error: {e}")

# ── START ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🤖 Oracle Bot starting...")
    print(f"👤 Owner: {USER_NAME}")
    print(f"✅ Polling...")
    bot.infinity_polling()
