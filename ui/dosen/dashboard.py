from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame
)

from PySide6.QtCore import Qt

from ui.components.sidebar import Sidebar


class DashboardDosen(QMainWindow):

    def __init__(self, user_data=None):
        super().__init__()

        self.user_data = user_data or {}

        self.setWindowTitle("AkademiQ - Dashboard Dosen")
        self.resize(1200, 750)
        self.setMinimumSize(1000, 700)

        self.build_ui()

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # =====================================
        # SIDEBAR
        # =====================================

        self.sidebar = Sidebar()
        self.sidebar.btn_logout.clicked.connect(
            self.logout
        )

        # =====================================
        # CONTENT
        # =====================================

        content = QWidget()
        content.setObjectName("rightPanel")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(
            25,
            25,
            25,
            25
        )
        content_layout.setSpacing(20)

        # =====================================
        # HEADER
        # =====================================

        header = QFrame()
        header.setObjectName("dashboardHeader")

        header_layout = QHBoxLayout(header)

        left_header = QVBoxLayout()

        title = QLabel("Dashboard Dosen")
        title.setObjectName("labelTitle")

        subtitle = QLabel(
            "Kelola aktivitas akademik dengan lebih mudah."
        )
        subtitle.setObjectName("labelSub")

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        header_layout.addLayout(left_header)
        header_layout.addStretch()

        # =====================================
        # PROFILE CARD
        # =====================================

        profile_card = QFrame()
        profile_card.setObjectName("profileCard")
        profile_card.setFixedSize(220, 70)

        profile_layout = QHBoxLayout(profile_card)
        profile_layout.setContentsMargins(
            12,
            10,
            12,
            10
        )

        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)

        nama = QLabel(
            self.user_data.get(
                "nama",
                "Dosen"
            )
        )
        nama.setObjectName("profileName")

        role = QLabel(
            self.user_data.get(
                "role",
                "Dosen"
            ).capitalize()
        )
        role.setObjectName("profileRole")

        info_layout.addWidget(nama)
        info_layout.addWidget(role)

        avatar = QLabel("👤")
        avatar.setObjectName("profileAvatar")
        avatar.setAlignment(Qt.AlignCenter)

        profile_layout.addLayout(info_layout)
        profile_layout.addStretch()
        profile_layout.addWidget(avatar)

        header_layout.addWidget(profile_card)

        content_layout.addWidget(header)

        # =====================================
        # KPI CARDS
        # =====================================

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        cards_layout.addWidget(
            self.create_kpi_card(
                "📚",
                "Mata Kuliah",
                5
            )
        )

        cards_layout.addWidget(
            self.create_kpi_card(
                "📝",
                "Total Tugas",
                18
            )
        )

        cards_layout.addWidget(
            self.create_kpi_card(
                "👨‍🎓",
                "Mahasiswa",
                120
            )
        )

        cards_layout.addWidget(
            self.create_kpi_card(
                "📅",
                "Jadwal Hari Ini",
                3
            )
        )

        content_layout.addLayout(cards_layout)

        # =====================================
        # AKTIVITAS AKADEMIK
        # =====================================

        aktivitas_card = QFrame()
        aktivitas_card.setObjectName("dashboardCard")

        aktivitas_layout = QVBoxLayout(
            aktivitas_card
        )

        aktivitas_title = QLabel(
            "Aktivitas Akademik"
        )
        aktivitas_title.setObjectName(
            "labelTitle"
        )

        aktivitas_sub = QLabel(
            "Ringkasan aktivitas dosen hari ini."
        )
        aktivitas_sub.setObjectName(
            "labelSub"
        )

        aktivitas_layout.addWidget(
            aktivitas_title
        )
        aktivitas_layout.addWidget(
            aktivitas_sub
        )

        aktivitas_layout.addSpacing(20)

        aktivitas_layout.addWidget(
            QLabel(
                "• Tugas Pemrograman Visual - Deadline 2 Hari Lagi"
            )
        )

        aktivitas_layout.addWidget(
            QLabel(
                "• Kelas Basis Data - Senin 08:00"
            )
        )

        aktivitas_layout.addWidget(
            QLabel(
                "• 35 Mahasiswa Mengumpulkan Tugas"
            )
        )

        aktivitas_layout.addStretch()

        content_layout.addWidget(
            aktivitas_card
        )

        # =====================================
        # ROOT
        # =====================================

        root_layout.addWidget(
            self.sidebar
        )

        root_layout.addWidget(
            content
        )

    def create_kpi_card(
        self,
        icon,
        title,
        value
    ):

        card = QFrame()
        card.setObjectName(
            "dashboardCard"
        )

        card.setMinimumHeight(130)

        layout = QVBoxLayout(card)

        icon_label = QLabel(icon)
        icon_label.setObjectName(
            "kpiIcon"
        )

        title_label = QLabel(title)
        title_label.setObjectName(
            "kpiTitle"
        )

        value_label = QLabel(
            str(value)
        )
        value_label.setObjectName(
            "kpiValue"
        )

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(value_label)

        return card

    def logout(self):

        from ui.auth.auth_window import AuthWindow

        self.login_window = AuthWindow()
        self.login_window.show()

        self.close()