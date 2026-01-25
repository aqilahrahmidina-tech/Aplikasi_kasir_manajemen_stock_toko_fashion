import os
from PySide6.QtWidgets import QMessageBox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from utils import resource_path, format_rupiah
from database import db

def generate_pdf(parent):
    file_name = "laporan_keuangan.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)

    # HEADER
    header_top = 770
    logo_y = 735
    logo_path = resource_path("logo.png")

    if os.path.exists(logo_path):
        c.drawImage(logo_path, 40, logo_y, width=120, height=60, preserveAspectRatio=True, mask="auto")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, header_top, "TOKO FASHION JAYA")
    c.setFont("Helvetica", 11)
    c.drawString(180, header_top - 18, "Jl. Contoh Alamat No.12, Jakarta")
    c.drawString(180, header_top - 34, "Telp: 0812-3456-7890")
    c.line(40, header_top - 50, 570, header_top - 50)
    
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, header_top - 70, "LAPORAN KEUANGAN")
    c.setFont("Helvetica", 10)
    c.drawString(40, header_top - 82, "==============================================")

    # TABEL
    y = header_top - 100
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "ID"); c.drawString(80, y, "Tanggal")
    c.drawString(200, y, "Total"); c.drawString(270, y, "Bayar"); c.drawString(340, y, "Kembali")

    y -= 15
    c.line(40, y, 570, y)
    y -= 15
    
    total_pemasukan = 0
    c.setFont("Helvetica", 10)

    for row in db.cursor.execute("SELECT * FROM transaksi"):
        idt, tanggal, total, bayar, kembali = row
        c.drawString(40, y, str(idt))
        c.drawString(80, y, str(tanggal))
        c.drawString(200, y, format_rupiah(total))
        c.drawString(270, y, format_rupiah(bayar))
        c.drawString(340, y, format_rupiah(kembali))
        total_pemasukan += total
        y -= 20
        if y < 80:
            c.showPage()
            y = 750

    c.line(40, y, 570, y)
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, f"TOTAL PEMASUKAN : Rp {format_rupiah(total_pemasukan)}")
    
    c.save()
    QMessageBox.information(parent, "Export Berhasil", "PDF laporan keuangan berhasil dibuat!")