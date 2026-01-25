import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        # Tabel produk
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT, kategori TEXT, ukuran TEXT, warna TEXT,
                harga INTEGER, stok INTEGER
            )
        """)
        # Tabel user
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE, password TEXT
            )
        """)
        # User default
        self.cursor.execute("""
            INSERT OR IGNORE INTO users (username, password)
            VALUES ('admin', 'admin')
        """)
        # Tabel transaksi
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT, total INTEGER, bayar INTEGER, kembali INTEGER
            )
        """)
        self.conn.commit()

# Instance db global yang akan di-import file lain
db = Database()