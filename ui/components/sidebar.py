from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt


class Sidebar(QWidget):

    def __init__(self):
        super().__init__()
        self.setObjectName("leftPanel")
        self.setFixedWidth(360)
        self.build_ui()

    def build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        container = QWidget()
        container.setObjectName("leftPanel")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 48, 40, 48)
        layout.setSpacing(0)

        # ── LOGO ──
        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_frame.setFixedSize(54, 54)

        logo_label = QLabel("AQ", logo_frame)
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setGeometry(0, 0, 54, 54)

        layout.addWidget(logo_frame)
        layout.addSpacing(28)

        # ── APP NAME ──
        app_name = QLabel("AkademiQ")
        app_name.setObjectName("appName")
        layout.addWidget(app_name)

        layout.addSpacing(8)

        tagline = QLabel("Platform manajemen akademik terpadu untuk mahasiswa & dosen.")
        tagline.setObjectName("tagline")
        tagline.setWordWrap(True)
        layout.addWidget(tagline)

        layout.addSpacing(36)

        # ── MENU LABEL ──
        menu_title = QLabel("MENU")
        menu_title.setObjectName("sidebarSection")
        layout.addWidget(menu_title)
        layout.addSpacing(8)

        # ── NAV BUTTONS ──
        self.btn_dashboard = self._nav_btn("🏠  Dashboard")
        self.btn_matkul    = self._nav_btn("📚  Kelola Mata Kuliah")
        self.btn_jadwal    = self._nav_btn("📅  Kelola Jadwal")
        self.btn_profil    = self._nav_btn("👤  Profil Saya")

        for btn in [self.btn_dashboard, self.btn_matkul, self.btn_jadwal, self.btn_profil]:
            layout.addWidget(btn)
            layout.addSpacing(4)

        layout.addStretch()

        # ── LOGOUT ──
        self.btn_logout = QPushButton("🚪  Logout")
        self.btn_logout.setObjectName("btnLogout")
        self.btn_logout.setMinimumHeight(40)
        layout.addWidget(self.btn_logout)

        layout.addSpacing(12)

        # ── VERSION ──
        version = QLabel("Kelompok 4 · v1.0.0")
        version.setObjectName("versionLabel")
        layout.addWidget(version)

        root_layout.addWidget(container)

    def _nav_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("btnNav")
        btn.setMinimumHeight(40)
        btn.setCheckable(True)
        btn.setAutoExclusive(False)   # kita urus manual di dashboard
        return btn
