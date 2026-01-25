from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QFont
from database import db
from utils import format_rupiah
from export_pdf import generate_pdf
from export_excel import generate_excel

class KeuanganTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_keuangan()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.table_keu = QTableWidget()
        self.table_keu.setColumnCount(5)
        self.table_keu.setHorizontalHeaderLabels(["ID", "Tanggal", "Total", "Bayar", "Kembali"])
        self.table_keu.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(QLabel("Riwayat Transaksi"))
        layout.addWidget(self.table_keu)

        self.lbl_pemasukan = QLabel("Total Pemasukan : 0")
        self.lbl_pemasukan.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.lbl_pemasukan)

        btn_pdf = QPushButton("📄 Export PDF")
        btn_excel = QPushButton("📊 Export Excel")
        btn_pdf.setStyleSheet("background:#E91E63;color:white;border-radius:10px;font-weight:bold;")
        btn_excel.setStyleSheet("background:#3F51B5;color:white;border-radius:10px;font-weight:bold;")

        btn_pdf.clicked.connect(lambda: generate_pdf(self))
        btn_excel.clicked.connect(lambda: generate_excel(self))

        layout.addWidget(btn_pdf)
        layout.addWidget(btn_excel)

    def load_keuangan(self):
        self.table_keu.setRowCount(0)
        total = 0
        for row in db.cursor.execute("SELECT * FROM transaksi"):
            r = self.table_keu.rowCount()
            self.table_keu.insertRow(r)
            for c, v in enumerate(row):
                if c >= 2: v = format_rupiah(v)
                self.table_keu.setItem(r, c, QTableWidgetItem(str(v)))
            total += row[2]
        self.lbl_pemasukan.setText(f"Total Pemasukan : Rp {format_rupiah(total)}")