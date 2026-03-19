# ⚡ ZEUS Desktop
### Zero Effort Universal System — AI Desktop Voice Assistant

> A fully-featured desktop voice assistant built with Python. Supports wake word detection, AI chat, system control, live weather, news, stocks, and much more — works both offline and online.

---

## ✨ Features

- 🎙️ **Wake Word** — Say "Hey ZEUS" to activate hands-free
- 🤖 **AI Chat** — Powered by Groq (Llama 3.3 70B)
- 🔊 **Voice Output** — Speaks every response aloud with STOP button
- 🌤️ **Live Weather** — Any city worldwide
- 📰 **News** — India news, Global news, by category
- 📈 **Stock Prices** — Real-time quotes
- 💱 **Currency Converter** — Live exchange rates
- 💻 **System Control** — Open apps, screenshots, volume, lock, shutdown
- 📁 **File Management** — Create files and folders
- 📝 **Notes & Todos** — Voice-driven productivity
- 🎵 **Play Music** — Local MP3 files
- 😂 **Jokes & Fun** — Random programming jokes
- 🔐 **Password Generator** — Secure random passwords
- 🌍 **Wikipedia Search** — Instant summaries
- 🔍 **Web Search** — Opens Google with your query
- 🖥️ **Multiple Voices** — Switch between installed Windows voices
- 🎭 **Personality Modes** — Friendly, Professional, Sarcastic, Motivational, Teacher

---

## 🖥️ Requirements

- Windows 10 or 11
- Python 3.11 — [Download here](https://www.python.org/downloads/release/python-3119/)
- Microphone (for voice input)
- Internet connection (for AI, weather, news, stocks)

---

## 🚀 Installation — Step by Step

### Step 1 — Download the project

**Clone with Git:**
```bash
git clone https://github.com/shreyash-mandlik/ZEUS-Desktop.git
cd ZEUS-Desktop
```

**Or download ZIP:**
- Click the green **Code** button → **Download ZIP**
- Extract and open the folder in VS Code or a terminal

---

### Step 2 — Install Python 3.11

1. Go to [python.org](https://www.python.org/downloads/release/python-3119/)
2. Download **Windows installer (64-bit)**
3. Run installer — **check "Add Python to PATH"**
4. Verify:
```bash
python --version
# Should show: Python 3.11.x
```

---

### Step 3 — Get your FREE API Keys

#### 🔑 Groq API Key (for AI chat) — Free
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Go to **API Keys** → **Create API Key**
4. Copy the key — starts with `gsk_...`

#### 🔑 NewsAPI Key (for news) — Free
1. Go to [newsapi.org](https://newsapi.org)
2. Click **Get API Key** and sign up free
3. Copy your API key from the dashboard

---

### Step 4 — Create your .env file

Open a terminal in the project folder and run:

```powershell
[System.IO.File]::WriteAllText("$PWD\.env", "GROQ_API_KEY=your_groq_key_here`nNEWS_API_KEY=your_newsapi_key_here`n")
```

Replace `your_groq_key_here` and `your_newsapi_key_here` with your actual keys.

Verify it worked:
```bash
cat .env
```

Should show:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
NEWS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ Never share this file or commit it to GitHub — it's already in `.gitignore`

---

### Step 5 — Install dependencies

```bash
python -m pip install -r requirements_desktop.txt
```

**If PyAudio fails:**
```bash
python -m pip install pipwin
pipwin install pyaudio
```

**If you get a DLL/charset error:**
```bash
python -m pip install charset-normalizer --force-reinstall --no-binary charset-normalizer
```

---

### Step 6 — Run ZEUS

```bash
python zeus_desktop.py
```

ZEUS will open and say **"ZEUS ready"** — you're all set! ⚡

---

## 🎙️ How to Use

### Option 1 — Wake Word (hands-free)
Say **"Hey ZEUS"** — ZEUS listens in the background constantly.
The MIC button turns red when active. Speak your command, ZEUS responds.

### Option 2 — MIC Button
Click **MIC**, speak your command, ZEUS responds with voice.

### Option 3 — Type
Type in the text box and press **Enter** or **Send**.

### Stop speaking
Click **STOP** anytime to interrupt ZEUS mid-sentence.

---

## 🗣️ Voice Commands Reference

### 🌤️ Weather
| Say | Result |
|-----|--------|
| `weather in pune` | Current weather for Pune |
| `weather in Mumbai` | Any city worldwide |

### 📰 News
| Say | Result |
|-----|--------|
| `india news` | Latest Indian headlines |
| `global news` | Worldwide headlines |
| `top 10 india news` | 10 headlines |
| `technology news` | Tech news |
| `sports news` | Sports headlines |
| `business news` | Business news |

### 📈 Stocks & Finance
| Say | Result |
|-----|--------|
| `stock AAPL` | Apple stock quote |
| `stock TSLA` | Tesla stock |
| `stock RELIANCE` | Reliance Industries |
| `convert 100 USD to INR` | Currency conversion |

### 💻 Open Apps
| Say | Result |
|-----|--------|
| `open WhatsApp` | Opens WhatsApp |
| `open Telegram` | Opens Telegram |
| `open Chrome` | Opens Chrome |
| `open VS Code` | Opens VS Code |
| `open Word` | Opens Microsoft Word |
| `open Excel` | Opens Microsoft Excel |
| `open Spotify` | Opens Spotify |
| `open Discord` | Opens Discord |
| `open any app` | Searches and opens |

### 📁 Files & System
| Say | Result |
|-----|--------|
| `create folder Projects` | New folder on Desktop |
| `create file notes.txt` | New file on Desktop |
| `take a screenshot` | Saved to Desktop |
| `volume up / down / mute` | Audio control |
| `lock computer` | Locks screen |
| `shutdown computer` | Shuts down (5s delay) |
| `type hello world` | Auto-types text |
| `what's in my clipboard` | Reads clipboard |

### 📝 Productivity
| Say | Result |
|-----|--------|
| `add note buy groceries` | Saves a note |
| `my notes` | Lists all notes |
| `add task finish report` | Adds todo |
| `my todos` | Lists pending tasks |
| `play music` | Plays local MP3 files |
| `search Google AI trends` | Google search |

### 🤖 AI & Fun
| Say | Result |
|-----|--------|
| `who is APJ Abdul Kalam` | Wikipedia summary |
| `what is deep learning` | AI explanation |
| `tell me a joke` | Random joke |
| `generate a password` | Secure password |
| `what time is it` | Current time & date |
| `help` | All commands list |
| Anything else | Groq AI answers |

---

## ⚙️ App Settings

- **Voice** — Switch between installed Windows voices (male/female)
- **Personality** — How ZEUS talks:
  - `Friendly` — Warm (default)
  - `Professional` — Formal
  - `Sarcastic` — Witty & funny
  - `Motivational` — Inspiring
  - `Teacher` — Clear explanations

---

## 🌐 Offline vs Online

| Feature | Offline | Online |
|---------|:-------:|:------:|
| Time & Date | ✅ | |
| Open Apps | ✅ | |
| Screenshots | ✅ | |
| Volume / Lock | ✅ | |
| Create Files | ✅ | |
| Notes & Todos | ✅ | |
| Password Generator | ✅ | |
| Jokes | ✅ | |
| Weather | | ✅ |
| News | | ✅ |
| Stock Prices | | ✅ |
| Currency | | ✅ |
| AI Chat | | ✅ |
| Wikipedia | | ✅ |

---

## 📦 Build Standalone .exe

To distribute ZEUS without Python:

1. Add real API keys to `.env`
2. Double-click `BUILD.bat`
3. Wait 3-5 minutes
4. Find exe at `dist\ZEUS_Desktop.exe`

Copy to any Windows PC — no Python needed!

---

## 🖱️ How to Open ZEUS Daily (After Setup)

Once setup is done, you never need to touch the terminal again.

### Option 1 — One-click Desktop Shortcut (Recommended)

Create a `Launch ZEUS.bat` file in your project folder with this content:
```bat
@echo off
cd /d "D:\Shreyash_Projects\ZEUSDesktop"
python zeus_desktop.py
```

Then:
1. **Right-click** `Launch ZEUS.bat` → **Create Shortcut**
2. **Drag the shortcut to your Desktop**
3. **Double-click it anytime** to open ZEUS instantly

> 💡 `.bat` files can't be pinned to taskbar directly. Use the desktop shortcut instead.

### Option 2 — From VS Code Terminal

Open VS Code in the project folder and run:
```bash
python zeus_desktop.py
```

### Option 3 — From any terminal

```bash
cd D:\Shreyash_Projects\ZEUSDesktop
python zeus_desktop.py
```

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `pip` blocked | Use `python -m pip install ...` |
| PyAudio fails | Run `pipwin install pyaudio` |
| DLL error | `pip install charset-normalizer --force-reinstall --no-binary charset-normalizer` |
| `.env` not loading | Make sure `.env` is in same folder as `zeus_desktop.py` |
| GROQ key not found | Check no spaces around `=` in `.env` |
| Mic not working | Windows Settings → Privacy → Microphone → Allow |
| Wake word not detecting | Say "Hey Zeus" clearly — also accepts "Hey Juice", "Hey Ze" |
| App not opening | App may not be installed — ZEUS will fall back to web search |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.11 | Core language |
| Tkinter | Desktop GUI |
| Groq API (Llama 3.3 70B) | AI responses |
| SpeechRecognition + PyAudio | Voice input |
| pyttsx3 | Voice output (TTS) |
| Open-Meteo API | Weather (free, no key) |
| NewsAPI | News headlines |
| yfinance | Stock prices |
| ExchangeRate API | Currency |
| Wikipedia | Knowledge search |
| PyAutoGUI | Screenshots & auto-type |
| PyPerClip | Clipboard |
| python-dotenv | API key management |

---

## 👤 Author

**Shreyash Mandlik**
- 🐙 GitHub: [github.com/shreyash-mandlik](https://github.com/shreyash-mandlik)
- 💼 LinkedIn: [linkedin.com/in/shreyash-mandlik](https://linkedin.com/in/shreyash-mandlik)
- 🌐 ZEUS Web: [Try the web version](https://zeus-ai-assistant-ga3bteyj5loaq4k2xduryv.streamlit.app)

---

> ⚡ Built by Shreyash Mandlik — Zero to Voice Assistant in one sprint!
