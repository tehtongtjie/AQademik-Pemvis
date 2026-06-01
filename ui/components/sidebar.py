from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFrame
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

        # LOGO
        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_frame.setFixedSize(54, 54)

        logo_label = QLabel("AQ", logo_frame)
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setGeometry(0, 0, 54, 54)

        layout.addWidget(logo_frame)

        layout.addSpacing(20)

        # APP NAME
        app_name = QLabel("AkademiQ")
        app_name.setObjectName("appName")

        layout.addWidget(app_name)

        layout.addSpacing(8)

        # TAGLINE

        tagline = QLabel(
            "Platform manajemen akademik terpadu untuk mahasiswa dan dosen."
        )

        tagline.setObjectName("tagline")
        tagline.setWordWrap(True)

        layout.addWidget(tagline)

        layout.addSpacing(30)

        # MENU TITLE
        menu_title = QLabel("MENU")

        menu_title.setObjectName("menuHeader")

        layout.addWidget(menu_title)

        layout.addSpacing(10)

        # MENU BUTTONS
        self.btn_dashboard = QPushButton("🏠 Dashboard")
        self.btn_matkul = QPushButton("📝 Kelola Mata Kuliah")
        self.btn_jadwal = QPushButton("📅 Kelola Jadwal")
        self.btn_logout = QPushButton("🚪 Logout")

        for btn in [
            self.btn_dashboard,
            self.btn_matkul,
            self.btn_jadwal,
        ]:
            btn.setObjectName("btnSecondary")
            layout.addWidget(btn)

        layout.addStretch()

        self.btn_logout.setObjectName("btnSecondary")
        layout.addWidget(self.btn_logout)

        # VERSION

        version = QLabel("Kelompok 4 · v1.0.0")

        version.setObjectName("versionLabel")

        layout.addWidget(version)
        root_layout.addWidget(container)