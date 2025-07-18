import gspread
import re
import logging
from datetime import datetime, timezone, timedelta
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(
    'credentials/service_account.json',
    scopes=SCOPES
)
client = gspread.authorize(creds)

def get_cyc_worksheet():
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    current_year = datetime.now().year
    target_title = f"CYC {current_year}"

    try:
        return spreadsheet.worksheet(target_title)
    except gspread.exceptions.WorksheetNotFound:
        pattern = re.compile(r"CYC\s20\d{2}")
        matching_sheets = [ws for ws in spreadsheet.worksheets() if pattern.match(ws.title)]
        if not matching_sheets:
            raise ValueError("Sheet dengan format 'CYC 20XX' tidak ditemukan")
        matching_sheets.sort(key=lambda ws: int(ws.title.split()[1]), reverse=True)
        return matching_sheets[0]

def get_column_index(header_row, column_name):
    header_dict = {h.strip().upper(): idx for idx, h in enumerate(header_row)}
    return header_dict.get(column_name.strip().upper())

def get_row_by_id(worksheet, idnumber):
    try:
        header_row = worksheet.row_values(1)
        id_col_index = get_column_index(header_row, "IdNumber")
        if id_col_index is None:
            raise ValueError("Kolom 'IdNumber' tidak ditemukan")

        all_cells = worksheet.findall(str(idnumber))
        for cell in all_cells:
            if cell.col == id_col_index + 1:
                return worksheet.row_values(cell.row), cell.row
    except Exception as e:
        logging.error(f"[get_row_by_id] {e}")
    return None, None

def get_invoice_reminder_data():
    try:
        worksheet = get_cyc_worksheet()
        rows = worksheet.get_all_records()
        header_row = worksheet.row_values(1)
        header_dict = {h.strip().upper(): h for h in header_row}

        kolom_status = next((h for h in header_row if "STATUS" in h.upper()), None)
        if not kolom_status:
            logging.warning("Kolom 'STATUS' tidak ditemukan")
            return []

        bulan_map = {
            "JANUARY": "JANUARI", "FEBRUARY": "FEBRUARI", "MARCH": "MARET",
            "APRIL": "APRIL", "MAY": "MEI", "JUNE": "JUNI", "JULY": "JULI",
            "AUGUST": "AGUSTUS", "SEPTEMBER": "SEPTEMBER", "OCTOBER": "OKTOBER",
            "NOVEMBER": "NOVEMBER", "DECEMBER": "DESEMBER"
        }

        bulan_inggris = datetime.now().strftime("%B").upper()
        bulan_indo = bulan_map.get(bulan_inggris, bulan_inggris)
        kolom_bulan_norm = f"CYC {bulan_indo}".upper()

        if kolom_bulan_norm not in header_dict:
            logging.warning(f"Kolom '{kolom_bulan_norm}' tidak ditemukan. Header: {header_row}")
            return []

        kolom_bulan_asli = header_dict[kolom_bulan_norm]

        result = []
        for row in rows:
            status_val = str(row.get(kolom_status, "")).strip().upper()
            if status_val == "PU":
                result.append({
                    "idnumber": row.get("IdNumber", ""),
                    "nama": row.get("BP Name", ""),
                    "am": str(row.get("AM", "")).strip(),
                    "bulan": bulan_indo.capitalize(),
                    "nilai": row.get(kolom_bulan_asli, ""),
                    "status": status_val
                })
        return result
    except Exception as e:
        logging.error(f"[get_invoice_reminder_data] {e}")
        return []

def update_keterangan_by_id(idnumber, keterangan):
    try:
        worksheet = get_cyc_worksheet()
        header_row = worksheet.row_values(1)

        kolom_keterangan_idx = get_column_index(header_row, "Keterangan")
        if kolom_keterangan_idx is None:
            raise ValueError("Kolom 'Keterangan' tidak ditemukan")

        kolom_update_idx = get_column_index(header_row, "Last Update")
        if kolom_update_idx is None:
            kolom_update_idx = len(header_row)
            worksheet.update_cell(1, kolom_update_idx + 1, "Last Update")

        row_values, row_index = get_row_by_id(worksheet, idnumber)
        if row_values and row_index:
            WIB = timezone(timedelta(hours=7))
            timestamp = datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S')

            worksheet.update_cell(row_index, kolom_keterangan_idx + 1, keterangan)
            worksheet.update_cell(row_index, kolom_update_idx + 1, timestamp)
    except Exception as e:
        logging.error(f"[update_keterangan_by_id] {e}")

def get_keterangan_by_id(idnumber):
    try:
        worksheet = get_cyc_worksheet()
        header_row = worksheet.row_values(1)

        kolom_keterangan_idx = get_column_index(header_row, "Keterangan")
        kolom_nama_idx = get_column_index(header_row, "BP Name")

        row_values, _ = get_row_by_id(worksheet, idnumber)
        if row_values:
            keterangan = row_values[kolom_keterangan_idx] if kolom_keterangan_idx is not None and kolom_keterangan_idx < len(row_values) else ""
            nama = row_values[kolom_nama_idx] if kolom_nama_idx is not None and kolom_nama_idx < len(row_values) else ""
            return {"keterangan": keterangan, "nama": nama}
    except Exception as e:
        logging.error(f"[get_keterangan_by_id] {e}")
    return {"keterangan": "", "nama": ""}

def get_bp_name_by_id(idnumber):
    try:
        worksheet = get_cyc_worksheet()
        header_row = worksheet.row_values(1)
        kolom_nama_idx = get_column_index(header_row, "BP Name")

        row_values, _ = get_row_by_id(worksheet, idnumber)
        if row_values and kolom_nama_idx is not None and kolom_nama_idx < len(row_values):
            return row_values[kolom_nama_idx] or "Tidak diketahui"
    except Exception as e:
        logging.error(f"[get_bp_name_by_id] {e}")
    return "Tidak ditemukan"


'''
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
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet("CYC 2025")
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

    # ⛳ UJI BULAN AGUSTUS —> Ubah ke bulan lain jika ingin simulasi
    bulan_inggris = "AUGUST"
    print(f"[TESTING] Simulasi bulan: {bulan_inggris}")

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
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet("CYC 2025")
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
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet("CYC 2025")
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
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet("CYC 2025")
    try:
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
'''