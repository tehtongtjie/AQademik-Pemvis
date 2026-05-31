import sqlite3
import hashlib
import os
from PySide6.QtCore import QObject, Signal

DB_PATH = os.path.join(os.path.dirname(__file__), "akademiq.db")


class DatabaseSignals(QObject):
    data_changed = Signal()


db_signals = DatabaseSignals()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabel users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nim_nip TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('mahasiswa', 'dosen')),
            phone TEXT DEFAULT '',
            address TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabel mata kuliah
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode TEXT UNIQUE NOT NULL,
            nama TEXT NOT NULL,
            sks INTEGER DEFAULT 3,
            dosen TEXT NOT NULL,
            deskripsi TEXT,
            enroll_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabel enrollment (menyimpan mahasiswa yang terdaftar di mata kuliah)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            UNIQUE(user_id, course_id)
        )
    """)
    
    # Tabel schedules (jadwal kuliah)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week TEXT NOT NULL,
            course_name TEXT NOT NULL,
            lecturer TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room TEXT,
            color TEXT DEFAULT '#3498db',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabel materi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            judul TEXT NOT NULL,
            deskripsi TEXT,
            filename TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)
    
    # Tabel tugas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            judul TEXT NOT NULL,
            deskripsi TEXT,
            deadline_date TEXT NOT NULL,
            deadline_time TEXT DEFAULT '23:59',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)
    
    # Tabel pengumpulan tugas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            file_path TEXT,
            catatan TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nilai TEXT DEFAULT '-',
            status TEXT DEFAULT 'submitted',
            FOREIGN KEY (assignment_id) REFERENCES assignments(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Tabel personal tasks (tugas yang dibuat mahasiswa sendiri)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personal_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            judul TEXT NOT NULL,
            course_name TEXT NOT NULL,
            deskripsi TEXT,
            deadline_date TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Insert sample courses jika kosong
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        _insert_sample_courses(cursor)
    
    # Insert sample materials jika kosong
    cursor.execute("SELECT COUNT(*) FROM materials")
    if cursor.fetchone()[0] == 0:
        _insert_sample_materials(cursor)
    
    # Insert sample assignments jika kosong
    cursor.execute("SELECT COUNT(*) FROM assignments")
    if cursor.fetchone()[0] == 0:
        _insert_sample_assignments(cursor)
    
    # Insert sample schedules if empty
    cursor.execute("SELECT COUNT(*) FROM schedules")
    if cursor.fetchone()[0] == 0:
        _insert_sample_schedules(cursor)
    
    # Insert sample courses if empty
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        _insert_sample_courses(cursor)
    
    conn.commit()
    conn.close()

def _insert_sample_schedules(cursor):
    sample_schedules = [
        # Senin
        ('Senin', 'Pemrograman Visual', 'Pahrul Irfan, S.Kom., M.Kom.', '07:00', '09:30', 'D3-04', '#3498db'),
        ('Senin', 'Ekstraksi Fitur', 'Fitri Bimantoro', '14:30', '16:10', 'D2-02', '#e74c3c'),
        # Selasa
        ('Selasa', 'Pemrograman Bergerak', '-', '12:50', '14:30', 'D3-04', '#2ecc71'),
        # Rabu
        ('Rabu', 'Logika Fuzzy', 'Mohammad Zaenuddin Hamidi', '07:00', '08:40', 'A3-01', '#9b59b6'),
        ('Rabu', 'Pemodelan dan Simulasi', 'Herliana Rosika, S.Kom., M.Kom.', '09:30', '12:00', 'D3-04', '#f39c12'),
        # Jumat
        ('Jumat', 'Pemrosesan Bahasa Alami', 'Dr. Eng. Budi', '07:50', '09:30', 'A3-02', '#1abc9c'),
        ('Jumat', 'Pembelajaran Mesin', 'Ramaditia', '09:30', '11:10', 'D2-01', '#e67e22'),
        ('Jumat', 'Jaringan Komputer Lanjut', 'Andy', '13:40', '15:20', 'D2-01', '#27ae60'),
    ]
    
    cursor.executemany("""
        INSERT INTO schedules (day_of_week, course_name, lecturer, start_time, end_time, room, color)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_schedules)

def _insert_sample_courses(cursor):
    sample_courses = [
        ("PV001", "Pemrograman Visual", 3, "Pahrul Irfan, S.Kom., M.Kom.", 
         "Mata kuliah ini membahas pemrograman desktop menggunakan PySide6 dan Qt Framework.", "ENR-PV001"),
        ("BD002", "Basis Data", 3, "Dr. Siti Aminah, M.Kom.",
         "Mata kuliah ini membahas konsep database, SQL, dan implementasi.", "ENR-BD002"),
        ("JK003", "Jaringan Komputer", 3, "Dr. Ahmad Wijaya, M.T.",
         "Mata kuliah ini membahas konsep jaringan komputer dan implementasinya.", "ENR-JK003"),
        ("PW004", "Pemrograman Web", 3, "Dr. Dwi Lestari, S.Kom.",
         "Mata kuliah ini membahas pengembangan web modern menggunakan HTML, CSS, JavaScript.", "ENR-PW004"),
        ("KB005", "Kecerdasan Buatan", 3, "Prof. Ratna Dewi, Ph.D.",
         "Mata kuliah ini membahas konsep AI, machine learning, dan implementasinya.", "ENR-KB005"),
        ("SO006", "Sistem Operasi", 3, "Dr. Hendra Gunawan, M.Kom.",
         "Mata kuliah ini membahas konsep sistem operasi dan manajemen proses.", "ENR-SO006"),
        ("PM007", "Pemrograman Mobile", 3, "Dr. Maya Sari, M.T.",
         "Mata kuliah ini membahas pengembangan aplikasi mobile multiplatform.", "ENR-PM007"),
        ("ST008", "Statistika", 3, "Dr. Rina Marlina, M.Si.",
         "Mata kuliah ini membahas konsep statistika dan analisis data.", "ENR-ST008"),
    ]
    
    cursor.executemany("""
        INSERT INTO courses (kode, nama, sks, dosen, deskripsi, enroll_code)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_courses)


def _insert_sample_materials(cursor):
    # Get course ID
    cursor.execute("SELECT id, kode FROM courses")
    courses = {row['kode']: row['id'] for row in cursor.fetchall()}
    
    sample_materials = [
        (courses.get('PV001', 1), "Bab 1: Pengantar PySide6", "Materi pengantar tentang PySide6 dan Qt Framework", "bab1_pyside6.pdf", "/materials/pv001/bab1.pdf"),
        (courses.get('PV001', 1), "Bab 2: Widget Dasar", "Materi tentang widget-widget dasar di PySide6", "bab2_widget.pdf", "/materials/pv001/bab2.pdf"),
        (courses.get('PV001', 1), "Slide Presentasi", "Slide presentasi perkuliahan", "slides_pv001.pptx", "/materials/pv001/slides.pptx"),
        (courses.get('BD002', 2), "Bab 1: Pengantar Database", "Materi tentang konsep dasar database", "bab1_db.pdf", "/materials/bd002/bab1.pdf"),
        (courses.get('BD002', 2), "Bab 2: SQL Dasar", "Materi tentang query SQL dasar", "bab2_sql.pdf", "/materials/bd002/bab2.pdf"),
        (courses.get('JK003', 3), "Bab 1: Model OSI", "Materi tentang model OSI layer", "bab1_osi.pdf", "/materials/jk003/bab1.pdf"),
    ]
    
    cursor.executemany("""
        INSERT INTO materials (course_id, judul, deskripsi, filename, file_path)
        VALUES (?, ?, ?, ?, ?)
    """, sample_materials)


def _insert_sample_assignments(cursor):
    cursor.execute("SELECT id, kode FROM courses")
    courses = {row['kode']: row['id'] for row in cursor.fetchall()}
    
    sample_assignments = [
        (courses.get('PV001', 1), "Tugas 1: Aplikasi CRUD", "Buat aplikasi CRUD sederhana menggunakan PySide6", "2025-06-10", "23:59"),
        (courses.get('PV001', 1), "Tugas 2: Dashboard", "Buat dashboard dengan chart menggunakan QtCharts", "2025-06-20", "23:59"),
        (courses.get('BD002', 2), "Quiz 1: SQL", "Kerjakan soal quiz tentang SQL", "2025-06-15", "23:59"),
        (courses.get('BD002', 2), "UTS Basis Data", "Ujian Tengah Semester Basis Data", "2025-06-25", "23:59"),
        (courses.get('JK003', 3), "Tugas 1: Simulasi Jaringan", "Buat simulasi jaringan sederhana", "2025-06-18", "23:59"),
        (courses.get('PW004', 4), "Proyek Web", "Buat website portofolio", "2025-07-01", "23:59"),
    ]
    
    cursor.executemany("""
        INSERT INTO assignments (course_id, judul, deskripsi, deadline_date, deadline_time)
        VALUES (?, ?, ?, ?, ?)
    """, sample_assignments)


# user oriented
def register_user(nama: str, nim_nip: str, email: str, password: str, role: str, phone="", address=""):
    nama = nama.strip()
    nim_nip = nim_nip.strip()
    email = email.strip().lower()
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
            "INSERT INTO users (nama, nim_nip, email, password, role, phone, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nama, nim_nip, email, hash_password(password), role, phone, address),
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
    email = email.strip().lower()
    password = password.strip()

    if not email or not password:
        return False, "Email dan password harus diisi."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, hash_password(password)),
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return True, dict(user)
    return False, "Email atau password salah."

def update_user_profile(user_id, name, email, phone, address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET nama = ?, email = ?, phone = ?, address = ?
            WHERE id = ?
        """, (name, email, phone, address, user_id))
        conn.commit()
        return True, "Profil berhasil diupdate!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def change_password(user_id, old_password, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verifikasi pw lama
    cursor.execute(
        "SELECT * FROM users WHERE id = ? AND password = ?",
        (user_id, hash_password(old_password))
    )
    if not cursor.fetchone():
        conn.close()
        return False, "Password lama salah!"
    
    # Update pw
    try:
        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hash_password(new_password), user_id)
        )
        conn.commit()
        db_signals.data_changed.emit()
        return True, "Password berhasil diganti!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Course oriented
def get_all_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses ORDER BY nama")
    courses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return courses

def get_course_by_id(course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    conn.close()
    return dict(course) if course else None

def get_course_by_enroll_code(enroll_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE enroll_code = ?", (enroll_code,))
    course = cursor.fetchone()
    conn.close()
    return dict(course) if course else None

# Schedule
def get_all_schedules_sync():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, day_of_week, course_name, lecturer, start_time, end_time, room, color
        FROM schedules
        ORDER BY 
            CASE day_of_week
                WHEN 'Senin' THEN 1
                WHEN 'Selasa' THEN 2
                WHEN 'Rabu' THEN 3
                WHEN 'Kamis' THEN 4
                WHEN 'Jumat' THEN 5
                WHEN 'Sabtu' THEN 6
                WHEN 'Minggu' THEN 7
            END, start_time
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

def get_user_schedule(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Debug: cek enrolled courses dulu 
    cursor.execute("""
        SELECT c.id, c.nama, c.kode
        FROM courses c
        JOIN enrollments e ON e.course_id = c.id
        WHERE e.user_id = ? AND e.status = 'active'
    """, (user_id,))
    enrolled_courses = cursor.fetchall()
    print(f"[DEBUG] Enrolled courses for user {user_id}: {[dict(row) for row in enrolled_courses]}")
    
    # Ambil jadwal berdasarkan enrolled courses
    cursor.execute("""
        SELECT 
            s.day_of_week,
            s.course_name,
            s.lecturer,
            s.start_time,
            s.end_time,
            s.room
        FROM schedules s
        WHERE s.course_name IN (
            SELECT c.nama
            FROM courses c
            JOIN enrollments e ON e.course_id = c.id
            WHERE e.user_id = ? AND e.status = 'active'
        )
        ORDER BY 
            CASE s.day_of_week
                WHEN 'Senin' THEN 1
                WHEN 'Selasa' THEN 2
                WHEN 'Rabu' THEN 3
                WHEN 'Kamis' THEN 4
                WHEN 'Jumat' THEN 5
                WHEN 'Sabtu' THEN 6
                WHEN 'Minggu' THEN 7
            END, 
            s.start_time
    """, (user_id,))
    
    schedules = [dict(row) for row in cursor.fetchall()]
    print(f"[DEBUG] Found schedules: {schedules}")
    
    conn.close()
    return schedules

def get_user_enrolled_courses_with_schedule(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get enrolled courses
    cursor.execute("""
        SELECT c.* FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.user_id = ? AND e.status = 'active'
        ORDER BY c.nama
    """, (user_id,))
    courses = [dict(row) for row in cursor.fetchall()]
    
    # Get schedules buat courses nya
    for course in courses:
        cursor.execute("""
            SELECT s.* FROM schedules s
            WHERE s.course_name = ?
            ORDER BY 
                CASE s.day_of_week
                    WHEN 'Senin' THEN 1
                    WHEN 'Selasa' THEN 2
                    WHEN 'Rabu' THEN 3
                    WHEN 'Kamis' THEN 4
                    WHEN 'Jumat' THEN 5
                    WHEN 'Sabtu' THEN 6
                    WHEN 'Minggu' THEN 7
                END, s.start_time
        """, (course['nama'],))
        course['schedules'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return courses

def get_schedules_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT s.id, s.day_of_week, s.course_name, s.lecturer, 
               s.start_time, s.end_time, s.room, s.color
        FROM schedules s
        JOIN courses c ON c.nama = s.course_name
        JOIN enrollments e ON e.course_id = c.id
        WHERE e.user_id = ? AND e.status = 'active'
        ORDER BY 
            CASE s.day_of_week
                WHEN 'Senin' THEN 1
                WHEN 'Selasa' THEN 2
                WHEN 'Rabu' THEN 3
                WHEN 'Kamis' THEN 4
                WHEN 'Jumat' THEN 5
                WHEN 'Sabtu' THEN 6
                WHEN 'Minggu' THEN 7
            END, s.start_time
    ''', (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def add_schedule(day, course_name, lecturer, start_time, end_time, room, color):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO schedules (day_of_week, course_name, lecturer, start_time, end_time, room, color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (day, course_name, lecturer, start_time, end_time, room, color))
        conn.commit()
        db_signals.data_changed.emit()
        return True, cursor.lastrowid
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def update_schedule(schedule_id, day, course_name, lecturer, start_time, end_time, room, color):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE schedules 
            SET day_of_week=?, course_name=?, lecturer=?, start_time=?, end_time=?, room=?, color=?
            WHERE id=?
        ''', (day, course_name, lecturer, start_time, end_time, room, color, schedule_id))
        conn.commit()
        db_signals.data_changed.emit()
        return True, "Schedule updated"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def delete_schedule(schedule_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM schedules WHERE id=?', (schedule_id,))
        conn.commit()
        db_signals.data_changed.emit()
        return True, "Schedule deleted"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
        
# Enrroll
def enroll_user(user_id, course_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Cek apakah sudah terdaftar
        cursor.execute(
            "SELECT id FROM enrollments WHERE user_id = ? AND course_id = ? AND status = 'active'",
            (user_id, course_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return False, "Anda sudah terdaftar di mata kuliah ini!"
        
        # Insert enrollment
        cursor.execute(
            "INSERT INTO enrollments (user_id, course_id, status) VALUES (?, ?, 'active')",
            (user_id, course_id)
        )
        conn.commit()
        
        # Verifikasi apakah berhasil tersimpan
        cursor.execute(
            "SELECT id FROM enrollments WHERE user_id = ? AND course_id = ? AND status = 'active'",
            (user_id, course_id)
        )
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return True, "Berhasil join mata kuliah!"
        else:
            conn.close()
            return False, "Gagal menyimpan data enrollment!"
            
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, f"Integrity Error: {str(e)}"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def is_user_enrolled(user_id, course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM enrollments WHERE user_id = ? AND course_id = ?",
        (user_id, course_id)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_user_enrolled_courses(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.* FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.user_id = ? AND e.status = 'active'
        ORDER BY c.nama
    """, (user_id,))
    courses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return courses

# Materi oriented
def get_course_materials(course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM materials WHERE course_id = ? ORDER BY created_at",
        (course_id,)
    )
    materials = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return materials


# Assignment oriented
def get_course_assignments(course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM assignments WHERE course_id = ? ORDER BY deadline_date",
        (course_id,)
    )
    assignments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return assignments


def submit_assignment(assignment_id, user_id, file_path, catatan=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO submissions (assignment_id, user_id, file_path, catatan)
            VALUES (?, ?, ?, ?)
        """, (assignment_id, user_id, file_path, catatan))
        conn.commit()
        return True, "Tugas berhasil dikumpulkan!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_submission(assignment_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM submissions 
        WHERE assignment_id = ? AND user_id = ?
        ORDER BY submitted_at DESC LIMIT 1
    """, (assignment_id, user_id))
    submission = cursor.fetchone()
    conn.close()
    return dict(submission) if submission else None

# Task oriented (personal tasks + course assignments) buat mhs
def get_all_tasks(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get personal tasks
    cursor.execute("""
        SELECT 
            id, 
            judul as tugas, 
            course_name as matkul, 
            deskripsi, 
            deadline_date as deadline, 
            priority, 
            status, 
            'personal' as source
        FROM personal_tasks 
        WHERE user_id = ?
        ORDER BY deadline_date
    """, (user_id,))
    personal_tasks = []
    for row in cursor.fetchall():
        personal_tasks.append(dict(row))
    
    # Get enrolled course IDs
    cursor.execute("""
        SELECT c.id, c.nama
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.user_id = ? AND e.status = 'active'
    """, (user_id,))
    enrolled_courses = cursor.fetchall()
    enrolled_course_ids = [row['id'] for row in enrolled_courses]
    
    # Get course assignments dari enrolled courses
    course_tasks = []
    if enrolled_course_ids:
        placeholders = ','.join(['?'] * len(enrolled_course_ids))
        cursor.execute(f"""
            SELECT 
                a.id, 
                a.judul as tugas, 
                c.nama as matkul, 
                a.deskripsi,
                a.deadline_date as deadline, 
                'Medium' as priority,
                CASE 
                    WHEN s.id IS NOT NULL AND s.status = 'submitted' THEN 'Doing'
                    WHEN s.id IS NOT NULL AND s.status = 'Done' THEN 'Done'
                    ELSE 'Not Started'
                END as status,
                'course' as source,
                a.course_id
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            LEFT JOIN submissions s ON s.assignment_id = a.id AND s.user_id = ?
            WHERE a.course_id IN ({placeholders})
            ORDER BY a.deadline_date
        """, (user_id, *enrolled_course_ids))
        for row in cursor.fetchall():
            course_tasks.append(dict(row))
    
    conn.close()
    
    # gabung
    all_tasks = personal_tasks + course_tasks
    # urutin dari deadline
    all_tasks.sort(key=lambda x: x.get('deadline', '9999-12-31'))
    
    return all_tasks

def add_personal_task(user_id, judul, matkul, deskripsi, deadline, priority, status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO personal_tasks (user_id, judul, course_name, deskripsi, deadline_date, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, judul, matkul, deskripsi, deadline, priority, status))
        conn.commit()
        db_signals.data_changed.emit()
        return True, cursor.lastrowid
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_personal_task(task_id, user_id, judul, matkul, deskripsi, deadline, priority, status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE personal_tasks 
            SET judul = ?, course_name = ?, deskripsi = ?, 
                deadline_date = ?, priority = ?, status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (judul, matkul, deskripsi, deadline, priority, status, task_id, user_id))
        conn.commit()
        db_signals.data_changed.emit()
        return True, "Task berhasil diupdate"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_personal_task(task_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM personal_tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        db_signals.data_changed.emit()
        return True, "Task berhasil dihapus"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_task_status(task_id, user_id, new_status, source='personal'):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if source == 'personal':
            cursor.execute("""
                UPDATE personal_tasks SET status = ? WHERE id = ? AND user_id = ?
            """, (new_status, task_id, user_id))
        else:
            # For course tasks, update submission status
            cursor.execute("""
                UPDATE submissions SET status = ? 
                WHERE assignment_id = ? AND user_id = ?
            """, (new_status, task_id, user_id))
        conn.commit()
        db_signals.data_changed.emit()
        return True, "Status berhasil diupdate"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_task_priority(task_id, user_id, new_priority, source='personal'):
    if source != 'personal':
        return False, "Tugas dari dosen tidak dapat mengubah prioritas"
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE personal_tasks SET priority = ? WHERE id = ? AND user_id = ?
        """, (new_priority, task_id, user_id))
        conn.commit()
        db_signals.data_changed.emit()
        return True, "Prioritas berhasil diupdate"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
        
# Inisialisasi DB saat modul diimpor
init_db()