"""
Application configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# API Keys
FRED_API_KEY = os.getenv('FRED_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')

# AI settings - Groq (cloud, fast) is preferred over Ollama (local, slow)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

# Ollama settings (fallback if Groq unavailable)
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

# Data source priority (primary to fallback)
DATA_SOURCE_PRIORITY = ['openbb', 'yfinance']

# Cache settings
CACHE_DIR = ROOT_DIR / '.cache'
CACHE_TTL_MINUTES = 15  # Cache time-to-live in minutes

# Database settings
DB_PATH = ROOT_DIR / 'data' / 'pdf_visualizer.db'
DB_PATH.parent.mkdir(exist_ok=True)

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = ROOT_DIR / 'logs' / 'app.log'
LOG_FILE.parent.mkdir(exist_ok=True)

# Streamlit settings
STREAMLIT_THEME = 'dark'
STREAMLIT_PORT = 8501
