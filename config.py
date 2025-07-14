import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Daftar ID Telegram
AM_MAPPING = {
    "FANDI": 1825371102,
    # dan seterusnya
}
