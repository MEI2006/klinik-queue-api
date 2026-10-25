
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "klinik.db"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS queues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pasien TEXT NOT NULL,
            poli TEXT NOT NULL,
            keluhan TEXT NOT NULL DEFAULT '',
            tanggal TEXT NOT NULL,
            nomor_antrian INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'menunggu'
                CHECK (status IN (
                    'menunggu', 'dipanggil', 'dilayani',
                    'selesai', 'dibatalkan'
                )),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (tanggal, poli, nomor_antrian)
        );
    """)
    connection.commit()

    try:
        yield connection
    finally:
        connection.close()
