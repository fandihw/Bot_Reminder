import os
import json
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Baca file am_mapping.json
with open("am_mapping.json", "r", encoding="utf-8") as f:
    AM_MAPPING = json.load(f)