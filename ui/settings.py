import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000").rstrip("/")
API_ACCESS_KEY = os.environ.get("API_ACCESS_KEY", "")
UI_PASSWORD = os.environ.get("UI_PASSWORD", "")