'''
def schedule_reminder(app):
    app.job_queue.run_daily(
        send_reminders,
        time=time(hour=8, minute=0, tzinfo=timezone(timedelta(hours=7))),
        name="daily_reminder"
    )
'''
#reminder.py
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from services.spreadsheet import get_invoice_reminder_data
from config import AM_MAPPING
from datetime import datetime

def format_rupiah(value):
    try:
        number = int(str(value).replace(".", "").replace(",", "").replace("Rp", "").strip())
        return f"Rp.{number:,}".replace(",", ".")
    except Exception:
        return str(value)

async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    tanggal_str = now.strftime("%d/%m/%Y")
    print(f"[INFO] Menjalankan pengiriman reminder pada {now}")

    data_list = get_invoice_reminder_data()
    if not data_list:
        print("[INFO] Tidak ada data pelanggan PU")
        return

    for data in data_list:
        am_name = data.get("am", "").upper()
        chat_id = AM_MAPPING.get(am_name)

        if not chat_id:
            print(f"[PERINGATAN] AM '{am_name}' BELUM TERDAFTAR")
            continue

        try:
            nilai_tagihan = format_rupiah(data["nilai"])
            text = (
                f"*📌 Reminder Tagihan {escape_markdown(tanggal_str, version=2)}*\n\n"
                f"*Pelanggan:* {escape_markdown(str(data['nama']), version=2)}\n"
                f"*AM:* {escape_markdown(am_name, version=2)}\n"
                f"*Bulan:* {escape_markdown(data['bulan'], version=2)}\n"
                f"*Nilai Tagihan:* {escape_markdown(nilai_tagihan, version=2)}\n\n"
                f"ID Pelanggan: `{escape_markdown(str(data['idnumber']), version=2)}`\n\n"
            )

            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="MarkdownV2"
            )
            print(f"[✓] Reminder dikirim ke {chat_id} → {data['nama']}")

        except Exception as e:
            print(f"[ERROR] Gagal kirim ke {chat_id} ({am_name}): {e}")

def schedule_reminder(app):
    app.job_queue.run_once(
        send_reminders,
        when=5,
        name="test_reminder"
    )