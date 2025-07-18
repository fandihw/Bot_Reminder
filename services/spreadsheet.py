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

def get_keterangan_updates_by_date(target_date):
    """Ambil semua update keterangan yang terjadi pada tanggal tertentu (YYYY-MM-DD)"""
    try:
        worksheet = get_cyc_worksheet()
        header_row = worksheet.row_values(1)
        kolom_update_idx = get_column_index(header_row, "Last Update")
        kolom_am_idx = get_column_index(header_row, "AM")
        kolom_nama_idx = get_column_index(header_row, "BP Name")

        if None in (kolom_update_idx, kolom_am_idx, kolom_nama_idx):
            raise ValueError("Kolom yang dibutuhkan tidak lengkap")

        all_rows = worksheet.get_all_values()[1:]  # skip header
        result = {}

        if isinstance(target_date, datetime):
            target_date_str = target_date.strftime("%Y-%m-%d")
        else:
            target_date_str = str(target_date)

        for row in all_rows:
            if kolom_update_idx >= len(row):
                continue
            last_update = row[kolom_update_idx].strip()

            if not last_update.startswith(target_date_str):
                continue

            # ✅ Normalize nama AM
            am = row[kolom_am_idx].strip().upper() if kolom_am_idx < len(row) else "TIDAK DIKETAHUI"
            nama_pelanggan = row[kolom_nama_idx].strip() if kolom_nama_idx < len(row) else "Tanpa nama"

            if am not in result:
                result[am] = []
            result[am].append(nama_pelanggan)

        return result
    except Exception as e:
        logging.error(f"[get_keterangan_updates_by_date] {e}")
        return {}
