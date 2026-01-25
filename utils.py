import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS   # saat jadi EXE
    except Exception:
        base_path = os.path.abspath(".")  # saat .py
    return os.path.join(base_path, relative_path)

def format_rupiah(angka):
    return f"{angka:,}".replace(",", ".")

def clean_angka(text):
    try:
        return int(text.replace(".", "").replace(",", ""))
    except ValueError:
        return 0