from telegram.ext import Application
from handlers.reminder import schedule_reminder
from config import TELEGRAM_TOKEN

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Jadwalkan reminder otomatis
    schedule_reminder(app)

    print("Bot Reminder berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
