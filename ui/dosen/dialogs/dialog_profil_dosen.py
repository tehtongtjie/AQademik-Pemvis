from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QTabWidget,
    QWidget, QFormLayout, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from database.db_manager import update_user_profile, change_password


# ══════════════════════════════════════════════════════════════
#  DIALOG PROFIL DOSEN
#  Tab 1 : Informasi Profil (lihat + update)
#  Tab 2 : Ganti Password
# ══════════════════════════════════════════════════════════════

class DialogProfilDosen(QDialog):
    """Dialog untuk melihat dan mengupdate profil dosen."""

    profil_diupdate = Signal(dict)   # emit dict user terbaru ke parent

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Profil Dosen")
        self.setMinimumWidth(480)
        self.setMinimumHeight(420)
        self._build_ui()

    # ──────────────────────────────────────────────────────────
    # BUILD UI
    # ──────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setObjectName("dashboardHeader")
        header.setFixedHeight(72)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        avatar = QLabel("👤")
        avatar.setObjectName("profileAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedWidth(40)

        info = QVBoxLayout()
        info.setSpacing(2)

        nama_lbl = QLabel(self.user.get("nama", "Dosen"))
        nama_lbl.setObjectName("cardTitle")

        role_lbl = QLabel(self.user.get("role", "dosen").capitalize())
        role_lbl.setObjectName("profileRole")

        info.addWidget(nama_lbl)
        info.addWidget(role_lbl)

        header_layout.addWidget(avatar)
        header_layout.addLayout(info)
        header_layout.addStretch()

        nip_badge = QLabel(f"NIP: {self.user.get('nim_nip', '-')}")
        nip_badge.setObjectName("badgeInfo")
        header_layout.addWidget(nip_badge, 0, Qt.AlignVCenter)

        root.addWidget(header)

        # ── Tabs ──
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #FFFFFF;
            }
            QTabBar::tab {
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                color: #64748B;
                font-size: 13px;
                font-weight: 500;
                min-width: 140px;
                padding: 10px 18px;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                color: #6366F1;
                font-weight: 700;
                border-top: 2px solid #6366F1;
            }
            QTabBar::tab:hover:!selected {
                background: #F1F5F9;
                color: #334155;
            }
        """)

        self.tabs.addTab(self._build_tab_profil(),   "👤  Informasi Profil")
        self.tabs.addTab(self._build_tab_password(),  "🔒  Ganti Password")

        root.addWidget(self.tabs)

    # ── TAB 1: Profil ──────────────────────────────────────

    def _build_tab_profil(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        def _field(placeholder="", text=""):
            f = QLineEdit()
            f.setPlaceholderText(placeholder)
            f.setText(text)
            f.setMinimumHeight(38)
            return f

        self.fld_nama    = _field("Nama lengkap",   self.user.get("nama", ""))
        self.fld_email   = _field("Email",           self.user.get("email", ""))
        self.fld_phone   = _field("Nomor telepon",   self.user.get("phone", "") or "")
        self.fld_address = _field("Alamat",          self.user.get("address", "") or "")

        # NIP/NIM read-only
        fld_nip = QLineEdit(self.user.get("nim_nip", ""))
        fld_nip.setReadOnly(True)
        fld_nip.setMinimumHeight(38)
        fld_nip.setStyleSheet("QLineEdit { color:#94A3B8; background:#F8FAFC; }")

        form.addRow(_lbl("NIP / NIM"),   fld_nip)
        form.addRow(_lbl("Nama"),        self.fld_nama)
        form.addRow(_lbl("Email"),       self.fld_email)
        form.addRow(_lbl("Telepon"),     self.fld_phone)
        form.addRow(_lbl("Alamat"),      self.fld_address)

        layout.addLayout(form)
        layout.addStretch()

        # ── Status label ──
        self.lbl_status_profil = QLabel("")
        self.lbl_status_profil.setWordWrap(True)
        self.lbl_status_profil.hide()
        layout.addWidget(self.lbl_status_profil)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_batal = QPushButton("Batal")
        btn_batal.setObjectName("btnSecondary")
        btn_batal.setMinimumHeight(38)
        btn_batal.setMinimumWidth(90)
        btn_batal.clicked.connect(self.reject)

        btn_simpan = QPushButton("💾  Simpan Perubahan")
        btn_simpan.setObjectName("btnPrimary")
        btn_simpan.setMinimumHeight(38)
        btn_simpan.setMinimumWidth(180)
        btn_simpan.clicked.connect(self._simpan_profil)

        btn_row.addWidget(btn_batal)
        btn_row.addWidget(btn_simpan)
        layout.addLayout(btn_row)

        return tab

    # ── TAB 2: Password ─────────────────────────────────────

    def _build_tab_password(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        def _pwd(placeholder):
            f = QLineEdit()
            f.setPlaceholderText(placeholder)
            f.setEchoMode(QLineEdit.Password)
            f.setMinimumHeight(38)
            return f

        self.fld_old_pwd  = _pwd("Password lama")
        self.fld_new_pwd  = _pwd("Password baru (min. 6 karakter)")
        self.fld_conf_pwd = _pwd("Konfirmasi password baru")

        form.addRow(_lbl("Password Lama"),    self.fld_old_pwd)
        form.addRow(_lbl("Password Baru"),    self.fld_new_pwd)
        form.addRow(_lbl("Konfirmasi"),       self.fld_conf_pwd)

        layout.addLayout(form)
        layout.addStretch()

        # ── Status label ──
        self.lbl_status_pwd = QLabel("")
        self.lbl_status_pwd.setWordWrap(True)
        self.lbl_status_pwd.hide()
        layout.addWidget(self.lbl_status_pwd)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_batal = QPushButton("Batal")
        btn_batal.setObjectName("btnSecondary")
        btn_batal.setMinimumHeight(38)
        btn_batal.setMinimumWidth(90)
        btn_batal.clicked.connect(self.reject)

        btn_ganti = QPushButton("🔒  Ganti Password")
        btn_ganti.setObjectName("btnPrimary")
        btn_ganti.setMinimumHeight(38)
        btn_ganti.setMinimumWidth(160)
        btn_ganti.clicked.connect(self._ganti_password)

        btn_row.addWidget(btn_batal)
        btn_row.addWidget(btn_ganti)
        layout.addLayout(btn_row)

        return tab

    # ──────────────────────────────────────────────────────────
    # LOGIC
    # ──────────────────────────────────────────────────────────

    def _simpan_profil(self):
        nama    = self.fld_nama.text().strip()
        email   = self.fld_email.text().strip()
        phone   = self.fld_phone.text().strip()
        address = self.fld_address.text().strip()

        if not nama or not email:
            self._show_status(self.lbl_status_profil, "Nama dan email tidak boleh kosong.", error=True)
            return

        success, pesan = update_user_profile(
            self.user["id"], nama, email, phone, address
        )

        if success:
            self._show_status(self.lbl_status_profil, "✅  Profil berhasil diupdate!", error=False)
            # Update local user dict dan emit
            self.user.update({"nama": nama, "email": email, "phone": phone, "address": address})
            self.profil_diupdate.emit(self.user)
        else:
            self._show_status(self.lbl_status_profil, f"❌  {pesan}", error=True)

    def _ganti_password(self):
        old_pwd  = self.fld_old_pwd.text()
        new_pwd  = self.fld_new_pwd.text()
        conf_pwd = self.fld_conf_pwd.text()

        if not old_pwd or not new_pwd or not conf_pwd:
            self._show_status(self.lbl_status_pwd, "Semua field password harus diisi.", error=True)
            return

        if new_pwd != conf_pwd:
            self._show_status(self.lbl_status_pwd, "Password baru dan konfirmasi tidak cocok.", error=True)
            return

        if len(new_pwd) < 6:
            self._show_status(self.lbl_status_pwd, "Password baru minimal 6 karakter.", error=True)
            return

        success, pesan = change_password(self.user["id"], old_pwd, new_pwd)

        if success:
            self._show_status(self.lbl_status_pwd, "✅  Password berhasil diganti!", error=False)
            self.fld_old_pwd.clear()
            self.fld_new_pwd.clear()
            self.fld_conf_pwd.clear()
        else:
            self._show_status(self.lbl_status_pwd, f"❌  {pesan}", error=True)

    def _show_status(self, label: QLabel, msg: str, error: bool):
        label.setText(msg)
        if error:
            label.setObjectName("labelError")
        else:
            label.setObjectName("labelSuccess")
        label.style().unpolish(label)
        label.style().polish(label)
        label.show()


# ── helper ──
def _lbl(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("labelField")
    return lbl
