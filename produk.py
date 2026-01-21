from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView
)
from database import db
from utils import format_rupiah, clean_angka

class ProdukTab(QWidget):
    def __init__(self):
        super().__init__()
        self.id = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout(self)
        form = QVBoxLayout()
        
        self.nama = QLineEdit()
        self.kategori = QComboBox()
        self.kategori.addItems(["Atasan", "Bawahan", "Aksesoris"])
        self.ukuran = QComboBox()
        self.ukuran.addItems(["S", "M", "L", "XL", "Oversize", "Tidak Ada"])
        self.warna = QComboBox()
        self.warna.addItems(["Hitam", "Putih", "Biru", "Jeans", "Coklat"])
        self.harga = QLineEdit()
        self.stok = QLineEdit()

        fields = [("Nama", self.nama), ("Kategori", self.kategori), 
                  ("Ukuran", self.ukuran), ("Warna", self.warna), 
                  ("Harga", self.harga), ("Stok", self.stok)]
        
        for l, wgt in fields:
            form.addWidget(QLabel(l))
            form.addWidget(wgt)

        btn_add = QPushButton("➕ Tambah")
        btn_edit = QPushButton("✏️ Edit")
        btn_del = QPushButton("🗑️ Hapus")

        btn_add.clicked.connect(self.add_data)
        btn_edit.clicked.connect(self.edit_data)
        btn_del.clicked.connect(self.delete_data)

        btn_add.setStyleSheet("background:#4CAF50;color:white;border-radius:12px;font-weight:bold;")
        btn_edit.setStyleSheet("background:#FFC107;color:black;border-radius:12px;font-weight:bold;")
        btn_del.setStyleSheet("background:#F44336;color:white;border-radius:12px;font-weight:bold;")

        for b in (btn_add, btn_edit, btn_del):
            b.setMinimumHeight(25)
            form.addWidget(b)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Kategori", "Ukuran", "Warna", "Harga", "Stok"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.load_form)

        layout.addLayout(form, 3)
        layout.addWidget(self.table, 7)

    def load_data(self):
        self.table.setRowCount(0)
        for row in db.cursor.execute("SELECT * FROM produk"):
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, v in enumerate(row):
                if c == 5: v = format_rupiah(v)
                self.table.setItem(r, c, QTableWidgetItem(str(v)))

    def load_form(self, row, col):
        self.id = self.table.item(row, 0).text()
        self.nama.setText(self.table.item(row, 1).text())
        self.kategori.setCurrentText(self.table.item(row, 2).text())
        self.ukuran.setCurrentText(self.table.item(row, 3).text())
        self.warna.setCurrentText(self.table.item(row, 4).text())
        self.harga.setText(self.table.item(row, 5).text())
        self.stok.setText(self.table.item(row, 6).text())

    def add_data(self):
        db.cursor.execute("INSERT INTO produk VALUES (NULL,?,?,?,?,?,?)",
            (self.nama.text(), self.kategori.currentText(), self.ukuran.currentText(),
             self.warna.currentText(), clean_angka(self.harga.text()), int(self.stok.text())))
        db.conn.commit()
        self.load_data()

    def edit_data(self):
        if not self.id: return
        db.cursor.execute("UPDATE produk SET nama=?,kategori=?,ukuran=?,warna=?,harga=?,stok=? WHERE id=?",
            (self.nama.text(), self.kategori.currentText(), self.ukuran.currentText(),
             self.warna.currentText(), clean_angka(self.harga.text()), int(self.stok.text()), self.id))
        db.conn.commit()
        self.load_data()

    def delete_data(self):
        if not self.id: return
        if QMessageBox.question(self, "Hapus", "Yakin hapus?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            db.cursor.execute("DELETE FROM produk WHERE id=?", (self.id,))
            db.conn.commit()
            self.load_data()