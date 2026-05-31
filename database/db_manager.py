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
        cek_email = supabase.table("users").select("id").eq("email", email).execute()
        if cek_email.data:
            return False, "Email sudah terdaftar."

        cek_nim = supabase.table("users").select("id").eq("nim_nip", nim_nip).execute()
        if cek_nim.data:
            return False, "NIM/NIP sudah terdaftar."

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


# ==========================================================================
# ─── UPLOAD PDF MAHASISWA (kumpul tugas) ──────────────────────────────────
# ==========================================================================

def submit_tugas(tugas_id: int, mahasiswa_id: int, file_path: str, catatan: str = ""):
    """Mahasiswa upload PDF untuk mengumpulkan tugas."""
    try:
        file_name    = os.path.basename(file_path)
        storage_path = f"{mahasiswa_id}/{tugas_id}/{file_name}"

        with open(file_path, "rb") as f:
            supabase.storage.from_("tugas-files").upload(
                path=storage_path,
                file=f,
                file_options={"content-type": "application/pdf"}
            )

        file_url = supabase.storage.from_("tugas-files").get_public_url(storage_path)

        cek = supabase.table("pengumpulan_tugas") \
                      .select("id") \
                      .eq("tugas_id", tugas_id) \
                      .eq("mahasiswa_id", mahasiswa_id) \
                      .execute()

        if cek.data:
            supabase.table("pengumpulan_tugas").update({
                "file_url":  file_url,
                "file_name": file_name,
                "status":    "selesai",
                "catatan":   catatan
            }).eq("tugas_id", tugas_id).eq("mahasiswa_id", mahasiswa_id).execute()
        else:
            supabase.table("pengumpulan_tugas").insert({
                "tugas_id":     tugas_id,
                "mahasiswa_id": mahasiswa_id,
                "file_url":     file_url,
                "file_name":    file_name,
                "status":       "selesai",
                "catatan":      catatan
            }).execute()

        return True, "Tugas berhasil dikumpulkan!"

    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"


def update_status_tugas(tugas_id: int, mahasiswa_id: int, status: str):
    """Update status pengerjaan tugas tanpa upload file."""
    if status not in ("belum_dikerjakan", "sedang_dikerjakan", "selesai"):
        return False, "Status tidak valid."
    try:
        cek = supabase.table("pengumpulan_tugas") \
                      .select("id") \
                      .eq("tugas_id", tugas_id) \
                      .eq("mahasiswa_id", mahasiswa_id) \
                      .execute()

        if cek.data:
            supabase.table("pengumpulan_tugas").update({
                "status": status
            }).eq("tugas_id", tugas_id).eq("mahasiswa_id", mahasiswa_id).execute()
        else:
            supabase.table("pengumpulan_tugas").insert({
                "tugas_id":     tugas_id,
                "mahasiswa_id": mahasiswa_id,
                "status":       status
            }).execute()

        return True, "Status berhasil diupdate!"

    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"


# ==========================================================================
# ─── UPLOAD PDF DOSEN (materi kuliah) ─────────────────────────────────────
# ==========================================================================

def upload_materi(file_path: str, dosen_id: int, judul: str, deskripsi: str = "", jadwal_id: int = None):
    """Dosen upload PDF materi kuliah."""
    try:
        file_name    = os.path.basename(file_path)
        storage_path = f"materi/{dosen_id}/{file_name}"

        with open(file_path, "rb") as f:
            supabase.storage.from_("tugas-files").upload(
                path=storage_path,
                file=f,
                file_options={"content-type": "application/pdf"}
            )

        file_url = supabase.storage.from_("tugas-files").get_public_url(storage_path)

        supabase.table("materi").insert({
            "judul":     judul,
            "deskripsi": deskripsi,
            "file_url":  file_url,
            "file_name": file_name,
            "dosen_id":  dosen_id,
            "jadwal_id": jadwal_id
        }).execute()

        return True, "Materi berhasil diupload!"

    except Exception as e:
        return False, f"Gagal upload materi: {e}"


def get_materi(dosen_id: int = None):
    """Ambil semua materi, bisa filter by dosen."""
    try:
        query = supabase.table("materi").select("*, users(nama)")
        if dosen_id:
            query = query.eq("dosen_id", dosen_id)
        res = query.order("created_at", desc=True).execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil materi: {e}"


def hapus_materi(materi_id: int, dosen_id: int):
    """Hapus materi beserta filenya (hanya dosen pemilik)."""
    try:
        res = supabase.table("materi").select("*") \
                      .eq("id", materi_id) \
                      .eq("dosen_id", dosen_id) \
                      .execute()

        if not res.data:
            return False, "Materi tidak ditemukan atau bukan milik Anda."

        materi       = res.data[0]
        storage_path = f"materi/{dosen_id}/{materi['file_name']}"

        supabase.storage.from_("tugas-files").remove([storage_path])
        supabase.table("materi").delete().eq("id", materi_id).execute()

        return True, "Materi berhasil dihapus!"

    except Exception as e:
        return False, f"Gagal hapus materi: {e}"