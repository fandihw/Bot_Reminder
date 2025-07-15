from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from services.spreadsheet import update_keterangan_by_id, get_keterangan_by_id, get_bp_name_by_id
from telegram.helpers import escape_markdown

EDIT_KETERANGAN, KONFIRMASI_KETERANGAN = range(2)

# Format: {user_id: {"idnumber": str, "nama": str, "draft": str}}
user_editing = {}

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("edit_"):
        idnumber = query.data.split("_")[1]
        user_id = query.from_user.id

        result = get_keterangan_by_id(idnumber)
        existing_note = result["keterangan"]
        nama_pelanggan = result["nama"]

        user_editing[user_id] = {
            "idnumber": idnumber,
            "nama": nama_pelanggan
        }

        text = (
            f"📝 *Edit Keterangan Pelanggan*\n\n"
            f"🆔 *ID Pelanggan:* `{escape_markdown(idnumber, version=2)}`\n"
            f"🏫 *Nama Pelanggan:* {escape_markdown(nama_pelanggan or 'Tidak diketahui', version=2)}\n"
            f"📄 *Keterangan saat ini:*\n"
            f"└─ _{escape_markdown(existing_note or 'Belum ada', version=2)}_\n\n"
            f"Silakan kirim keterangan baru untuk pelanggan ini:"
        )

        await query.message.reply_text(text, parse_mode="MarkdownV2")
        return EDIT_KETERANGAN

    elif query.data == "confirm_keterangan":
        user_id = update.effective_user.id
        if user_id not in user_editing:
            await update.callback_query.message.reply_text("❌ Tidak ada data yang sedang dikonfirmasi")
            return ConversationHandler.END

        idnumber = user_editing[user_id]["idnumber"]
        keterangan = user_editing[user_id]["draft"]

        update_keterangan_by_id(idnumber, keterangan)
        await query.message.edit_reply_markup(reply_markup=None)
        bp_name = get_bp_name_by_id(idnumber)
        await update.callback_query.message.reply_text(
            f"✅ *Keterangan berhasil diperbarui*\n\n"
            f"🏢 *BP Name:* {escape_markdown(bp_name, version=2)}\n" #<-----
            f"🆔 *ID Pelanggan:* `{escape_markdown(idnumber, version=2)}`\n"
            f"🆕 *Keterangan baru:*\n"
            f"└─ _{escape_markdown(keterangan, version=2)}_",
            parse_mode="MarkdownV2"
        )
        del user_editing[user_id]
        return ConversationHandler.END

    elif query.data == "cancel_keterangan":
        del user_editing[update.effective_user.id]

    await update.callback_query.edit_message_text(
        text="❌ *Edit keterangan dibatalkan*",
        parse_mode="MarkdownV2"
    )
    return ConversationHandler.END

async def handle_keterangan_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keterangan = update.message.text

    if user_id not in user_editing:
        await update.message.reply_text("❌ Tidak ada data yang sedang diedit")
        return ConversationHandler.END

    user_editing[user_id]["draft"] = keterangan

    preview = (
        f"🔎 *Konfirmasi Keterangan*\n\n"
        f"🆔 *ID Pelanggan:* `{escape_markdown(user_editing[user_id]['idnumber'], version=2)}`\n"
        f"🏫 *Nama Pelanggan:* {escape_markdown(user_editing[user_id]['nama'], version=2)}\n"
        f"✍️ *Keterangan baru:*\n"
        f"└─ _{escape_markdown(keterangan, version=2)}_\n\n"
        f"Apakah kamu yakin ingin menyimpan ini?"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ya, Simpan", callback_data="confirm_keterangan"),
            InlineKeyboardButton("❌ Batal", callback_data="cancel_keterangan")
        ]
    ])

    await update.message.reply_text(preview, parse_mode="MarkdownV2", reply_markup=keyboard)
    return KONFIRMASI_KETERANGAN
