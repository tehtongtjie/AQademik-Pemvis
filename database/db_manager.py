from supabase import create_client
from dotenv import load_dotenv
import os
import bcrypt
import re

# ==========================================================================
# ─── KONFIGURASI SUPABASE ─────────────────────────────────────────────────
# ==========================================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==========================================================================
# ─── PASSWORD HASHING ─────────────────────────────────────────────────────
# ==========================================================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ==========================================================================
# ─── VALIDASI ─────────────────────────────────────────────────────────────
# ==========================================================================

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", email))

def validate_register_input(nama, nim_nip, email, password, role):
    if not all([nama, nim_nip, email, password]):
        return False, "Semua field harus diisi."
    if len(nama) < 3:
        return False, "Nama minimal 3 karakter."
    if not is_valid_email(email):
        return False, "Format email tidak valid."
    if len(password) < 6:
        return False, "Password minimal 6 karakter."
    if role not in ("mahasiswa", "dosen"):
        return False, "Role tidak valid."
    return True, ""


# ==========================================================================
# ─── REGISTER ─────────────────────────────────────────────────────────────
# ==========================================================================

def register_user(nama: str, nim_nip: str, email: str, password: str, role: str):
    nama     = nama.strip()
    nim_nip  = nim_nip.strip()
    email    = email.strip().lower()
    password = password.strip()

    valid, err = validate_register_input(nama, nim_nip, email, password, role)
    if not valid:
        return False, err

    try:
        # Cek email sudah terdaftar
        cek_email = supabase.table("users").select("id").eq("email", email).execute()
        if cek_email.data:
            return False, "Email sudah terdaftar."

        # Cek NIM/NIP sudah terdaftar
        cek_nim = supabase.table("users").select("id").eq("nim_nip", nim_nip).execute()
        if cek_nim.data:
            return False, "NIM/NIP sudah terdaftar."

        # Simpan ke Supabase
        supabase.table("users").insert({
            "nama":     nama,
            "nim_nip":  nim_nip,
            "email":    email,
            "password": hash_password(password),
            "role":     role
        }).execute()

        return True, "Registrasi berhasil!"

    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"


# ==========================================================================
# ─── LOGIN ────────────────────────────────────────────────────────────────
# ==========================================================================

def login_user(email: str, password: str):
    email    = email.strip().lower()
    password = password.strip()

    if not email or not password:
        return False, "Email dan password harus diisi."
    if not is_valid_email(email):
        return False, "Format email tidak valid."

    try:
        res = supabase.table("users").select("*").eq("email", email).execute()

        if not res.data:
            return False, "Email atau password salah."

        user = res.data[0]

        if not verify_password(password, user["password"]):
            return False, "Email atau password salah."

        return True, user

    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"