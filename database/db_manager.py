import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "akademiq.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Mengamankan password menggunakan SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Membuat tabel users jika belum ada."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nim_nip TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('mahasiswa', 'dosen')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def register_user(nama: str, nim_nip: str, email: str, password: str, role: str):
    """
    Register user baru. 
    Secara otomatis membersihkan spasi berlebih dan mengecilkan format huruf email.
    """
    # Bersihkan spasi di awal/akhir dan normalkan input
    nama = nama.strip()
    nim_nip = nim_nip.strip()
    email = email.strip().lower()  # Mengubah email jadi huruf kecil semua agar tidak sensitif kapital
    password = password.strip()

    if not nama or not nim_nip or not email or not password:
        return False, "Semua field harus diisi."
    if role not in ("mahasiswa", "dosen"):
        return False, "Role tidak valid."
    if len(password) < 6:
        return False, "Password minimal 6 karakter."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (nama, nim_nip, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (nama, nim_nip, email, hash_password(password), role),
        )
        conn.commit()
        return True, "Registrasi berhasil!"
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "nim_nip" in err_msg:
            return False, "NIM/NIP sudah terdaftar."
        elif "email" in err_msg:
            return False, "Email sudah terdaftar."
        return False, "Data sudah terdaftar."
    finally:
        conn.close()


def login_user(email: str, password: str):
    """
    Login user menggunakan email dan password.
    Return (True, user_dict) atau (False, "pesan error").
    """
    email = email.strip().lower()  # Disamakan dengan format register (huruf kecil)
    password = password.strip()

    if not email or not password:
        return False, "Email dan password harus diisi."

    conn = get_connection()
    cursor = conn.cursor()
    
    # Mencari user berdasarkan email dan password yang sudah di-hash
    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, hash_password(password)),
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return True, dict(user)
    return False, "Email atau password salah."


# Inisialisasi DB saat modul diimpor
init_db()