from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from utils import resource_path
from database import db

class LoginDialog(QDialog):
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
        u = self.user.text()
        p = self.pwd.text()
        db.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        if db.cursor.fetchone():
            self.accept()
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau Password salah")