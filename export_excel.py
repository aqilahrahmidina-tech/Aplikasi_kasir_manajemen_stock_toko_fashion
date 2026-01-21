from PySide6.QtWidgets import QMessageBox
from openpyxl import Workbook
from database import db

def generate_excel(parent):
    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan"
    ws.append(["ID", "Tanggal", "Total", "Bayar", "Kembali"])

    for row in db.cursor.execute("SELECT * FROM transaksi"):
        ws.append(list(row))

    wb.save("laporan_keuangan.xlsx")
    QMessageBox.information(parent, "Export Berhasil", "Laporan berhasil disimpan sebagai Excel")