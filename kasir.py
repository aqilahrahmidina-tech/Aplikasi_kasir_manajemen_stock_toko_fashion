from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtGui import QFont
from database import db
from utils import format_rupiah, clean_angka
from struk import StrukDialog

class KasirTab(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = []
        self.init_ui()
        self.load_products()

    def init_ui(self):
        kasir = QVBoxLayout(self)
        
        self.cb = QComboBox()
        self.qty = QLineEdit()
        self.bayar = QLineEdit()

        kasir.addWidget(QLabel("Pilih Produk"))
        kasir.addWidget(self.cb)
        kasir.addWidget(QLabel("Jumlah"))
        kasir.addWidget(self.qty)

        btn_cart = QPushButton("🛒 Tambah Item")
        btn_cart.clicked.connect(self.add_cart)
        btn_cart.setStyleSheet("background:#2196F3;color:white;border-radius:12px;font-weight:bold;")
        btn_cart.setMinimumHeight(25)
        kasir.addWidget(btn_cart)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(3)
        self.cart_table.setHorizontalHeaderLabels(["Produk", "Qty", "Subtotal"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        kasir.addWidget(self.cart_table)

        self.lbl_total = QLabel("Total : 0")
        self.lbl_total.setFont(QFont("Arial", 12, QFont.Bold))
        kasir.addWidget(self.lbl_total)

        kasir.addWidget(QLabel("Uang Bayar"))
        kasir.addWidget(self.bayar)

        btn_pay = QPushButton("💳 Proses Transaksi")
        btn_pay.clicked.connect(self.pay)
        btn_pay.setStyleSheet("background:#673AB7;color:white;border-radius:12px;font-weight:bold;")
        btn_pay.setMinimumHeight(25)
        kasir.addWidget(btn_pay)

    def load_products(self):
        self.cb.clear()
        for r in db.cursor.execute("SELECT id,nama,harga,stok FROM produk"):
            self.cb.addItem(f"{r[1]} | {format_rupiah(r[2])} | stok:{r[3]}", r)

    def add_cart(self):
        data = self.cb.currentData()
        if not data or not self.qty.text().isdigit(): return
        idp, nama, harga, stok = data
        q = int(self.qty.text())
        if q > stok:
            QMessageBox.warning(self, "Error", "Stok tidak cukup")
            return
        self.cart.append({"id": idp, "nama": nama, "qty": q, "sub": harga * q})
        self.refresh_cart()

    def refresh_cart(self):
        self.cart_table.setRowCount(0)
        for i in self.cart:
            r = self.cart_table.rowCount()
            self.cart_table.insertRow(r)
            self.cart_table.setItem(r, 0, QTableWidgetItem(i["nama"]))
            self.cart_table.setItem(r, 1, QTableWidgetItem(str(i["qty"])))
            self.cart_table.setItem(r, 2, QTableWidgetItem(format_rupiah(i["sub"])))
        self.lbl_total.setText(f"Total : {format_rupiah(sum(i['sub'] for i in self.cart))}")

    def pay(self):
        if not self.cart or not self.bayar.text(): return
        total = sum(i["sub"] for i in self.cart)
        bayar = clean_angka(self.bayar.text())

        if bayar < total:
            QMessageBox.warning(self, "Error", "Uang bayar kurang")
            return

        for i in self.cart:
            db.cursor.execute("UPDATE produk SET stok = stok - ? WHERE id = ?", (i["qty"], i["id"]))
        db.conn.commit()

        # Struk logic
        lines = ["TOKO FASHION", "--------------------"]
        for i in self.cart:
            lines.append(f"{i['nama'].upper()} x{i['qty']} = {format_rupiah(i['sub'])}")
        lines.append("--------------------")
        lines.append(f"Total   : {format_rupiah(total)}")
        lines.append(f"Bayar   : {format_rupiah(bayar)}")
        lines.append(f"Kembali : {format_rupiah(bayar - total)}")
        lines.append(f"Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\nTerima Kasih")
        
        StrukDialog("\n".join(lines)).exec()

        db.cursor.execute("INSERT INTO transaksi VALUES (NULL,?,?,?,?)",
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), total, bayar, bayar - total))
        db.conn.commit()

        self.cart.clear()
        self.refresh_cart()
        self.bayar.clear()
        self.load_products() # Refresh stok di combo box