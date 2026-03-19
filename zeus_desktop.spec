# -*- mode: python ; coding: utf-8 -*-
# ⚡ ZEUS Desktop — PyInstaller spec file
# Build with:  pyinstaller zeus_desktop.spec

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['zeus_desktop.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[
        ('.env', '.'),                  # include .env so API keys load
    ],
    hiddenimports=[
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',        # Windows TTS driver
        'pyttsx3.drivers.nsss',         # macOS TTS driver
        'pyttsx3.drivers.espeak',       # Linux TTS driver
        'speech_recognition',
        'pyaudio',
        'groq',
        'requests',
        'yfinance',
        'wikipedia',
        'pyjokes',
        'pyautogui',
        'pyperclip',
        'dotenv',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'pkg_resources.py2_compat',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'streamlit',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ZEUS_Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # No black CMD window — GUI only
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,               # Add icon='zeus.ico' if you have one
)
