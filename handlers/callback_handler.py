from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import escape_markdown

from services.spreadsheet import (
    update_keterangan_by_id,
    get_keterangan_by_id,
    get_bp_name_by_id
)

EDIT_KETERANGAN, KONFIRMASI_KETERANGAN = range(2)

# Format: {user_id: {"idnumber": str, "nama": str, "draft": str}}
user_editing = {}

def build_keterangan_edit_message(idnumber, nama, existing_note):
    return (
        f"📝 *Edit Keterangan Pelanggan*\n\n"
        f"🆔 *ID Pelanggan:* `{escape_markdown(idnumber, version=2)}`\n"
        f"🏫 *Nama Pelanggan:* {escape_markdown(nama or 'Tidak diketahui', version=2)}\n"
        f"📄 *Keterangan saat ini:*\n"
        f"└─ _{escape_markdown(existing_note or 'Belum ada', version=2)}_\n\n"
        f"Silakan kirim keterangan baru untuk pelanggan ini:"
    )

def build_keterangan_confirm_preview(idnumber, nama, keterangan):
    return (
        f"🔎 *Konfirmasi Keterangan*\n\n"
        f"🆔 *ID Pelanggan:* `{escape_markdown(idnumber, version=2)}`\n"
        f"🏫 *Nama Pelanggan:* {escape_markdown(nama, version=2)}\n"
        f"✍️ *Keterangan baru:*\n"
        f"└─ _{escape_markdown(keterangan, version=2)}_\n\n"
        f"Apakah kamu yakin ingin menyimpan ini?"
    )

def build_keterangan_update_success(bp_name, idnumber, keterangan):
    return (
        f"✅ *Keterangan berhasil diperbarui*\n\n"
        f"🏢 *BP Name:* {escape_markdown(bp_name, version=2)}\n"
        f"🆔 *ID Pelanggan:* `{escape_markdown(idnumber, version=2)}`\n"
        f"🆕 *Keterangan baru:*\n"
        f"└─ _{escape_markdown(keterangan, version=2)}_"
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("edit_"):
        idnumber = query.data.split("_", maxsplit=1)[1]
        result = get_keterangan_by_id(idnumber)

        if not result:
            await query.message.reply_text("❌ Data pelanggan tidak ditemukan")
            return ConversationHandler.END

        nama_pelanggan = result.get("nama") or "Tidak diketahui"
        existing_note = result.get("keterangan") or "Belum ada"

        user_editing[user_id] = {
            "idnumber": idnumber,
            "nama": nama_pelanggan
        }

        message = build_keterangan_edit_message(idnumber, nama_pelanggan, existing_note)
        await query.message.reply_text(message, parse_mode="MarkdownV2")
        return EDIT_KETERANGAN

    elif query.data == "confirm_keterangan":
        if user_id not in user_editing or "draft" not in user_editing[user_id]:
            await query.message.reply_text("❌ Tidak ada data yang sedang dikonfirmasi")
            return ConversationHandler.END

        idnumber = user_editing[user_id]["idnumber"]
        keterangan = user_editing[user_id]["draft"]
        update_keterangan_by_id(idnumber, keterangan)

        await query.message.edit_reply_markup(reply_markup=None)

        bp_name = get_bp_name_by_id(idnumber) or "Tidak diketahui"
        success_message = build_keterangan_update_success(bp_name, idnumber, keterangan)
        await query.message.reply_text(success_message, parse_mode="MarkdownV2")

        # 🎉 Pesan tambahan santai
        await query.message.reply_text(
            "🎉 Sip, datanya udah di-update ya!\n"
            "Kalau mau ubah lagi, tinggal klik edit seperti biasa. 😉"
        )

        del user_editing[user_id]
        return ConversationHandler.END

    elif query.data == "cancel_keterangan":
        if user_id in user_editing:
            del user_editing[user_id]

        await query.edit_message_text(
            text="❌ *Edit keterangan dibatalkan*",
            parse_mode="MarkdownV2"
        )

        # ✋ Pesan tambahan santai
        await query.message.reply_text(
            "Oke, nggak jadi disimpan ya. 👍\n"
            "Kalau berubah pikiran, tinggal coba lagi kapan aja."
        )
        return ConversationHandler.END

    elif query.data == "edit_keterangan":
        await query.message.reply_text(
            "🔍 Silakan kirim ID pelanggan yang ingin kamu edit keterangannya."
        )
        return ConversationHandler.END

    await query.message.reply_text("⚠️ Aksi tidak dikenali")
    return ConversationHandler.END

async def handle_keterangan_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keterangan = update.message.text.strip()

    if user_id not in user_editing:
        await update.message.reply_text("❌ Tidak ada data yang sedang diedit")
        return ConversationHandler.END

    user_editing[user_id]["draft"] = keterangan

    idnumber = user_editing[user_id]["idnumber"]
    nama = user_editing[user_id]["nama"]
    preview = build_keterangan_confirm_preview(idnumber, nama, keterangan)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ya, Simpan", callback_data="confirm_keterangan"),
            InlineKeyboardButton("❌ Batal", callback_data="cancel_keterangan")
        ]
    ])

    await update.message.reply_text(preview, parse_mode="MarkdownV2", reply_markup=keyboard)
    return KONFIRMASI_KETERANGAN
