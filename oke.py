import os
import sys
import sqlite3
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTabWidget,
    QHeaderView
)

from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt

def resource_path(relative_path):
    
    """
    Mengembalikan path absolut untuk file resource.
    Digunakan agar aplikasi tetap bisa membaca file
    saat sudah dikompilasi menjadi .exe dengan PyInstaller.
    """
    try:
        base_path = sys._MEIPASS   # saat jadi EXE
    except Exception:
        base_path = os.path.abspath(".")  # saat .py

    return os.path.join(base_path, relative_path)



# ================= UTIL =================
def format_rupiah(angka):
    return f"{angka:,}".replace(",", ".")
    
    """
    Mengubah angka integer menjadi format rupiah
    Contoh: 1000000 -> 1.000.000
    """

def clean_angka(text):
    return int(text.replace(".", "").replace(",", ""))

    """
    Membersihkan format angka rupiah menjadi integer
    Contoh: '1.000.000' -> 1000000
    """
# ================= DATABASE =================
class Database:
    """
    Class Database berfungsi sebagai MODEL.
    Mengatur koneksi SQLite dan pembuatan tabel.
    """
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()

        # Tabel produk
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT,
                kategori TEXT,
                ukuran TEXT,
                warna TEXT,
                harga INTEGER,
                stok INTEGER
            )
        """)

        # Tabel user
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

        # User default
        self.cursor.execute("""
            INSERT OR IGNORE INTO users (username, password)
            VALUES ('admin', 'admin')
        """)
        # Tabel transaksi / keuangan
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT,
                total INTEGER,
                bayar INTEGER,
                kembali INTEGER
            )
        """)


        self.conn.commit()
        
        

db = Database()


# ================= LOGIN DIALOG =================
class LoginDialog(QDialog):
    
    """
    Dialog login untuk autentikasi user.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login User")
        self.setWindowIcon(QPixmap(resource_path("logo.png")))
        self.setFixedSize(350, 420)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        logo.setPixmap(QPixmap(resource_path("logo.png")).scaled(120, 120, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)

        title = QLabel("LOGIN APLIKASI")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")

        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("Password")
        self.pwd.setEchoMode(QLineEdit.Password)

        btn = QPushButton("Login")
        btn.setMinimumHeight(25)
        btn.setStyleSheet("background:#4CAF50;color:white;font-weight:bold;border-radius:10px;")
        btn.clicked.connect(self.login)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(self.user)
        layout.addWidget(self.pwd)
        layout.addSpacing(10)
        layout.addWidget(btn)

    def login(self):
        
        """
        Mengecek username dan password ke database.
        Jika benar, dialog ditutup dan aplikasi utama terbuka.
        """
        
        u = self.user.text()
        p = self.pwd.text()

        db.cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, p)
        )
        if db.cursor.fetchone():
            self.accept()
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau Password salah")


# ================= STRUK =================
class StrukDialog(QDialog):
    
    """
    Dialog untuk menampilkan struk transaksi.
    """
    def __init__(self, text):
        super().__init__()
        self.setWindowTitle("Struk Transaksi")
        self.setFixedSize(400, 400)

        layout = QVBoxLayout(self)

        lbl = QLabel(text)
        lbl.setFont(QFont("Consolas", 10))
        lbl.setAlignment(Qt.AlignTop)
        lbl.setWordWrap(True)

        layout.addWidget(lbl)

        btn = QPushButton("Tutup")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)



# ================= MAIN APP =================
class App(QMainWindow):
    
    """
    Window utama aplikasi kasir dan manajemen stok.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kasir & Stok Toko Fashion")
        self.setWindowIcon(QPixmap(resource_path("logo.png")))
        self.setGeometry(100, 100, 1200, 650)

        self.cart = []
        self.id = None

        self.init_ui()
        self.load_data()

    # ================= UI =================
    def init_ui(self):
        
        """
        Membuat tampilan utama dan tab aplikasi.
        """
        central = QWidget()
        main = QVBoxLayout(central)

        # ===== HEADER =====
        header = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap(resource_path("logo.png")).scaled(60, 60, Qt.KeepAspectRatio))
        header.addWidget(logo)

        title = QLabel("Aplikasi Kasir & Stok Toko Fashion")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        main.addLayout(header)

        # ===== TAB =====
        tabs = QTabWidget()
        main.addWidget(tabs)

        tabs.addTab(self.tab_produk(), "📦 Manajemen Produk")
        tabs.addTab(self.tab_kasir(), "🛒 Transaksi")
        tabs.addTab(self.tab_keuangan(), "📊 Keuangan")


        self.setCentralWidget(central)

    # ================= TAB PRODUK =================
    def tab_produk(self):
        
        """
        Memuat data produk dari database ke tabel dan combobox kasir.
        """
        
        w = QWidget()
        layout = QHBoxLayout(w)

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

        for l, wgt in [
            ("Nama", self.nama),
            ("Kategori", self.kategori),
            ("Ukuran", self.ukuran),
            ("Warna", self.warna),
            ("Harga", self.harga),
            ("Stok", self.stok),
        ]:
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
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nama", "Kategori", "Ukuran", "Warna", "Harga", "Stok"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.load_form)

        layout.addLayout(form, 3)
        layout.addWidget(self.table, 7)
        return w

    # ================= TAB KASIR =================
    def tab_kasir(self):
        
        """
        Menambahkan data produk baru ke database.
        """
        
        w = QWidget()
        kasir = QVBoxLayout(w)

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

        return w
    def tab_keuangan(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.table_keu = QTableWidget()
        self.table_keu.setColumnCount(5)
        self.table_keu.setHorizontalHeaderLabels(
            ["ID", "Tanggal", "Total", "Bayar", "Kembali"]
        )
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

        btn_pdf.clicked.connect(self.export_pdf)
        btn_excel.clicked.connect(self.export_excel)

        layout.addWidget(btn_pdf)
        layout.addWidget(btn_excel)

        self.load_keuangan()

        return w

    # ================= FUNGSI =================
    def load_data(self):
        self.table.setRowCount(0)
        self.cb.clear()

        for row in db.cursor.execute("SELECT * FROM produk"):
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, v in enumerate(row):
                if c == 5:
                    v = format_rupiah(v)
                self.table.setItem(r, c, QTableWidgetItem(str(v)))

        for r in db.cursor.execute("SELECT id,nama,harga,stok FROM produk"):
            self.cb.addItem(f"{r[1]} | {format_rupiah(r[2])} | stok:{r[3]}", r)

    def load_form(self, row, col):
        self.id = self.table.item(row, 0).text()
        self.nama.setText(self.table.item(row, 1).text())
        self.kategori.setCurrentText(self.table.item(row, 2).text())
        self.ukuran.setCurrentText(self.table.item(row, 3).text())
        self.warna.setCurrentText(self.table.item(row, 4).text())
        self.harga.setText(self.table.item(row, 5).text())
        self.stok.setText(self.table.item(row, 6).text())

    def add_data(self):
        db.cursor.execute(
            "INSERT INTO produk VALUES (NULL,?,?,?,?,?,?)",
            (self.nama.text(), self.kategori.currentText(),
             self.ukuran.currentText(), self.warna.currentText(),
             clean_angka(self.harga.text()), int(self.stok.text()))
        )
        db.conn.commit()
        self.load_data()

    def edit_data(self):
        if not self.id:
            return
        db.cursor.execute(
            "UPDATE produk SET nama=?,kategori=?,ukuran=?,warna=?,harga=?,stok=? WHERE id=?",
            (self.nama.text(), self.kategori.currentText(),
             self.ukuran.currentText(), self.warna.currentText(),
             clean_angka(self.harga.text()), int(self.stok.text()), self.id)
        )
        db.conn.commit()
        self.load_data()

    def delete_data(self):
        if not self.id:
            return
        if QMessageBox.question(self, "Hapus", "Yakin hapus data?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            db.cursor.execute("DELETE FROM produk WHERE id=?", (self.id,))
            db.conn.commit()
            self.load_data()

    def add_cart(self):
        data = self.cb.currentData()
        if not data or not self.qty.text().isdigit():
            return
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
        
    def load_keuangan(self):
        self.table_keu.setRowCount(0)
        total = 0

        for row in db.cursor.execute("SELECT * FROM transaksi"):
            r = self.table_keu.rowCount()
            self.table_keu.insertRow(r)
            for c, v in enumerate(row):
                if c >= 2:
                    v = format_rupiah(v)
                self.table_keu.setItem(r, c, QTableWidgetItem(str(v)))
            total += row[2]

        self.lbl_pemasukan.setText(f"Total Pemasukan : Rp {format_rupiah(total)}")

    def export_pdf(self):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm

        file = "laporan_keuangan.pdf"
        c = canvas.Canvas(file, pagesize=letter)

    # ================= HEADER =================
        header_top = 770
        logo_y = 735
        logo_height = 60
        logo_width = 120

        logo_path = resource_path("logo.png")

        if os.path.exists(logo_path):
            c.drawImage(
                logo_path,
                40, logo_y,
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask="auto"
            )


        c.setFont("Helvetica-Bold", 16)
        c.drawString(180, header_top, "TOKO FASHION APIM")

        c.setFont("Helvetica", 11)
        c.drawString(180, header_top - 18, "Jl. DR WAHIDIN GG REVOLUSI AA.37")
        c.drawString(180, header_top - 34, "Telp: 0812-3456-7890")

        c.line(40, header_top - 50, 570, header_top - 50)

        c.setFont("Helvetica-Bold", 13)
        c.drawString(40, header_top - 70, "LAPORAN KEUANGAN")

        c.setFont("Helvetica", 10)
        c.drawString(40, header_top - 82, "==============================================")

    # ================= TABEL =================
        y = header_top - 100

        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y, "ID")
        c.drawString(80, y, "Tanggal")
        c.drawString(200, y, "Total")
        c.drawString(270, y, "Bayar")
        c.drawString(340, y, "Kembali")

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

    # ================= FOOTER =================
        c.line(40, y, 570, y)
        y -= 25

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, f"TOTAL PEMASUKAN : Rp {format_rupiah(total_pemasukan)}")

        c.save()

        QMessageBox.information(self, "Export Berhasil", "PDF laporan keuangan berhasil dibuat!")



    def export_excel(self):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Laporan"

        ws.append(["ID", "Tanggal", "Total", "Bayar", "Kembali"])

        for row in db.cursor.execute("SELECT * FROM transaksi"):
            ws.append(list(row))

        wb.save("laporan_keuangan.xlsx")

        QMessageBox.information(self, "Export Berhasil", "Laporan berhasil disimpan sebagai Excel")


    def pay(self):
        
        """
        Memproses transaksi penjualan:
        - Menghitung total
        - Update stok
        - Simpan transaksi
        - Menampilkan struk
        """
        
        if not self.cart or not self.bayar.text():
            return

        total = sum(i["sub"] for i in self.cart)
        bayar = clean_angka(self.bayar.text())

        if bayar < total:
            QMessageBox.warning(self, "Error", "Uang bayar kurang")
            return

        # Update stok
        for i in self.cart:
            db.cursor.execute(
                "UPDATE produk SET stok = stok - ? WHERE id = ?",
                (i["qty"], i["id"])
            )
        db.conn.commit()

        # ===== STRUK =====
        lines = []
        lines.append("TOKO FASHION")
        lines.append("--------------------")

        for i in self.cart:
            line = f"{i['nama'].upper()} x{i['qty']} = {format_rupiah(i['sub'])}"
            lines.append(line)

        lines.append("--------------------")
        lines.append(f"Total   : {format_rupiah(total)}")
        lines.append(f"Bayar   : {format_rupiah(bayar)}")
        lines.append(f"Kembali : {format_rupiah(bayar - total)}")
        lines.append(f"Tanggal : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("Terima Kasih")

        struk_text = "\n".join(lines)

        StrukDialog(struk_text).exec()
        
                # Simpan transaksi ke keuangan
        db.cursor.execute(
            "INSERT INTO transaksi VALUES (NULL,?,?,?,?)",
            (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total,
                bayar,
                bayar - total
            )
        )
        db.conn.commit()

        self.load_keuangan()


        # Reset
        self.cart.clear()
        self.refresh_cart()
        self.load_data()
        self.bayar.clear()



# ================= RUN =================
app = QApplication(sys.argv)
login = LoginDialog()
if login.exec() == QDialog.Accepted:
    win = App()
    win.show()
    sys.exit(app.exec())