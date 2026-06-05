from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QTabWidget,
    QFormLayout, QSizePolicy, QScrollArea, QTextEdit
)
from PySide6.QtCore import Qt, Signal

from database.db_manager import update_user_profile, change_password


class ProfilPage(QWidget):
    """
    Halaman profil dosen — inline di QStackedWidget.
    Field disesuaikan dengan kolom tabel users:
      nama, nim_nip (read-only), email, phone, address, role (read-only)
    """

    profil_diupdate = Signal(dict)

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self._build_ui()

    # ──────────────────────────────────────────────────────────
    # BUILD UI
    # ──────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(20)

        # ── Page header ──
        header = QFrame()
        header.setObjectName("dashboardHeader")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)

        left = QVBoxLayout()
        left.setSpacing(4)

        title = QLabel("Profil Dosen")
        title.setObjectName("labelTitle")

        sub = QLabel("Lihat dan perbarui informasi akun Anda.")
        sub.setObjectName("labelSub")

        left.addWidget(title)
        left.addWidget(sub)
        header_layout.addLayout(left)
        header_layout.addStretch()
        header_layout.addWidget(self._build_avatar_card())

        root.addWidget(header)

        # ── Info card read-only (NIP, Email, Role) ──
        info_card = QFrame()
        info_card.setObjectName("dashboardCard")
        info_layout = QHBoxLayout(info_card)
        info_layout.setContentsMargins(20, 14, 20, 14)
        info_layout.setSpacing(0)

        for icon, label, key in [
            ("🪪", "NIP / NIM",  "nim_nip"),
            ("📧", "Email",      "email"),
            ("👥", "Role",       "role"),
        ]:
            col = QVBoxLayout()
            col.setSpacing(3)
            col.addWidget(_sec_lbl(label))
            val = QLabel(str(self.user.get(key) or "-"))
            val.setObjectName("cardTitle")
            col.addWidget(val)
            info_layout.addLayout(col)
            info_layout.addStretch()

        root.addWidget(info_card)

        # ── Scrollable content ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(16)

        # ── Tab widget ──
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 0 12px 12px 12px;
                background: #FFFFFF;
            }
            QTabBar::tab {
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-bottom: none;
                border-radius: 10px 10px 0 0;
                color: #64748B;
                font-size: 13px;
                font-weight: 500;
                min-width: 160px;
                padding: 10px 20px;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                color: #6366F1;
                font-weight: 700;
                border-top: 2.5px solid #6366F1;
            }
            QTabBar::tab:hover:!selected {
                background: #F1F5F9;
                color: #334155;
            }
        """)

        self.tabs.addTab(self._build_tab_info(),     "👤  Informasi Profil")
        self.tabs.addTab(self._build_tab_password(), "🔒  Ganti Password")

        inner_layout.addWidget(self.tabs)
        inner_layout.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll)

    def _build_avatar_card(self):
        card = QFrame()
        card.setObjectName("profileCard")
        card.setFixedSize(220, 64)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)

        info = QVBoxLayout()
        info.setSpacing(2)

        self._lbl_nama_card = QLabel(self.user.get("nama", "Dosen"))
        self._lbl_nama_card.setObjectName("profileName")

        role_lbl = QLabel(self.user.get("role", "dosen").capitalize())
        role_lbl.setObjectName("profileRole")

        info.addWidget(self._lbl_nama_card)
        info.addWidget(role_lbl)

        avatar = QLabel("👤")
        avatar.setObjectName("profileAvatar")
        avatar.setAlignment(Qt.AlignCenter)

        layout.addLayout(info)
        layout.addStretch()
        layout.addWidget(avatar)
        return card

    # ── TAB 1 : Informasi Profil ────────────────────────────

    def _build_tab_info(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        form_card = QFrame()
        form_card.setObjectName("dashboardCard")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 20, 24, 20)
        form_layout.setSpacing(16)

        sec = QLabel("Edit Informasi")
        sec.setObjectName("cardTitle")
        form_layout.addWidget(sec)

        hint = QLabel("NIP/NIM dan Role tidak dapat diubah di sini.")
        hint.setObjectName("labelSub")
        form_layout.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Field sesuai kolom DB: nama, email, phone, address
        self.fld_nama    = _field(self.user.get("nama", ""),            "Nama lengkap")
        self.fld_email   = _field(self.user.get("email", ""),           "Alamat email")
        self.fld_phone   = _field(self.user.get("phone", "") or "",     "Contoh: 08123456789")
        self.fld_address = _field(self.user.get("address", "") or "",   "Alamat domisili")

        # NIP/NIM — read-only
        fld_nip = QLineEdit(self.user.get("nim_nip", "") or "")
        fld_nip.setReadOnly(True)
        fld_nip.setMinimumHeight(38)
        fld_nip.setStyleSheet(
            "QLineEdit { color:#94A3B8; background:#F1F5F9;"
            " border:1.5px solid #E2E8F0; border-radius:10px; padding:6px 12px; }"
        )

        # Role — read-only
        fld_role = QLineEdit((self.user.get("role", "") or "").capitalize())
        fld_role.setReadOnly(True)
        fld_role.setMinimumHeight(38)
        fld_role.setStyleSheet(
            "QLineEdit { color:#94A3B8; background:#F1F5F9;"
            " border:1.5px solid #E2E8F0; border-radius:10px; padding:6px 12px; }"
        )

        form.addRow(_lbl("NIP / NIM"),  fld_nip)
        form.addRow(_lbl("Role"),       fld_role)
        form.addRow(_lbl("Nama"),       self.fld_nama)
        form.addRow(_lbl("Email"),      self.fld_email)
        form.addRow(_lbl("Telepon"),    self.fld_phone)
        form.addRow(_lbl("Alamat"),     self.fld_address)

        form_layout.addLayout(form)

        # Status
        self.lbl_status_profil = QLabel("")
        self.lbl_status_profil.setWordWrap(True)
        self.lbl_status_profil.hide()
        form_layout.addWidget(self.lbl_status_profil)

        # Tombol
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_reset = QPushButton("Reset")
        btn_reset.setObjectName("btnSecondary")
        btn_reset.setMinimumHeight(38)
        btn_reset.setMinimumWidth(90)
        btn_reset.clicked.connect(self._reset_form)

        btn_simpan = QPushButton("💾  Simpan Perubahan")
        btn_simpan.setObjectName("btnPrimary")
        btn_simpan.setMinimumHeight(38)
        btn_simpan.setMinimumWidth(180)
        btn_simpan.clicked.connect(self._simpan_profil)

        btn_row.addWidget(btn_reset)
        btn_row.addSpacing(8)
        btn_row.addWidget(btn_simpan)
        form_layout.addLayout(btn_row)

        layout.addWidget(form_card)
        layout.addStretch()
        return tab

    # ── TAB 2 : Ganti Password ──────────────────────────────

    def _build_tab_password(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        pwd_card = QFrame()
        pwd_card.setObjectName("dashboardCard")
        pwd_layout = QVBoxLayout(pwd_card)
        pwd_layout.setContentsMargins(24, 20, 24, 20)
        pwd_layout.setSpacing(16)

        sec = QLabel("Ubah Password Akun")
        sec.setObjectName("cardTitle")
        pwd_layout.addWidget(sec)

        hint = QLabel("Password baru minimal 6 karakter.")
        hint.setObjectName("labelSub")
        pwd_layout.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.fld_old_pwd  = _pwd_field("Password saat ini")
        self.fld_new_pwd  = _pwd_field("Password baru (min. 6 karakter)")
        self.fld_conf_pwd = _pwd_field("Konfirmasi password baru")

        form.addRow(_lbl("Password Lama"), self.fld_old_pwd)
        form.addRow(_lbl("Password Baru"), self.fld_new_pwd)
        form.addRow(_lbl("Konfirmasi"),    self.fld_conf_pwd)

        pwd_layout.addLayout(form)

        self.lbl_status_pwd = QLabel("")
        self.lbl_status_pwd.setWordWrap(True)
        self.lbl_status_pwd.hide()
        pwd_layout.addWidget(self.lbl_status_pwd)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_bersih = QPushButton("Bersihkan")
        btn_bersih.setObjectName("btnSecondary")
        btn_bersih.setMinimumHeight(38)
        btn_bersih.setMinimumWidth(100)
        btn_bersih.clicked.connect(self._clear_pwd_form)

        btn_ganti = QPushButton("🔒  Ganti Password")
        btn_ganti.setObjectName("btnPrimary")
        btn_ganti.setMinimumHeight(38)
        btn_ganti.setMinimumWidth(160)
        btn_ganti.clicked.connect(self._ganti_password)

        btn_row.addWidget(btn_bersih)
        btn_row.addSpacing(8)
        btn_row.addWidget(btn_ganti)
        pwd_layout.addLayout(btn_row)

        layout.addWidget(pwd_card)
        layout.addStretch()
        return tab

    # ──────────────────────────────────────────────────────────
    # LOGIC
    # ──────────────────────────────────────────────────────────

    def refresh_user(self, user: dict):
        self.user = user
        self.fld_nama.setText(user.get("nama", ""))
        self.fld_email.setText(user.get("email", ""))
        self.fld_phone.setText(user.get("phone", "") or "")
        self.fld_address.setText(user.get("address", "") or "")
        self._lbl_nama_card.setText(user.get("nama", "Dosen"))

    def _reset_form(self):
        self.fld_nama.setText(self.user.get("nama", ""))
        self.fld_email.setText(self.user.get("email", ""))
        self.fld_phone.setText(self.user.get("phone", "") or "")
        self.fld_address.setText(self.user.get("address", "") or "")
        self.lbl_status_profil.hide()

    def _clear_pwd_form(self):
        for f in (self.fld_old_pwd, self.fld_new_pwd, self.fld_conf_pwd):
            f.clear()
        self.lbl_status_pwd.hide()

    def _simpan_profil(self):
        nama    = self.fld_nama.text().strip()
        email   = self.fld_email.text().strip()
        phone   = self.fld_phone.text().strip()
        address = self.fld_address.text().strip()

        if not nama or not email:
            _show_status(self.lbl_status_profil, "Nama dan email tidak boleh kosong.", error=True)
            return

        success, pesan = update_user_profile(self.user["id"], nama, email, phone, address)

        if success:
            self.user.update({"nama": nama, "email": email, "phone": phone, "address": address})
            self._lbl_nama_card.setText(nama)
            _show_status(self.lbl_status_profil, "✅  Profil berhasil diupdate!", error=False)
            self.profil_diupdate.emit(self.user)
        else:
            _show_status(self.lbl_status_profil, f"❌  {pesan}", error=True)

    def _ganti_password(self):
        old_pwd  = self.fld_old_pwd.text()
        new_pwd  = self.fld_new_pwd.text()
        conf_pwd = self.fld_conf_pwd.text()

        if not old_pwd or not new_pwd or not conf_pwd:
            _show_status(self.lbl_status_pwd, "Semua field harus diisi.", error=True)
            return
        if new_pwd != conf_pwd:
            _show_status(self.lbl_status_pwd, "Password baru dan konfirmasi tidak cocok.", error=True)
            return
        if len(new_pwd) < 6:
            _show_status(self.lbl_status_pwd, "Password baru minimal 6 karakter.", error=True)
            return

        success, pesan = change_password(self.user["id"], old_pwd, new_pwd)

        if success:
            _show_status(self.lbl_status_pwd, "✅  Password berhasil diganti!", error=False)
            self._clear_pwd_form()
        else:
            _show_status(self.lbl_status_pwd, f"❌  {pesan}", error=True)


# ── Helper functions ─────────────────────────────────────────

def _lbl(text: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName("labelField")
    return l

def _sec_lbl(text: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName("sectionLabel")
    return l

def _field(text: str = "", placeholder: str = "") -> QLineEdit:
    f = QLineEdit()
    f.setText(text)
    f.setPlaceholderText(placeholder)
    f.setMinimumHeight(38)
    return f

def _pwd_field(placeholder: str) -> QLineEdit:
    f = QLineEdit()
    f.setPlaceholderText(placeholder)
    f.setEchoMode(QLineEdit.Password)
    f.setMinimumHeight(38)
    return f

def _show_status(label: QLabel, msg: str, error: bool):
    label.setText(msg)
    label.setObjectName("labelError" if error else "labelSuccess")
    label.style().unpolish(label)
    label.style().polish(label)
    label.show()
