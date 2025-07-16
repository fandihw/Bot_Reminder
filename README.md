# ⏰ Reminder Telegram Bot

Bot Telegram otomatis yang digunakan untuk mengirimkan pengingat pembayaran kepada Account Manager (AM) berdasarkan data dari **Google Spreadsheet**. Bot ini membantu proses follow-up tagihan pelanggan secara efisien, terstruktur, dan terdokumentasi.

---

## 🚀 Fitur Utama

- Menarik data pelanggan berstatus *PU* dari spreadsheet secara otomatis
- Format pesan reminder per pelanggan, disesuaikan dengan bulan tagihan berjalan
- Pengiriman pesan otomatis setiap bulan (tanggal 15–31), atau dapat dijalankan manual untuk pengujian
- ID pelanggan ditampilkan dalam pesan agar dapat dibalas langsung oleh AM
- Dukungan reply-to-message untuk pengisian komitmen pembayaran
- Konfirmasi pembaruan jika kolom `Keterangan` sudah terisi sebelumnya

---

## 🧰 Teknologi yang Digunakan

- [Python 3.x](https://www.python.org/)
- [python-telegram-bot ≥ v20](https://github.com/python-telegram-bot/python-telegram-bot)
- [gspread](https://gspread.readthedocs.io/)
- [Google Sheets API](https://developers.google.com/sheets)

---

## ⚙️ Cara Menjalankan

1. Pastikan environment sudah terisi dengan variabel `TELEGRAM_TOKEN`, `SPREADSHEET_ID`, dan path ke `service_account.json`.
2. Jalankan bot dengan:
```bash
python main.py
