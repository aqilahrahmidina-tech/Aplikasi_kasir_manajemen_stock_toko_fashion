import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt

from utils import resource_path
from login import LoginDialog
from produk import ProdukTab
from kasir import KasirTab
from keuangan import KeuanganTab
from database import db

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kasir & Stok Toko Fashion")
        self.setWindowIcon(QPixmap(resource_path("logo.png")))
        self.setGeometry(100, 100, 1200, 650)
        self.init_ui()

    def init_ui(self):
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
        self.tabs = QTabWidget()
        main.addWidget(self.tabs)

        # Inisialisasi Tab
        self.tab_produk_ui = ProdukTab()
        self.tab_kasir_ui = KasirTab()
        self.tab_keuangan_ui = KeuanganTab()

        self.tabs.addTab(self.tab_produk_ui, "📦 Manajemen Produk")
        self.tabs.addTab(self.tab_kasir_ui, "🛒 Transaksi")
        self.tabs.addTab(self.tab_keuangan_ui, "📊 Keuangan")

        # Event saat pindah tab agar data selalu update
        self.tabs.currentChanged.connect(self.on_tab_change)

        self.setCentralWidget(central)

    def on_tab_change(self, index):
        # Refresh data ketika tab dibuka
        if index == 0:
            self.tab_produk_ui.load_data()
        elif index == 1:
            self.tab_kasir_ui.load_products()
        elif index == 2:
            self.tab_keuangan_ui.load_keuangan()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Cek login dulu
    login = LoginDialog()
    if login.exec() == LoginDialog.Accepted:
        win = App()
        win.show()
        sys.exit(app.exec())
    else:
        sys.exit()