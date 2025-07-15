import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import SPREADSHEET_ID

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(
    'credentials/service_account.json',
    scopes=SCOPES
)
client = gspread.authorize(creds)

def get_invoice_reminder_data():
    worksheet = client.open_by_key(SPREADSHEET_ID).sheet1
    rows = worksheet.get_all_records()
    header_row = worksheet.row_values(1)

    # Normalisasi header
    normalized_header = [h.strip().upper() for h in header_row]
    header_dict = {h.strip().upper(): h for h in header_row}

    # Mapping bulan
    bulan_map = {
        "JANUARY": "JANUARI",
        "FEBRUARY": "FEBRUARI",
        "MARCH": "MARET",
        "APRIL": "APRIL",
        "MAY": "MEI",
        "JUNE": "JUNI",
        "JULY": "JULI",
        "AUGUST": "AGUSTUS",
        "SEPTEMBER": "SEPTEMBER",
        "OCTOBER": "OKTOBER",
        "NOVEMBER": "NOVEMBER",
        "DECEMBER": "DESEMBER"
    }

    bulan_inggris = datetime.now().strftime("%B").upper()
    bulan_indo = bulan_map.get(bulan_inggris, bulan_inggris)
    kolom_bulan_norm = f"CYC {bulan_indo}".upper()

    if kolom_bulan_norm not in header_dict:
        print(f"[PERINGATAN] Kolom '{kolom_bulan_norm}' tidak ditemukan")
        print("[DEBUG] Header tersedia:", header_row)
        return []

    kolom_bulan_asli = header_dict[kolom_bulan_norm]

    result = []
    for row in rows:
        if str(row.get("STATUS", "")).strip().upper() == "PU":
            result.append({
                "idnumber": row.get("id Pelanggan", ""),
                "nama": row.get("BP Name", ""),
                "am": row.get("AM", "").strip(),
                "bulan": bulan_indo.capitalize(),
                "nilai": row.get(kolom_bulan_asli, ""),
                "status": row.get("STATUS", "")
            })
    return result

def update_keterangan_by_id(idnumber, keterangan):
    worksheet = client.open_by_key(SPREADSHEET_ID).sheet1
    try:
        cell = worksheet.find(str(idnumber))
        if cell:
            row = cell.row
            header_row = worksheet.row_values(1)
            header_dict = {h.strip().upper(): h for h in header_row}
            if "KETERANGAN" in header_dict:
                kolom_keterangan = header_row.index(header_dict["KETERANGAN"]) + 1
                worksheet.update_cell(row, kolom_keterangan, keterangan)
    except gspread.exceptions.CellNotFound:
        print(f"[ERROR] ID Pelanggan {idnumber} tidak ditemukan di spreadsheet")

def get_keterangan_by_id(idnumber):
    worksheet = client.open_by_key(SPREADSHEET_ID).sheet1
    try:
        cell = worksheet.find(str(idnumber))
        if cell:
            row = cell.row
            header_row = worksheet.row_values(1)
            values_row = worksheet.row_values(row)
            header_dict = {h.strip().upper(): h for h in header_row}

            kolom_keterangan = header_row.index(header_dict.get("KETERANGAN", "KETERANGAN")) + 1
            kolom_nama = header_row.index(header_dict.get("BP NAME", "BP NAME")) + 1

            keterangan = values_row[kolom_keterangan - 1] if kolom_keterangan <= len(values_row) else ""
            nama = values_row[kolom_nama - 1] if kolom_nama <= len(values_row) else ""

            return {"keterangan": keterangan, "nama": nama}
    except gspread.exceptions.CellNotFound:
        print(f"[ERROR] ID Pelanggan {idnumber} tidak ditemukan saat mengambil keterangan")
    return {"keterangan": "", "nama": ""}

def get_bp_name_by_id(idnumber):
    worksheet = client.open_by_key(SPREADSHEET_ID).sheet1
    try:
        # Temukan baris berdasarkan ID Pelanggan
        cell = worksheet.find(str(idnumber))
        if cell:
            row = cell.row
            header_row = worksheet.row_values(1)
            values_row = worksheet.row_values(row)
            header_dict = {h.strip().upper(): h for h in header_row}

            kolom_nama = header_row.index(header_dict.get("BP NAME", "BP NAME")) + 1
            nama = values_row[kolom_nama - 1] if kolom_nama <= len(values_row) else ""

            return nama or "Tidak diketahui"
    except gspread.exceptions.CellNotFound:
        print(f"[ERROR] ID Pelanggan {idnumber} tidak ditemukan saat mencari BP Name")
    return "Tidak ditemukan"
