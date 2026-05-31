import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QFrame, QStackedWidget, 
    QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

# ==========================================================================
# ─── DATABASE INTEGRATION & FALLBACK MOCK ─────────────────────────────────
# ==========================================================================
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    from database.db_manager import login_user, register_user
except ImportError:
    USERS_DB = [
        {"nama": "Budi Santoso", "nim": "12345", "email": "budi@email.com", "password": "password123", "role": "mahasiswa"},
        {"nama": "Dr. Adi", "nim": "67890", "email": "adi@email.com", "password": "password123", "role": "dosen"}
    ]
    
    def login_user(email, password):
        for u in USERS_DB:
            if u["email"] == email and u["password"] == password:
                return True, u
        return False, "Email atau password salah!"

    def register_user(nama, nim, email, password, role):
        if not all([nama, nim, email, password]):
            return False, "Semua data harus diisi!"
        if len(password) < 6:
            return False, "Password minimal 6 karakter!"
        if any(u["email"] == email for u in USERS_DB):
            return False, "Email sudah terdaftar!"
        USERS_DB.append({"nama": nama, "nim": nim, "email": email, "password": password, "role": role})
        return True, "Registrasi berhasil!"


# ==========================================================================
# ─── VISUAL EFFECTS HOOK ──────────────────────────────────────────────────
# ==========================================================================
def apply_shadow(widget, radius=12, offset_y=3, color_hex="#64748B", alpha=25):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(radius)
    shadow.setOffset(0, offset_y)
    shadow.setColor(QColor(color_hex + f"{alpha:02x}"))
    widget.setGraphicsEffect(shadow)


# ==========================================================================
# ─── CUSTOM REUSABLE FIELD GROUP ──────────────────────────────────────────
# ==========================================================================
class FieldGroup(QWidget):
    def __init__(self, label: str, placeholder: str, is_password=False, parent=None):
        super().__init__(parent)
        self.is_password = is_password
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel(label.upper())
        lbl.setObjectName("labelField")
        layout.addWidget(lbl)

        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        input_container.setFixedHeight(46)
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(4, 0, 8, 0)
        input_layout.setSpacing(0)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setStyleSheet("QLineEdit { border: none; background: transparent; }")
        input_layout.addWidget(self.input)

        if self.is_password:
            self.input.setEchoMode(QLineEdit.Password)
            self.btn_toggle = QPushButton("👁️")
            self.btn_toggle.setFixedSize(36, 36)
            self.btn_toggle.setCursor(Qt.PointingHandCursor)
            self.btn_toggle.setStyleSheet("""
                QPushButton { background: transparent; border: none; font-size: 14px; }
                QPushButton:hover { color: #38BDF8; }
            """)
            self.btn_toggle.clicked.connect(self._toggle_visibility)
            input_layout.addWidget(self.btn_toggle)

        layout.addWidget(input_container)

    def _toggle_visibility(self):
        if self.input.echoMode() == QLineEdit.Password:
            self.input.setEchoMode(QLineEdit.Normal)
            self.btn_toggle.setText("🔒")
        else:
            self.input.setEchoMode(QLineEdit.Password)
            self.btn_toggle.setText("👁️")

    def value(self) -> str: 
        return self.input.text().strip()
        
    def clear(self): 
        self.input.clear()


# ==========================================================================
# ─── LOGIN PANEL LAYOUT ───────────────────────────────────────────────────
# ==========================================================================
class LoginPage(QWidget):
    def __init__(self, on_login_success, on_goto_register, parent=None):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.on_goto_register = on_goto_register
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(54, 0, 54, 0)
        main.setSpacing(14)
        main.addStretch()

        badge = QLabel("AKADEMIQ")
        badge.setObjectName("badge")
        main.addWidget(badge)

        title = QLabel("Selamat Datang Kembali 👋")
        title.setObjectName("labelTitle")
        main.addWidget(title)

        sub = QLabel("Masuk untuk mengelola aktivitas akademikmu.")
        sub.setObjectName("labelSub")
        main.addWidget(sub)
        main.addSpacing(10)

        self.f_email = FieldGroup("Email", "nama@email.com")
        self.f_password = FieldGroup("Password", "••••••••", is_password=True)
        main.addWidget(self.f_email)
        main.addWidget(self.f_password)

        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("labelError")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.hide()
        main.addWidget(self.lbl_status)

        self.btn_login = QPushButton("Masuk Aplikasi")
        self.btn_login.setObjectName("btnPrimary")
        self.btn_login.setFixedHeight(48)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self._handle_login)
        apply_shadow(self.btn_login, radius=10, offset_y=3, color_hex="#C084FC", alpha=35)
        main.addWidget(self.btn_login)

        row = QHBoxLayout()
        row.addStretch()
        lbl_q = QLabel("Belum punya akun?")
        lbl_q.setObjectName("labelSub")
        btn_reg = QPushButton("Daftar Sekarang")
        btn_reg.setObjectName("btnLink")
        btn_reg.setCursor(Qt.PointingHandCursor)
        btn_reg.clicked.connect(self.on_goto_register)
        row.addWidget(lbl_q)
        row.addWidget(btn_reg)
        row.addStretch()
        main.addLayout(row)

        main.addStretch()

    def _handle_login(self):
        self.lbl_status.hide()
        ok, result = login_user(self.f_email.value(), self.f_password.value())
        if ok:
            role_label = "Dosen" if result["role"] == "dosen" else "Mahasiswa"
            QMessageBox.information(
                self, "Login Berhasil",
                f"✅ Selamat datang kembali, {result['nama']}!\nAnda masuk sebagai {role_label}."
            )
            self.f_email.clear()
            self.f_password.clear()
            # Panggil callback yang sudah diset
            if self.on_login_success:
                self.on_login_success(result)
        else:
            self.lbl_status.setText(f"⚠ {result}")
            self.lbl_status.show()


# ==========================================================================
# ─── REGISTER PANEL LAYOUT ────────────────────────────────────────────────
# ==========================================================================
class RegisterPage(QWidget):
    def __init__(self, on_register_success, on_goto_login, parent=None):
        super().__init__(parent)
        self.on_register_success = on_register_success
        self.on_goto_login = on_goto_login
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(54, 0, 54, 0)
        main.setSpacing(12)
        main.addStretch()

        badge = QLabel("AKADEMIQ")
        badge.setObjectName("badge")
        main.addWidget(badge)

        title = QLabel("Buat Akun Baru ✨")
        title.setObjectName("labelTitle")
        main.addWidget(title)

        self.f_nama = FieldGroup("Nama Lengkap", "Masukkan nama lengkap")
        self.f_nim = FieldGroup("NIM / NIP", "Nomor Induk Akademik")
        self.f_email = FieldGroup("Email", "nama@email.com")
        self.f_password = FieldGroup("Password", "Minimal 6 karakter", is_password=True)
        
        for field in [self.f_nama, self.f_nim, self.f_email, self.f_password]:
            main.addWidget(field)

        role_layout = QVBoxLayout()
        role_layout.setSpacing(6)
        role_lbl = QLabel("ROLE")
        role_lbl.setObjectName("labelField")
        self.combo_role = QComboBox()
        self.combo_role.addItem("🎓 Mahasiswa", "mahasiswa")
        self.combo_role.addItem("📋 Dosen", "dosen")
        self.combo_role.setFixedHeight(46)
        role_layout.addWidget(role_lbl)
        role_layout.addWidget(self.combo_role)
        main.addLayout(role_layout)

        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.hide()
        main.addWidget(self.lbl_status)

        self.btn_register = QPushButton("Daftar Akun")
        self.btn_register.setObjectName("btnPrimary")
        self.btn_register.setFixedHeight(48)
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.clicked.connect(self._handle_register)
        apply_shadow(self.btn_register, radius=10, offset_y=3, color_hex="#C084FC", alpha=35)
        main.addWidget(self.btn_register)

        row = QHBoxLayout()
        row.addStretch()
        lbl_q = QLabel("Sudah punya akun?")
        lbl_q.setObjectName("labelSub")
        btn_login = QPushButton("Masuk")
        btn_login.setObjectName("btnLink")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.clicked.connect(self.on_goto_login)
        row.addWidget(lbl_q)
        row.addWidget(btn_login)
        row.addStretch()
        main.addLayout(row)

        main.addStretch()

    def _handle_register(self):
        self.lbl_status.hide()
        ok, msg = register_user(
            self.f_nama.value(), self.f_nim.value(), 
            self.f_email.value(), self.f_password.value(), 
            self.combo_role.currentData()
        )
        if ok:
            self.lbl_status.setObjectName("labelSuccess")
            self.lbl_status.setStyle(self.style())
            self.lbl_status.setText(f"✅ {msg} Mengalihkan...")
            self.lbl_status.show()
            QTimer.singleShot(1400, self._reset_and_go_login)
        else:
            self.lbl_status.setObjectName("labelError")
            self.lbl_status.setStyle(self.style())
            self.lbl_status.setText(f"⚠ {msg}")
            self.lbl_status.show()

    def _reset_and_go_login(self):
        for field in [self.f_nama, self.f_nim, self.f_email, self.f_password]:
            field.clear()
        self.lbl_status.hide()
        self.on_goto_login()


# ==========================================================================
# ─── MAIN WINDOW CONTROLLER ───────────────────────────────────────────────
# ==========================================================================
class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AkademiQ — Autentikasi")
        self.resize(920, 620)          
        self.setMinimumSize(920, 620)
        self.on_login_success = None  # Initialize callback
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- PANEL KIRI: INFO APP BRANDING ---
        left = QWidget()
        left.setObjectName("leftPanel")
        left.setFixedWidth(360)
        
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(40, 48, 40, 48)
        left_layout.setSpacing(0)

        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_frame.setFixedSize(54, 54)
        
        logo_lbl = QLabel("AQ", logo_frame)
        logo_lbl.setObjectName("logoLabel")
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setGeometry(0, 0, 54, 54)
        
        apply_shadow(logo_frame, radius=15, offset_y=4, color_hex="#38BDF8", alpha=40)
        left_layout.addWidget(logo_frame)
        left_layout.addSpacing(28)

        app_name = QLabel("AkademiQ")
        app_name.setObjectName("appName")
        left_layout.addWidget(app_name)
        left_layout.addSpacing(8)

        tagline = QLabel("Platform manajemen akademik terpadu untuk mahasiswa & dosen.")
        tagline.setObjectName("tagline")
        tagline.setWordWrap(True)
        left_layout.addWidget(tagline)
        left_layout.addSpacing(36)

        features = [
            ("📅", "Kelola jadwal kuliah"),
            ("📝", "Pantau tugas & deadline"),
            ("📊", "Lacak progres belajar"),
            ("👥", "Multi-role terintegrasi"),
        ]
        for icon, text in features:
            row = QHBoxLayout()
            row.setSpacing(12)
            ic = QLabel(icon)
            ic.setObjectName("featureIcon")
            ic.setFixedWidth(24)
            tx = QLabel(text)
            tx.setObjectName("featureText")
            row.addWidget(ic)
            row.addWidget(tx)
            row.addStretch()
            left_layout.addLayout(row)
            left_layout.addSpacing(16)

        left_layout.addStretch()

        ver = QLabel("Kelompok 4 · v1.0.0")
        ver.setObjectName("versionLabel")
        left_layout.addWidget(ver)
        root_layout.addWidget(left)

        # --- PANEL KANAN: FORM INTERAKTIF ---
        right = QWidget()
        right.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("transparentStack")

        self.login_page = LoginPage(
            on_login_success=self._on_login_success,
            on_goto_register=lambda: self.stack.setCurrentIndex(1)
        )
        self.register_page = RegisterPage(
            on_register_success=lambda: self.stack.setCurrentIndex(0),
            on_goto_login=lambda: self.stack.setCurrentIndex(0)
        )

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        right_layout.addWidget(self.stack)
        root_layout.addWidget(right)

    def _on_login_success(self, user: dict):
        """Callback dari LoginPage - memanggil callback eksternal"""
        print(f"[AUTH] Login sukses untuk {user.get('nama')}")
        if self.on_login_success:
            self.on_login_success(user)
        else:
            print("[AUTH] Tidak ada callback yang diset!")