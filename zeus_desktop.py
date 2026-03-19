"""
⚡ ZEUS Desktop — Zero Effort Universal System
Full voice assistant with system control, AI chat, and all web features.
"""

import os
import sys
import json
import time
import random
import string
import threading
import subprocess
import platform
import datetime
import webbrowser
import glob
import shutil
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from same folder as this script
_here = Path(__file__).parent
load_dotenv(dotenv_path=str(_here / ".env"))

# ── API Keys ─────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NEWS_API_KEY  = os.getenv("NEWS_API_KEY", "")
print(f"[ZEUS] GROQ key loaded: {bool(GROQ_API_KEY)}, NEWS key: {bool(NEWS_API_KEY)}")

# ── Optional imports (graceful fallback) ─────────────────────────────────────
try:
    import pyttsx3
    _test = pyttsx3.init()
    _test.stop()
    TTS_OK = True
except Exception:
    TTS_OK = False

try:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.pause_threshold  = 0.8
    MIC_OK = True
except Exception:
    MIC_OK = False

try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    GROQ_OK = bool(GROQ_API_KEY)
except Exception:
    groq_client = None
    GROQ_OK = False

try:
    import requests
    NET_OK = True
except Exception:
    NET_OK = False

try:
    import pyjokes
    JOKES_OK = True
except Exception:
    JOKES_OK = False

try:
    import pyautogui
    import pyperclip
    GUI_OK = True
except Exception:
    GUI_OK = False

try:
    import yfinance as yf
    YFINANCE_OK = True
except Exception:
    YFINANCE_OK = False

try:
    import wikipedia
    WIKI_OK = True
except Exception:
    WIKI_OK = False

# ── Personality ───────────────────────────────────────────────────────────────
PERSONALITY = "Friendly"
PERSONALITY_PROMPTS = {
    "Friendly":      "You are ZEUS, a friendly helpful voice assistant. Keep replies SHORT and conversational — 1-3 sentences max unless detail is asked. No markdown, plain text only.",
    "Professional":  "You are ZEUS, a professional voice assistant. Be concise, formal and precise. Plain text only.",
    "Sarcastic":     "You are ZEUS, witty and sarcastic but still helpful. Short punchy replies. Plain text only.",
    "Motivational":  "You are ZEUS, an inspiring motivational coach. Short energetic replies. Plain text only.",
    "Teacher":       "You are ZEUS, an educational assistant. Explain clearly but briefly. Plain text only.",
}

# ── Chat history ──────────────────────────────────────────────────────────────
chat_history = []       # list of {"role": ..., "content": ...}
notes_store  = []
todos_store  = []

# ── TTS ───────────────────────────────────────────────────────────────────────
# Run pyttsx3 in a separate subprocess so stopping never affects tkinter
_speak_proc = None
_stop_flag = threading.Event()
CURRENT_VOICE_INDEX = 0

_TTS_SCRIPT = """
import sys, pyttsx3
text = sys.argv[1]
voice_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
engine = pyttsx3.init()
engine.setProperty('rate', 155)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
if voices and voice_index < len(voices):
    engine.setProperty('voice', voices[voice_index].id)
engine.say(text)
engine.runAndWait()
"""

def get_available_voices():
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = [(i, v.name) for i, v in enumerate(engine.getProperty('voices'))]
        engine.stop()
        return voices
    except Exception:
        return []

def speak(text: str):
    """Speak in a fully isolated subprocess — killing it is instant and safe."""
    print(f"ZEUS: {text}")
    if not TTS_OK:
        return
    _stop_flag.clear()
    def _do():
        global _speak_proc
        try:
            import tempfile, sys
            # Write TTS script to temp file
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py',
                                              delete=False, encoding='utf-8')
            tmp.write(_TTS_SCRIPT)
            tmp.close()
            # Run as subprocess
            proc = subprocess.Popen(
                [sys.executable, tmp.name, text, str(CURRENT_VOICE_INDEX)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            _speak_proc = proc
            proc.wait()
            _speak_proc = None
            import os as _os
            try: _os.unlink(tmp.name)
            except: pass
        except Exception as e:
            print(f"TTS error: {e}")
            _speak_proc = None
    threading.Thread(target=_do, daemon=True).start()

def stop_speaking():
    """Kill the TTS subprocess instantly — zero crash risk."""
    _stop_flag.set()
    global _speak_proc
    p = _speak_proc
    if p:
        try:
            p.kill()
        except Exception:
            pass
        _speak_proc = None

# ── STT ───────────────────────────────────────────────────────────────────────
def listen(timeout=5, phrase_limit=10) -> str:
    """Listen from microphone and return recognized text, or ''."""
    if not MIC_OK:
        return input("You (type): ").strip()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text.lower()
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        return ""

# ── Wake word listener ────────────────────────────────────────────────────────
def wake_word_loop(callback, stop_event: threading.Event):
    """Continuously listen for 'hey zeus' and call callback()."""
    if not MIC_OK:
        return
    while not stop_event.is_set():
        text = listen(timeout=3, phrase_limit=4)
        if text and ("zeus" in text):
            # Strip wake phrase, only pass actual command if present
            command = text.replace("hey zeus", "").replace("zeus", "").strip()
            callback(command)

# ── AI brain ──────────────────────────────────────────────────────────────────
def ask_zeus(prompt: str, system_override: str = None) -> str:
    if not GROQ_OK:
        return "I need an internet connection and Groq API key for AI responses."
    try:
        sys_msg = system_override or PERSONALITY_PROMPTS.get(PERSONALITY, PERSONALITY_PROMPTS["Friendly"])
        messages = [{"role": "system", "content": sys_msg}]
        # Include last 6 turns for context
        messages += chat_history[-6:]
        messages.append({"role": "user", "content": prompt})
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=400,
        )
        answer = resp.choices[0].message.content.strip()
        chat_history.append({"role": "user",      "content": prompt})
        chat_history.append({"role": "assistant",  "content": answer})
        return answer
    except Exception as e:
        return f"AI error: {e}"

# ── Weather ───────────────────────────────────────────────────────────────────
def get_weather(city: str) -> str:
    try:
        try:
            geo = requests.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json",
                timeout=8).json()
        except Exception:
            geo = requests.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json",
                timeout=8, verify=False).json()
        if not geo.get('results'):
            return f"City {city} not found."
        r = geo['results'][0]
        lat, lon, name, country = r['latitude'], r['longitude'], r['name'], r.get('country','')
        try:
            w = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,windspeed_10m,weathercode"
                f"&timezone=auto", timeout=8).json()
        except Exception:
            w = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,windspeed_10m,weathercode"
                f"&timezone=auto", timeout=8, verify=False).json()
        c = w['current']
        codes = {0:"clear sky",1:"mainly clear",2:"partly cloudy",3:"overcast",
                 45:"foggy",51:"light drizzle",61:"rain",71:"snow",80:"showers",95:"thunderstorm"}
        cond = codes.get(c.get('weathercode',0), "clear")
        return (f"Weather in {name}, {country}: {c['temperature_2m']}°C, {cond}. "
                f"Humidity {c['relative_humidity_2m']}%, wind {c['windspeed_10m']} km/h.")
    except Exception as e:
        return f"Weather error: {e}"

# ── News ──────────────────────────────────────────────────────────────────────
def get_news(category="general", country="in", count=5) -> str:
    try:
        count = min(count, 10)

        if country == "in":
            # India news via everything endpoint with india query — most reliable on free tier
            url = (f"https://newsapi.org/v2/everything"
                   f"?q=india&language=en&sortBy=publishedAt"
                   f"&pageSize=15&apiKey={NEWS_API_KEY}")
            label = "India"
            data = requests.get(url, timeout=8).json()
            articles = data.get('articles', [])
        else:
            # Global/US news
            url = (f"https://newsapi.org/v2/top-headlines"
                   f"?language=en&pageSize={count}&apiKey={NEWS_API_KEY}")
            if category != "general":
                url += f"&category={category}"
            label = "Global"
            data = requests.get(url, timeout=8).json()
            articles = data.get('articles', [])

        if not articles:
            return "No news found right now."

        headlines = []
        for a in articles:
            title = a.get('title', '').split(' - ')[0].strip()
            source = a.get('source', {}).get('name', '')
            # Skip blank, removed, or generic Google News placeholders
            if not title or title == '[Removed]' or title.lower() == 'google news':
                continue
            headlines.append(f"{len(headlines)+1}. {title} ({source})")
            if len(headlines) >= count:
                break

        if not headlines:
            return "No news found right now."

        return f"Here are the latest {label} headlines. " + ". ".join(headlines)
    except Exception as e:
        return f"News error: {e}"

# ── Stocks ────────────────────────────────────────────────────────────────────
def get_stock(symbol: str) -> str:
    if not YFINANCE_OK:
        return "yfinance not installed."
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        price  = round(info.last_price, 2)
        change = round(info.last_price - info.previous_close, 2)
        pct    = round(change / info.previous_close * 100, 2)
        direction = "up" if change >= 0 else "down"
        return f"{symbol.upper()} is trading at {price} dollars, {direction} {abs(change)} or {abs(pct)}% today."
    except Exception as e:
        return f"Stock error: {e}"

# ── Currency ──────────────────────────────────────────────────────────────────
def convert_currency(amount: float, frm: str, to: str) -> str:
    try:
        r = requests.get(f"https://api.exchangerate-api.com/v4/latest/{frm.upper()}", timeout=8).json()
        rate = r['rates'][to.upper()]
        result = round(amount * rate, 2)
        return f"{amount} {frm.upper()} equals {result} {to.upper()}."
    except Exception as e:
        return f"Currency error: {e}"

# ── Wikipedia ─────────────────────────────────────────────────────────────────
def search_wikipedia(query: str) -> str:
    if not WIKI_OK:
        return ask_zeus(query)
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except Exception:
        return ask_zeus(query)

# ── Jokes ─────────────────────────────────────────────────────────────────────
def tell_joke() -> str:
    if JOKES_OK:
        return pyjokes.get_joke()
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
        "Why did the AI cross the road? To optimize the chicken's path.",
    ]
    return random.choice(jokes)

# ── Password ──────────────────────────────────────────────────────────────────
def generate_password(length=16) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = ''.join(random.choice(chars) for _ in range(length))
    return f"Your new password is: {pwd}"

# ── System control ────────────────────────────────────────────────────────────
SYSTEM = platform.system()   # 'Windows', 'Darwin', 'Linux'

APP_MAP = {
    "notepad":         "notepad.exe",
    "calculator":      "calc.exe",
    "paint":           "mspaint.exe",
    "explorer":        "explorer.exe",
    "file explorer":   "explorer.exe",
    "task manager":    "taskmgr.exe",
    "cmd":             "cmd.exe",
    "command prompt":  "cmd.exe",
    "powershell":      "powershell.exe",
    "vs code":         "code",
    "vscode":          "code",
    "chrome":          "chrome.exe",
    "google chrome":   "chrome.exe",
    "firefox":         "firefox.exe",
    "vlc":             "vlc.exe",
    "word":            "winword.exe",
    "excel":           "excel.exe",
    "powerpoint":      "powerpnt.exe",
}

# Known UWP app IDs — corrected
UWP_MAP = {
    "whatsapp":  ("5319275A.WhatsAppDesktop_cv1g1gvanyjgm", "WhatsAppDesktop"),
    "telegram":  ("TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm", "Telegram"),
    "spotify":   ("SpotifyAB.SpotifyMusic_zpdnekdrzrea0", "Spotify"),
    "netflix":   ("4DF9E0F8.Netflix_mcm4njqhnhss8", "App"),
    "instagram": ("Facebook.Instagram_8xx8rvfyw5nnt", "Instagram"),
    "facebook":  ("Facebook.Facebook_8xx8rvfyw5nnt", "Facebook"),
    "twitter":   ("Twitter.Twitter_8xx8rvfyw5nnt", "Twitter"),
    "x":         ("Twitter.Twitter_8xx8rvfyw5nnt", "Twitter"),
    "zoom":      ("Zoom.Zoom_d3b5apdbfhgpj", "Zoom"),
    "teams":     ("MicrosoftTeams_8wekyb3d8bbwe", "Teams"),
    "microsoft teams": ("MicrosoftTeams_8wekyb3d8bbwe", "Teams"),
    "xbox":      ("Microsoft.XboxApp_8wekyb3d8bbwe", "App"),
    "photos":    ("Microsoft.Windows.Photos_8wekyb3d8bbwe", "App"),
    "camera":    ("Microsoft.WindowsCamera_8wekyb3d8bbwe", "App"),
    "mail":      ("microsoft.windowscommunicationsapps_8wekyb3d8bbwe", "ppleae38afbc22005"),
    "maps":      ("Microsoft.WindowsMaps_8wekyb3d8bbwe", "App"),
    "weather":   ("Microsoft.BingWeather_8wekyb3d8bbwe", "App"),
}

def open_app(app_name: str) -> str:
    name = app_name.lower().strip()
    for filler in [" app", " application", " software", " program"]:
        name = name.replace(filler, "")
    name = name.strip()

    # 1. Simple built-in Windows tools
    builtin = {
        "notepad": "notepad.exe", "calculator": "calc.exe",
        "paint": "mspaint.exe", "explorer": "explorer.exe",
        "file explorer": "explorer.exe", "task manager": "taskmgr.exe",
        "cmd": "cmd.exe", "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
    }
    for key, exe in builtin.items():
        if key in name:
            subprocess.Popen(exe)
            return f"Opening {key}."

    # 2. PowerShell Start-Process for installed desktop apps
    ps_map = {
        "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
        "vscode": "code", "vs code": "code", "chrome": "chrome",
        "google chrome": "chrome", "firefox": "firefox", "vlc": "vlc",
        "spotify": "spotify", "discord": "discord", "zoom": "zoom",
        "edge": "msedge", "microsoft edge": "msedge",
        "onenote": "onenote", "outlook": "outlook",
    }
    proc_name = ps_map.get(name, name.replace(" ", ""))
    try:
        result = subprocess.run(
            ["powershell", "-command", f"Start-Process '{proc_name}'"],
            capture_output=True, text=True, timeout=8
        )
        if result.returncode == 0:
            return f"Opening {app_name}."
    except Exception:
        pass

    # 3. UWP Store apps — use Start-Process with shell URI (most reliable)
    uwp_uris = {
        "whatsapp":  "whatsapp:",
        "telegram":  "shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram",
        "teams":     "msteams:",
        "xbox":      "xbox:",
        "photos":    "ms-photos:",
        "camera":    "microsoft.windows.camera:",
        "maps":      "bingmaps:",
        "mail":      "mailto:",
        "calendar":  "outlookcal:",
    }
    for key, uri in uwp_uris.items():
        if key in name:
            try:
                subprocess.Popen(["powershell", "-command", f"Start-Process '{uri}'"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Opening {key.capitalize()}."
            except Exception:
                pass

    # 4. UWP via PackageFamilyName
    for key, (family, app_id) in UWP_MAP.items():
        if key in name or name in key:
            try:
                subprocess.Popen(
                    ["powershell", "-command",
                     f"Start-Process 'shell:AppsFolder\\{family}!{app_id}'"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return f"Opening {key.capitalize()}."
            except Exception as e:
                print(f"UWP error for {key}: {e}")

    # 5. Dynamic PowerShell UWP lookup
    try:
        result = subprocess.run(
            ["powershell", "-command",
             f"(Get-AppxPackage *{name}* | Select-Object -First 1).PackageFamilyName"],
            capture_output=True, text=True, timeout=6
        )
        family = result.stdout.strip()
        if family and len(family) > 5:
            subprocess.Popen(
                ["powershell", "-command",
                 f"Start-Process 'shell:AppsFolder\\{family}!App'"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return f"Opening {name.capitalize()}."
    except Exception:
        pass

    # 6. Search Program Files
    for base in [Path("C:/Program Files"), Path("C:/Program Files (x86)"),
                 Path.home() / "AppData" / "Local",
                 Path.home() / "AppData" / "Roaming"]:
        if not base.exists():
            continue
        try:
            for m in list(base.rglob(f"*{name}*.exe"))[:5]:
                skip = ["uninstall", "update", "crash", "squirrel", "setup", "install"]
                if any(s in m.name.lower() for s in skip):
                    continue
                try:
                    subprocess.Popen([str(m)])
                    return f"Opening {m.stem}."
                except Exception:
                    continue
        except Exception:
            continue

    return f"Could not find {app_name}. Make sure it is installed on this PC."

def create_folder(folder_name: str, location: str = None) -> str:
    base = location or str(Path.home() / "Desktop")
    path = os.path.join(base, folder_name)
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder '{folder_name}' created on your Desktop."
    except Exception as e:
        return f"Could not create folder: {e}"

def create_file(filename: str, location: str = None) -> str:
    base = location or str(Path.home() / "Desktop")
    path = os.path.join(base, filename)
    try:
        with open(path, 'w') as f:
            f.write("")
        return f"File '{filename}' created on your Desktop."
    except Exception as e:
        return f"Could not create file: {e}"

def take_screenshot() -> str:
    if not GUI_OK:
        return "pyautogui not installed. Run: pip install pyautogui"
    try:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Try Desktop first, fall back to Documents, then script folder
        for folder in [
            Path.home() / "Desktop",
            Path.home() / "OneDrive" / "Desktop",
            Path.home() / "Documents",
            _here,
        ]:
            if folder.exists():
                path = str(folder / f"screenshot_{ts}.png")
                pyautogui.screenshot(path)
                return f"Screenshot saved to {path}"
        return "Could not find a valid save location for screenshot."
    except Exception as e:
        return f"Screenshot error: {e}"

def control_volume(action: str) -> str:
    try:
        if SYSTEM == "Windows":
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if action == "up":
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
            elif action == "down":
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
            elif action == "mute":
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        elif SYSTEM == "Darwin":
            if action == "up":   os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")
            elif action == "down": os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")
            elif action == "mute": os.system("osascript -e 'set volume with output muted'")
        else:
            if action == "up":   os.system("amixer -q sset Master 10%+")
            elif action == "down": os.system("amixer -q sset Master 10%-")
            elif action == "mute": os.system("amixer -q sset Master toggle")
        return f"Volume {action}."
    except Exception as e:
        return f"Volume error: {e}"

def lock_computer() -> str:
    try:
        if SYSTEM == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif SYSTEM == "Darwin":
            os.system("pmset displaysleepnow")
        else:
            os.system("gnome-screensaver-command -l")
        return "Computer locked."
    except Exception as e:
        return f"Lock error: {e}"

def shutdown_computer(restart=False) -> str:
    action = "restart" if restart else "shutdown"
    speak(f"Initiating {action} in 5 seconds.")
    time.sleep(5)
    try:
        if SYSTEM == "Windows":
            cmd = "shutdown /r /t 0" if restart else "shutdown /s /t 0"
        elif SYSTEM == "Darwin":
            cmd = "sudo shutdown -r now" if restart else "sudo shutdown -h now"
        else:
            cmd = "sudo reboot" if restart else "sudo poweroff"
        os.system(cmd)
        return f"{action.capitalize()} initiated."
    except Exception as e:
        return f"{action.capitalize()} error: {e}"

def type_text(text: str) -> str:
    if not GUI_OK:
        return "pyautogui not installed."
    try:
        time.sleep(1)
        pyautogui.typewrite(text, interval=0.05)
        return f"Typed: {text}"
    except Exception as e:
        return f"Type error: {e}"

def search_files(query: str) -> str:
    home = Path.home()
    results = list(home.rglob(f"*{query}*"))[:5]
    if not results:
        return f"No files matching '{query}' found in your home directory."
    return "Found: " + ", ".join(str(p) for p in results)

def get_clipboard() -> str:
    if not GUI_OK:
        return "pyperclip not installed."
    try:
        content = pyperclip.paste()
        return f"Clipboard contains: {content[:200]}"
    except Exception as e:
        return f"Clipboard error: {e}"

def set_clipboard(text: str) -> str:
    if not GUI_OK:
        return "pyperclip not installed."
    try:
        pyperclip.copy(text)
        return "Copied to clipboard."
    except Exception as e:
        return f"Clipboard error: {e}"

def search_web(query: str) -> str:
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    return f"Searching Google for: {query}"

def play_music() -> str:
    music_dirs = [
        Path.home() / "Music",
        Path.home() / "Downloads",
        Path.home() / "Desktop",
    ]
    for d in music_dirs:
        files = list(d.glob("*.mp3")) + list(d.glob("*.wav")) + list(d.glob("*.flac"))
        if files:
            f = random.choice(files)
            if SYSTEM == "Windows":
                os.startfile(str(f))
            elif SYSTEM == "Darwin":
                os.system(f'open "{f}"')
            else:
                os.system(f'xdg-open "{f}"')
            return f"Playing {f.name}"
    return "No music files found. Opening YouTube Music."

def get_time_date() -> str:
    now = datetime.datetime.now()
    return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d %Y')}."

# ── Notes & Todos ─────────────────────────────────────────────────────────────
def add_note(note: str) -> str:
    notes_store.append({"text": note, "time": datetime.datetime.now().strftime("%H:%M")})
    return f"Note saved: {note}"

def list_notes() -> str:
    if not notes_store:
        return "You have no notes."
    return "Your notes: " + ". ".join(f"{i+1}. {n['text']}" for i, n in enumerate(notes_store))

def add_todo(task: str) -> str:
    todos_store.append({"task": task, "done": False})
    return f"Added to your todo list: {task}"

def list_todos() -> str:
    pending = [t for t in todos_store if not t['done']]
    if not pending:
        return "Your todo list is empty."
    return "Your todos: " + ". ".join(f"{i+1}. {t['task']}" for i, t in enumerate(pending))

# ── Command parser ────────────────────────────────────────────────────────────
def parse_and_execute(text: str) -> str:
    t = text.lower().strip()

    # ── Time / Date ───────────────────────────────────────────────────────────
    if any(w in t for w in ["what time", "what's the time", "current time", "what date", "today's date"]):
        return get_time_date()

    # ── Weather ───────────────────────────────────────────────────────────────
    if "weather" in t:
        for prep in ["in ", "for ", "at "]:
            if prep in t:
                city = t.split(prep, 1)[-1].strip().split()[0]
                return get_weather(city)
        return get_weather("Pune")

    # ── News ──────────────────────────────────────────────────────────────────
    if "news" in t:
        # Detect count (e.g. "top 10 news", "5 news")
        count = 5
        import re as _re
        nums = _re.findall(r'\b(\d+)\b', t)
        if nums:
            count = min(int(nums[0]), 10)
        # Detect country
        if any(w in t for w in ["global","world","international","worldwide"]):
            country = "global"
        elif any(w in t for w in ["us ","usa","america","american"]):
            country = "us"
        elif any(w in t for w in ["uk","britain","british","england"]):
            country = "gb"
        else:
            country = "in"   # default India
        # Detect category
        cat = "general"
        for c in ["technology","tech","sports","business","entertainment","health","science"]:
            if c in t:
                cat = c if c != "tech" else "technology"
                break
        return get_news(cat, country, count)

    # ── Stock ─────────────────────────────────────────────────────────────────
    if "stock" in t or "share price" in t:
        words = t.split()
        for w in words:
            if w.upper() in ["AAPL","TSLA","GOOGL","MSFT","AMZN","META","NFLX","NVDA","RELIANCE","TCS","INFY"]:
                return get_stock(w)
        return ask_zeus(text)

    # ── Currency ──────────────────────────────────────────────────────────────
    if "convert" in t and ("usd" in t or "inr" in t or "eur" in t or "rupee" in t or "dollar" in t):
        words = t.split()
        try:
            amt  = float(next(w for w in words if w.replace('.','').isdigit()))
            currencies = [w.upper() for w in words if w.upper() in ["USD","INR","EUR","GBP","JPY","AUD","CAD"]]
            if len(currencies) >= 2:
                return convert_currency(amt, currencies[0], currencies[1])
        except Exception:
            pass
        return ask_zeus(text)

    # ── Joke ──────────────────────────────────────────────────────────────────
    if any(w in t for w in ["joke","jokes","funny","make me laugh","tell me a joke"]):
        return tell_joke()

    # ── Password ──────────────────────────────────────────────────────────────
    if "password" in t and ("generate" in t or "create" in t or "new" in t):
        return generate_password()

    # ── Wikipedia ─────────────────────────────────────────────────────────────
    if t.startswith("who is") or t.startswith("what is") or t.startswith("tell me about"):
        topic = t.replace("who is","").replace("what is","").replace("tell me about","").strip()
        return search_wikipedia(topic)

    # ── Open app ──────────────────────────────────────────────────────────────
    if t.startswith("open "):
        app = t.replace("open ", "", 1).strip()
        return open_app(app)

    # ── Create folder ─────────────────────────────────────────────────────────
    if "create folder" in t or "make folder" in t or "new folder" in t:
        name = t.replace("create folder","").replace("make folder","").replace("new folder","").strip()
        name = name or "New Folder"
        return create_folder(name)

    # ── Create file ───────────────────────────────────────────────────────────
    if "create file" in t or "new file" in t or "make file" in t:
        name = t.replace("create file","").replace("new file","").replace("make file","").strip()
        name = name or "new_file.txt"
        return create_file(name)

    # ── Screenshot ────────────────────────────────────────────────────────────
    if "screenshot" in t or "take a screenshot" in t or "capture screen" in t:
        return take_screenshot()

    # ── Volume ────────────────────────────────────────────────────────────────
    if "volume up" in t or "increase volume" in t or "louder" in t:
        return control_volume("up")
    if "volume down" in t or "decrease volume" in t or "quieter" in t or "lower volume" in t:
        return control_volume("down")
    if "mute" in t:
        return control_volume("mute")

    # ── Lock ──────────────────────────────────────────────────────────────────
    if "lock" in t and ("computer" in t or "screen" in t or "pc" in t):
        return lock_computer()

    # ── Shutdown / Restart ────────────────────────────────────────────────────
    if "shutdown" in t or "shut down" in t:
        return shutdown_computer(restart=False)
    if "restart" in t or "reboot" in t:
        return shutdown_computer(restart=True)

    # ── Type text ─────────────────────────────────────────────────────────────
    if t.startswith("type "):
        content = t.replace("type ", "", 1)
        return type_text(content)

    # ── Search files ──────────────────────────────────────────────────────────
    if "find file" in t or "search file" in t or "locate file" in t:
        query = t.replace("find file","").replace("search file","").replace("locate file","").strip()
        return search_files(query)

    # ── Clipboard ─────────────────────────────────────────────────────────────
    if "clipboard" in t or "what did i copy" in t:
        return get_clipboard()
    if t.startswith("copy "):
        return set_clipboard(t.replace("copy ", "", 1))

    # ── Music ─────────────────────────────────────────────────────────────────
    if "play music" in t or "play song" in t or "play my playlist" in t or "play something" in t:
        return play_music()

    # ── Web search ────────────────────────────────────────────────────────────
    if t.startswith("search") or t.startswith("google"):
        query = t
        for filler in ["search the web for", "search the web", "search for",
                       "search google for", "search google", "search", "google"]:
            if query.startswith(filler):
                query = query[len(filler):].strip()
                break
        if query:
            return search_web(query)
        return "What would you like me to search for?"

    # ── Notes ─────────────────────────────────────────────────────────────────
    if "note" in t and ("add" in t or "save" in t or "remember" in t):
        content = t.replace("add note","").replace("save note","").replace("remember","").strip()
        return add_note(content)
    if "my notes" in t or "show notes" in t or "list notes" in t:
        return list_notes()

    # ── Todos ─────────────────────────────────────────────────────────────────
    if "add todo" in t or "add task" in t:
        task = t.replace("add todo","").replace("add task","").strip()
        return add_todo(task)
    if "my todos" in t or "my tasks" in t or "show tasks" in t:
        return list_todos()

    # ── Greetings ─────────────────────────────────────────────────────────────
    if any(w in t for w in ["hello","hi","hey","greetings","good morning","good evening","good afternoon"]):
        hour = datetime.datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
        return f"{greeting}! I'm ZEUS, your personal assistant. How can I help you today?"

    # ── Exit ──────────────────────────────────────────────────────────────────
    if any(w in t for w in ["exit","quit","bye","goodbye","shut yourself","stop zeus"]):
        speak("Goodbye! Have a great day!")
        return "__EXIT__"

    # ── Help ──────────────────────────────────────────────────────────────────
    if "help" in t or "what can you do" in t or "commands" in t:
        return (
            "I can: check weather, read news, get stock prices, tell jokes, "
            "open apps, create files and folders, take screenshots, control volume, "
            "lock or shutdown your computer, play music, search the web, manage notes and todos, "
            "convert currencies, and answer any question using AI. Just ask!"
        )

    # ── Fallback: AI ─────────────────────────────────────────────────────────
    return ask_zeus(text)


# ── GUI ───────────────────────────────────────────────────────────────────────
try:
    import tkinter as tk
    from tkinter import scrolledtext, ttk
    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False

class ZeusGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ZEUS Desktop Assistant")
        self.root.geometry("820x700")
        self.root.minsize(600, 600)
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(True, True)
        self.listening = False
        self._wake_active = False
        self._build_ui()
        self.root.after(1000, self._start_wake_word)

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1a1a2e", pady=12)
        header.pack(fill=tk.X, padx=15, pady=(15, 0))
        tk.Label(header, text="ZEUS", font=("Consolas", 28, "bold"),
                 fg="#ffd700", bg="#1a1a2e").pack(side=tk.LEFT, padx=15)
        tk.Label(header, text="Zero Effort Universal System",
                 font=("Segoe UI", 11), fg="#aaaaaa", bg="#1a1a2e").pack(side=tk.LEFT)

        # Status
        self.status_var = tk.StringVar(value="Ready — type, click MIC, or say 'Hey ZEUS'")
        tk.Label(self.root, textvariable=self.status_var,
                 font=("Segoe UI", 9), fg="#888888", bg="#0a0a0a"
                 ).pack(fill=tk.X, padx=15, pady=(6, 0))

        # Chat box — fixed height so input row is always visible
        self.chat_box = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state=tk.DISABLED,
            font=("Consolas", 11), bg="#111111", fg="#e0e0e0",
            insertbackground="#ffd700", relief=tk.FLAT,
            padx=12, pady=12, height=18)
        self.chat_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 5))
        self.chat_box.tag_config("user",   foreground="#ffd700", font=("Consolas", 11, "bold"))
        self.chat_box.tag_config("zeus",   foreground="#00ff88")
        self.chat_box.tag_config("system", foreground="#555555", font=("Consolas", 9, "italic"))

        # Input row
        row = tk.Frame(self.root, bg="#0a0a0a")
        row.pack(fill=tk.X, padx=15, pady=(0, 8))

        self.text_input = tk.Entry(
            row, font=("Consolas", 12),
            bg="#1a1a2e", fg="#ffffff",
            insertbackground="#ffd700",
            relief=tk.SOLID, bd=1)
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9, padx=(0, 8))
        self.text_input.bind("<Return>", lambda e: self._send_text())
        self.text_input.focus_set()   # auto-focus so user can type immediately

        tk.Button(row, text="Send", font=("Segoe UI", 10, "bold"),
                  bg="#ffd700", fg="#000000", activebackground="#ffee00",
                  relief=tk.FLAT, cursor="hand2", padx=16, pady=8,
                  command=self._send_text).pack(side=tk.LEFT)

        self.mic_btn = tk.Button(
            row, text="MIC", font=("Segoe UI", 10, "bold"),
            bg="#1a1a2e", fg="#ffffff", activebackground="#2a2a4e",
            relief=tk.FLAT, cursor="hand2", padx=12, pady=8,
            command=self._mic_click)
        self.mic_btn.pack(side=tk.LEFT, padx=(8, 0))

        tk.Button(row, text="STOP", font=("Segoe UI", 10, "bold"),
                  bg="#ff4444", fg="#ffffff", activebackground="#cc2222",
                  relief=tk.FLAT, cursor="hand2", padx=12, pady=8,
                  command=stop_speaking).pack(side=tk.LEFT, padx=(8, 0))

        # Quick buttons
        quick_row = tk.Frame(self.root, bg="#0a0a0a")
        quick_row.pack(fill=tk.X, padx=15, pady=(0, 10))
        for label, cmd in [
            ("Weather", "weather in pune"),
            ("India News", "india news"),
            ("Joke",    "tell me a joke"),
            ("Time",    "what time is it"),
            ("Screenshot", "take a screenshot"),
            ("Help",    "help"),
        ]:
            tk.Button(quick_row, text=label, font=("Segoe UI", 9),
                      bg="#1a1a2e", fg="#cccccc", activebackground="#2a2a4e",
                      relief=tk.FLAT, cursor="hand2", padx=10, pady=5,
                      command=lambda c=cmd: self._run_command(c)
                      ).pack(side=tk.LEFT, padx=3)

        # Voice + Personality row
        bottom_row = tk.Frame(self.root, bg="#0a0a0a")
        bottom_row.pack(fill=tk.X, padx=15, pady=(0, 12))

        tk.Label(bottom_row, text="Voice:", font=("Segoe UI", 9),
                 fg="#555555", bg="#0a0a0a").pack(side=tk.LEFT)
        self.voice_var = tk.StringVar(value="Loading...")
        self.voice_menu = ttk.Combobox(bottom_row, textvariable=self.voice_var,
                                       width=28, state="readonly")
        self.voice_menu.pack(side=tk.LEFT, padx=(4, 16))
        self.voice_menu.bind("<<ComboboxSelected>>", self._change_voice)

        tk.Label(bottom_row, text="Personality:", font=("Segoe UI", 9),
                 fg="#555555", bg="#0a0a0a").pack(side=tk.LEFT)
        self.pers_var = tk.StringVar(value=PERSONALITY)
        pers_menu = ttk.Combobox(bottom_row, textvariable=self.pers_var,
                                 values=list(PERSONALITY_PROMPTS.keys()),
                                 width=14, state="readonly")
        pers_menu.pack(side=tk.LEFT, padx=(4, 0))
        pers_menu.bind("<<ComboboxSelected>>", self._change_personality)

        # Load voices after UI is ready
        self.root.after(500, self._load_voices)

        # Welcome
        self._log("system", "ZEUS Desktop ready. Type a command and press Enter, or click MIC.\n"
                             "Type 'help' to see all commands.\n")

    def _log(self, role, text):
        self.chat_box.config(state=tk.NORMAL)
        if role == "user":
            self.chat_box.insert(tk.END, f"\nYou: {text}\n", "user")
        elif role == "zeus":
            self.chat_box.insert(tk.END, f"ZEUS: {text}\n", "zeus")
        else:
            self.chat_box.insert(tk.END, text, "system")
        self.chat_box.config(state=tk.DISABLED)
        self.chat_box.see(tk.END)
        self.text_input.focus_set()   # always return focus to input box

    def _run_command(self, text):
        text = text.strip()
        if not text:
            return
        if getattr(self, '_busy', False):
            return   # prevent double execution
        self._busy = True
        self._log("user", text)
        self.status_var.set("Thinking...")

        def worker():
            try:
                response = parse_and_execute(text)
                if response == "__EXIT__":
                    self.root.after(0, self.root.destroy)
                    return
                self.root.after(0, lambda r=response: self._log("zeus", r))
                self.root.after(0, lambda: self.status_var.set("Ready — type or click MIC"))
                speak(response)
            except Exception as e:
                msg = f"Error: {e}"
                print(msg)
                import traceback; traceback.print_exc()
                self.root.after(0, lambda m=msg: self._log("zeus", m))
                self.root.after(0, lambda: self.status_var.set("Ready"))
            finally:
                self._busy = False

        threading.Thread(target=worker, daemon=True).start()

    def _send_text(self):
        text = self.text_input.get().strip()
        if not text:
            return
        self.text_input.delete(0, tk.END)
        self._run_command(text)

    def _mic_click(self):
        if self.listening:
            return
        if not MIC_OK:
            self._log("zeus", "Microphone not available. Please type your command.")
            return
        self.listening = True
        self.mic_btn.config(text="...", bg="#ff4444")
        self.status_var.set("Listening... speak now")

        def worker():
            heard = ""
            try:
                heard = listen(timeout=7, phrase_limit=15)
            except Exception as e:
                print(f"Mic error: {e}")
            self.listening = False
            self.root.after(0, lambda: self.mic_btn.config(text="MIC", bg="#1a1a2e"))
            if heard:
                self.root.after(0, lambda h=heard: self._run_command(h))
            else:
                self.root.after(0, lambda: self.status_var.set("Didn't catch that — try again or type"))

        threading.Thread(target=worker, daemon=True).start()

    def _load_voices(self):
        def worker():
            voices = get_available_voices()
            if voices:
                names = [f"{i}. {n}" for i, n in voices]
                self.root.after(0, lambda: self.voice_menu.config(values=names))
                self.root.after(0, lambda: self.voice_var.set(names[CURRENT_VOICE_INDEX] if names else "No voices found"))
            else:
                self.root.after(0, lambda: self.voice_var.set("No voices found"))
        threading.Thread(target=worker, daemon=True).start()

    def _start_wake_word(self):
        """Always-on wake word — uses separate recognizer instance."""
        if not MIC_OK:
            return
        self._wake_active = True
        wake_recognizer = sr.Recognizer()
        wake_recognizer.energy_threshold = 200
        wake_recognizer.dynamic_energy_threshold = True
        wake_recognizer.pause_threshold = 0.5
        def _loop():
            while self._wake_active:
                try:
                    if self.listening:
                        time.sleep(0.3)
                        continue
                    with sr.Microphone() as source:
                        wake_recognizer.adjust_for_ambient_noise(source, duration=0.2)
                        try:
                            audio = wake_recognizer.listen(
                                source, timeout=2, phrase_time_limit=4)
                            heard = wake_recognizer.recognize_google(audio).lower()
                            print(f"[WAKE] heard: {heard}")
                            # Accept common mishearings of "Zeus"
                            zeus_variants = ["zeus", "juice", "jews", "ze ", "zus",
                                           "use", "zooms", "z ", "hey z", "zeus's"]
                            if any(v in heard for v in zeus_variants):
                                cmd = heard
                                for v in ["hey zeus","hey juice","hey jews",
                                          "hey ze","hey zus","zeus","juice",
                                          "jews","ze ","zus","hey"]:
                                    cmd = cmd.replace(v, "")
                                cmd = cmd.strip()
                                if cmd and len(cmd) > 3:
                                    self.root.after(0, lambda c=cmd: self._run_command(c))
                                else:
                                    self.root.after(0, self._mic_click)
                        except (sr.WaitTimeoutError, sr.UnknownValueError):
                            pass
                        except Exception as e:
                            print(f"[WAKE] recognition error: {e}")
                except Exception as e:
                    print(f"[WAKE] mic error: {e}")
                    time.sleep(2)
        threading.Thread(target=_loop, daemon=True).start()

    def _change_voice(self, event=None):
        global CURRENT_VOICE_INDEX
        val = self.voice_var.get()
        try:
            CURRENT_VOICE_INDEX = int(val.split(".")[0])
            self._log("system", f"[Voice changed to: {val}]\n")
            speak("Hello, this is your new voice.")
        except Exception:
            pass

    def _change_personality(self, event=None):
        global PERSONALITY
        PERSONALITY = self.pers_var.get()
        self._log("system", f"[Personality changed to {PERSONALITY}]\n")

    def run(self):
        self.root.after(800, lambda: speak("ZEUS ready."))
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._busy = False   # init here to prevent startup double-trigger
        self.root.mainloop()

    def _on_close(self):
        self._wake_active = False
        self.root.destroy()


# ── CLI fallback ──────────────────────────────────────────────────────────────
def run_cli():
    print("⚡ ZEUS Desktop — CLI mode (no display found)")
    speak("ZEUS is ready in command line mode.")
    while True:
        try:
            text = input("\nYou: ").strip()
            if not text:
                continue
            response = parse_and_execute(text)
            if response == "__EXIT__":
                break
            speak(response)
        except (KeyboardInterrupt, EOFError):
            speak("Goodbye!")
            break


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if GUI_AVAILABLE:
        app = ZeusGUI()
        app.run()
    else:
        run_cli()
