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
# ─── COURSES ──────────────────────────────────────────────────────────────
# ==========================================================================

def get_courses():
    """Ambil semua mata kuliah."""
    try:
        res = supabase.table("courses").select("*").order("nama").execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil courses: {e}"

def add_course(kode: str, nama: str, sks: int, dosen: str, deskripsi: str, enroll_code: str):
    """Dosen tambah mata kuliah baru."""
    try:
        supabase.table("courses").insert({
            "kode":        kode.strip().upper(),
            "nama":        nama.strip(),
            "sks":         sks,
            "dosen":       dosen.strip(),
            "deskripsi":   deskripsi.strip(),
            "enroll_code": enroll_code.strip().upper()
        }).execute()
        return True, "Mata kuliah berhasil ditambahkan!"
    except Exception as e:
        return False, f"Gagal tambah course: {e}"

def update_course(course_id: int, data: dict):
    """Update data mata kuliah."""
    try:
        supabase.table("courses").update(data).eq("id", course_id).execute()
        return True, "Mata kuliah berhasil diupdate!"
    except Exception as e:
        return False, f"Gagal update course: {e}"

def hapus_course(course_id: int):
    """Hapus mata kuliah."""
    try:
        supabase.table("courses").delete().eq("id", course_id).execute()
        return True, "Mata kuliah berhasil dihapus!"
    except Exception as e:
        return False, f"Gagal hapus course: {e}"


# ==========================================================================
# ─── ENROLLMENTS ──────────────────────────────────────────────────────────
# ==========================================================================

def enroll_course(user_id: int, enroll_code: str):
    """Mahasiswa daftar mata kuliah pakai kode enroll."""
    try:
        cek = supabase.table("courses").select("*").eq("enroll_code", enroll_code.strip().upper()).execute()
        if not cek.data:
            return False, "Kode enroll tidak ditemukan."

        course    = cek.data[0]
        course_id = course["id"]

        cek_enroll = supabase.table("enrollments").select("id") \
                             .eq("user_id", user_id) \
                             .eq("course_id", course_id).execute()
        if cek_enroll.data:
            return False, "Sudah terdaftar di mata kuliah ini."

        supabase.table("enrollments").insert({
            "user_id":   user_id,
            "course_id": course_id,
            "status":    "active"
        }).execute()

        return True, f"Berhasil mendaftar ke {course['nama']}!"

    except Exception as e:
        return False, f"Gagal enroll: {e}"

def get_enrolled_courses(user_id: int):
    """Ambil semua mata kuliah yang diikuti mahasiswa."""
    try:
        res = supabase.table("enrollments").select("*, courses(*)") \
                      .eq("user_id", user_id) \
                      .eq("status", "active").execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil enrolled courses: {e}"

def get_mahasiswa_list(course_id: int = None):
    """Dosen lihat daftar mahasiswa, bisa filter by course."""
    try:
        if course_id:
            res = supabase.table("enrollments").select("*, users(*)") \
                          .eq("course_id", course_id).execute()
        else:
            res = supabase.table("users").select("*").eq("role", "mahasiswa").execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil mahasiswa: {e}"


# ==========================================================================
# ─── SCHEDULES ────────────────────────────────────────────────────────────
# ==========================================================================

def get_schedules():
    """Ambil semua jadwal kuliah."""
    try:
        res = supabase.table("schedules").select("*").order("day_of_week").execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil jadwal: {e}"

def add_schedule(day_of_week: str, course_name: str, lecturer: str,
                 start_time: str, end_time: str, room: str, color: str = "#3498db"):
    """Dosen tambah jadwal kuliah."""
    try:
        supabase.table("schedules").insert({
            "day_of_week": day_of_week,
            "course_name": course_name,
            "lecturer":    lecturer,
            "start_time":  start_time,
            "end_time":    end_time,
            "room":        room,
            "color":       color
        }).execute()
        return True, "Jadwal berhasil ditambahkan!"
    except Exception as e:
        return False, f"Gagal tambah jadwal: {e}"

def update_schedule(schedule_id: int, data: dict):
    """Update jadwal kuliah."""
    try:
        supabase.table("schedules").update(data).eq("id", schedule_id).execute()
        return True, "Jadwal berhasil diupdate!"
    except Exception as e:
        return False, f"Gagal update jadwal: {e}"

def hapus_schedule(schedule_id: int):
    """Hapus jadwal kuliah."""
    try:
        supabase.table("schedules").delete().eq("id", schedule_id).execute()
        return True, "Jadwal berhasil dihapus!"
    except Exception as e:
        return False, f"Gagal hapus jadwal: {e}"


# ==========================================================================
# ─── ASSIGNMENTS ──────────────────────────────────────────────────────────
# ==========================================================================

def get_assignments(course_id: int = None):
    """Ambil semua tugas, bisa filter by course."""
    try:
        query = supabase.table("assignments").select("*, courses(nama)")
        if course_id:
            query = query.eq("course_id", course_id)
        res = query.order("deadline_date").execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil tugas: {e}"

def add_assignment(course_id: int, judul: str, deskripsi: str,
                   deadline_date: str, deadline_time: str = "23:59:00"):
    """Dosen tambah tugas baru."""
    try:
        supabase.table("assignments").insert({
            "course_id":     course_id,
            "judul":         judul.strip(),
            "deskripsi":     deskripsi.strip(),
            "deadline_date": deadline_date,
            "deadline_time": deadline_time
        }).execute()
        return True, "Tugas berhasil ditambahkan!"
    except Exception as e:
        return False, f"Gagal tambah tugas: {e}"

def update_assignment(assignment_id: int, data: dict):
    """Update tugas."""
    try:
        supabase.table("assignments").update(data).eq("id", assignment_id).execute()
        return True, "Tugas berhasil diupdate!"
    except Exception as e:
        return False, f"Gagal update tugas: {e}"

def hapus_assignment(assignment_id: int):
    """Hapus tugas."""
    try:
        supabase.table("assignments").delete().eq("id", assignment_id).execute()
        return True, "Tugas berhasil dihapus!"
    except Exception as e:
        return False, f"Gagal hapus tugas: {e}"


# ==========================================================================
# ─── SUBMISSIONS (mahasiswa upload PDF) ───────────────────────────────────
# ==========================================================================

def submit_tugas(assignment_id: int, user_id: int, file_path: str, catatan: str = ""):
    """Mahasiswa upload PDF untuk mengumpulkan tugas."""
    try:
        file_name    = os.path.basename(file_path)
        storage_path = f"{user_id}/{assignment_id}/{file_name}"

        with open(file_path, "rb") as f:
            supabase.storage.from_("tugas-files").upload(
                path=storage_path,
                file=f,
                file_options={"content-type": "application/pdf"}
            )

        file_url = supabase.storage.from_("tugas-files").get_public_url(storage_path)

        cek = supabase.table("submissions").select("id") \
                      .eq("assignment_id", assignment_id) \
                      .eq("user_id", user_id).execute()

        if cek.data:
            supabase.table("submissions").update({
                "file_path": storage_path,
                "file_url":  file_url,
                "file_name": file_name,
                "catatan":   catatan,
                "status":    "submitted"
            }).eq("assignment_id", assignment_id).eq("user_id", user_id).execute()
        else:
            supabase.table("submissions").insert({
                "assignment_id": assignment_id,
                "user_id":       user_id,
                "file_path":     storage_path,
                "file_url":      file_url,
                "file_name":     file_name,
                "catatan":       catatan,
                "status":        "submitted"
            }).execute()

        return True, "Tugas berhasil dikumpulkan!"

    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"

def get_submissions(assignment_id: int = None, user_id: int = None):
    """Ambil submissions, bisa filter by assignment atau user."""
    try:
        query = supabase.table("submissions").select("*, users(nama, nim_nip), assignments(judul)")
        if assignment_id:
            query = query.eq("assignment_id", assignment_id)
        if user_id:
            query = query.eq("user_id", user_id)
        res = query.order("submitted_at", desc=True).execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil submissions: {e}"

def beri_nilai(submission_id: int, nilai: str):
    """Dosen beri nilai pada submission mahasiswa."""
    try:
        supabase.table("submissions").update({
            "nilai": nilai
        }).eq("id", submission_id).execute()
        return True, "Nilai berhasil disimpan!"
    except Exception as e:
        return False, f"Gagal beri nilai: {e}"


# ==========================================================================
# ─── MATERIALS (dosen upload PDF) ─────────────────────────────────────────
# ==========================================================================

def upload_materi(file_path: str, course_id: int, judul: str, deskripsi: str = ""):
    """Dosen upload PDF materi kuliah."""
    try:
        file_name    = os.path.basename(file_path)
        storage_path = f"materi/{course_id}/{file_name}"

        with open(file_path, "rb") as f:
            supabase.storage.from_("tugas-files").upload(
                path=storage_path,
                file=f,
                file_options={"content-type": "application/pdf"}
            )

        file_url = supabase.storage.from_("tugas-files").get_public_url(storage_path)

        supabase.table("materials").insert({
            "course_id": course_id,
            "judul":     judul.strip(),
            "deskripsi": deskripsi.strip(),
            "filename":  file_name,
            "file_path": storage_path,
            "file_url":  file_url
        }).execute()

        return True, "Materi berhasil diupload!"

    except Exception as e:
        return False, f"Gagal upload materi: {e}"

def get_materi(course_id: int = None):
    """Ambil semua materi, bisa filter by course."""
    try:
        query = supabase.table("materials").select("*, courses(nama)")
        if course_id:
            query = query.eq("course_id", course_id)
        res = query.order("created_at", desc=True).execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil materi: {e}"

def hapus_materi(materi_id: int):
    """Hapus materi beserta filenya."""
    try:
        res = supabase.table("materials").select("*").eq("id", materi_id).execute()
        if not res.data:
            return False, "Materi tidak ditemukan."

        storage_path = res.data[0]["file_path"]
        supabase.storage.from_("tugas-files").remove([storage_path])
        supabase.table("materials").delete().eq("id", materi_id).execute()

        return True, "Materi berhasil dihapus!"

    except Exception as e:
        return False, f"Gagal hapus materi: {e}"


# ==========================================================================
# ─── PERSONAL TASKS ───────────────────────────────────────────────────────
# ==========================================================================

def get_personal_tasks(user_id: int):
    """Ambil semua tugas pribadi milik user."""
    try:
        res = supabase.table("personal_tasks").select("*") \
                      .eq("user_id", user_id) \
                      .order("deadline_date").execute()
        return True, res.data
    except Exception as e:
        return False, f"Gagal ambil personal tasks: {e}"

def add_personal_task(user_id: int, judul: str, course_name: str,
                      deskripsi: str, deadline_date: str, priority: str = "Medium"):
    """Tambah tugas pribadi."""
    if priority not in ("Low", "Medium", "High"):
        return False, "Priority tidak valid."
    try:
        supabase.table("personal_tasks").insert({
            "user_id":       user_id,
            "judul":         judul.strip(),
            "course_name":   course_name.strip(),
            "deskripsi":     deskripsi.strip(),
            "deadline_date": deadline_date,
            "priority":      priority,
            "status":        "Pending"
        }).execute()
        return True, "Tugas berhasil ditambahkan!"
    except Exception as e:
        return False, f"Gagal tambah tugas: {e}"

def update_personal_task(task_id: int, user_id: int, data: dict):
    """Update tugas pribadi (hanya milik sendiri)."""
    allowed_status = ("Pending", "Not Started", "Doing", "Done")
    if "status" in data and data["status"] not in allowed_status:
        return False, "Status tidak valid."
    try:
        supabase.table("personal_tasks").update(data) \
                .eq("id", task_id).eq("user_id", user_id).execute()
        return True, "Tugas berhasil diupdate!"
    except Exception as e:
        return False, f"Gagal update tugas: {e}"

def hapus_personal_task(task_id: int, user_id: int):
    """Hapus tugas pribadi (hanya milik sendiri)."""
    try:
        supabase.table("personal_tasks").delete() \
                .eq("id", task_id).eq("user_id", user_id).execute()
        return True, "Tugas berhasil dihapus!"
    except Exception as e:
        return False, f"Gagal hapus tugas: {e}"