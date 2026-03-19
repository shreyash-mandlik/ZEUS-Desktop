# ⚡ ZEUS Desktop
### Zero Effort Universal System — Desktop Voice Assistant

A full offline-capable voice assistant with system control, AI chat, and all web features.

---

## 🚀 Quick Start

### Option A — Run directly (development)
```bash
pip install -r requirements_desktop.txt
python zeus_desktop.py
```

### Option B — Build .exe (distribute anywhere)
```
Double-click BUILD.bat
→ Your exe appears at dist/ZEUS_Desktop.exe
```

---

## 🎙️ Voice Commands

### Wake Word
Just say **"Hey ZEUS"** — it's always listening in the background.

### Time & Greetings
| Say | Action |
|-----|--------|
| "What time is it" | Current time and date |
| "Hello" / "Hey" | Greeting |

### Weather & News
| Say | Action |
|-----|--------|
| "Weather in Mumbai" | Live weather |
| "Latest news" | Top 3 headlines |
| "Technology news" | Category news |

### Stocks & Finance
| Say | Action |
|-----|--------|
| "Stock price TSLA" | Stock quote |
| "Convert 100 USD to INR" | Currency conversion |

### System Control 💻
| Say | Action |
|-----|--------|
| "Open VS Code" | Launches app |
| "Open Chrome" | Opens browser |
| "Create folder Projects" | New folder on Desktop |
| "Create file notes.txt" | New file on Desktop |
| "Take a screenshot" | Saves PNG to Desktop |
| "Volume up / down / mute" | Audio control |
| "Lock computer" | Locks screen |
| "Shutdown computer" | Shuts down (5s delay) |
| "Restart computer" | Restarts (5s delay) |
| "Type hello world" | Auto-types text |

### Productivity
| Say | Action |
|-----|--------|
| "Add note buy groceries" | Saves a note |
| "My notes" | Lists all notes |
| "Add task finish report" | Adds to todo list |
| "My todos" | Lists pending tasks |
| "Search Google machine learning" | Opens browser search |
| "Play music" | Plays local MP3 files |
| "What's in my clipboard" | Reads clipboard |

### AI & Fun
| Say | Action |
|-----|--------|
| "Tell me a joke" | Random joke |
| "Generate a password" | Secure password |
| "Who is Elon Musk" | Wikipedia summary |
| "What is quantum computing" | AI explanation |
| Anything else | Groq AI (Llama 3.3 70B) |

---

## 🛠️ Setup

### 1. API Keys
Edit `.env` file:
```
GROQ_API_KEY=your_key_here     # free at console.groq.com
NEWS_API_KEY=your_key_here     # free at newsapi.org
```

### 2. PyAudio (Windows)
If `pip install pyaudio` fails:
```bash
pip install pipwin
pipwin install pyaudio
```

### 3. PyAudio (Linux)
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
```

---

## 📦 Building the .exe

1. Put your real API keys in `.env`
2. Double-click `BUILD.bat`
3. Wait 2-5 minutes
4. Find your exe at `dist/ZEUS_Desktop.exe`

**The exe is fully self-contained** — works on any Windows PC without Python installed.

---

## 🌐 Offline vs Online features

| Feature | Offline | Online |
|---------|---------|--------|
| Time/Date | ✅ | — |
| Open apps | ✅ | — |
| Screenshots | ✅ | — |
| Volume/Lock | ✅ | — |
| Create files | ✅ | — |
| Notes & Todos | ✅ | — |
| Password gen | ✅ | — |
| Jokes | ✅ | — |
| Weather | ❌ | ✅ |
| News | ❌ | ✅ |
| Stock prices | ❌ | ✅ |
| Currency | ❌ | ✅ |
| AI Chat | ❌ | ✅ |
| Wikipedia | ❌ | ✅ |

---

## 👤 Author
**Shreyash Mandlik**  
[GitHub](https://github.com/shreyash-mandlik) | [LinkedIn](https://linkedin.com/in/shreyash-mandlik)
