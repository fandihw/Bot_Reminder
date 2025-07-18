import json
import logging
from datetime import datetime, timedelta
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from services.spreadsheet import get_keterangan_updates_by_date
from config import AM_MAPPING


# Fungsi untuk membaca ID manager dari file JSON
def load_manager_ids():
    try:
        with open('manager_id.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('manager_id', [])
    except Exception as e:
        logging.error(f"[ERROR] Gagal membaca file manager_id.json: {e}")
        return []

# Fungsi utama untuk mengirim laporan harian
async def send_daily_keterangan_report(bot):
    try:
        yesterday = (datetime.now() - timedelta(days=1)).date()
        updates = get_keterangan_updates_by_date(str(yesterday))

        logging.debug(f"Ada {len(updates)} update untuk tanggal {yesterday}")

        if not updates:
            logging.info("Tidak ada update keterangan untuk dikirim")
            return

        # Header pesan (tanggal perlu di-escape)
        message = f"*📋 Laporan Update Keterangan \\({escape_markdown(str(yesterday), version=2)}\\)*\n\n"

        # Tambahkan per AM
        for am, pelanggan_list in updates.items():
            escaped_am = escape_markdown(am.upper(), version=2)
            message += f"👤 *{escaped_am}*\n"
            for pelanggan in pelanggan_list:
                escaped_pelanggan = escape_markdown(pelanggan, version=2)
                message += f"• {escaped_pelanggan}\n"
            message += "\n"

        manager_ids = load_manager_ids()
        logging.debug(f"Manager IDs: {manager_ids}")

        if not manager_ids:
            logging.warning("Tidak ada ID manager yang ditemukan. Laporan tidak dikirim")
            return

        # Kirim ke semua manager dan log status
        for manager_id in manager_ids:
            await bot.send_message(
                chat_id=manager_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            logging.info(f"[✓] Laporan dikirim ke {manager_id}")
            print(f"[✓] Report berhasil dikirim ke Manager -> {manager_id}")

    except Exception as e:
        logging.exception("[!] Gagal mengirim laporan update keterangan:")
