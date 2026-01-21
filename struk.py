from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class StrukDialog(QDialog):
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