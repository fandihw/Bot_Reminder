from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from handlers.callback_handler import handle_callback_query, handle_keterangan_input, EDIT_KETERANGAN, KONFIRMASI_KETERANGAN
from config import TELEGRAM_TOKEN
from start import create_scheduler  # ✅ Ini sekarang akan berhasil

async def start_scheduler(app):
    scheduler = create_scheduler(app)
    scheduler.start()

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(start_scheduler).build()

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_callback_query)],
        states={
            EDIT_KETERANGAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_keterangan_input)],
            KONFIRMASI_KETERANGAN: [CallbackQueryHandler(handle_callback_query)],
        },
        fallbacks=[]
    ))

    print("Bot Reminder berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
