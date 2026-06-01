import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QStackedWidget
)

from PySide6.QtCore import Qt
from ui.components.sidebar import Sidebar
from ui.dosen.mata_kuliah import (
    MataKuliah,
    DetailMataKuliah
)

class DashboardDosen(QMainWindow):

    def __init__(self, user_data=None):
        super().__init__()

        self.user_data = user_data or {}
        self.load_stylesheet()
        self.setWindowTitle("AkademiQ - Dashboard Dosen")
        self.resize(920, 620)          
        self.setMinimumSize(920, 620)

        self.build_ui()

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # SIDEBAR
        self.sidebar = Sidebar()
        self.stack = QStackedWidget()

        self.dashboard_page = QWidget()
        self.matkul_page = MataKuliah()
        self.sidebar.btn_dashboard.clicked.connect(
            self.show_dashboard
        )
        self.sidebar.btn_matkul.clicked.connect(
            self.show_matkul
        )
        # self.sidebar.btn_jadwal.clicked.connect(
        #     self.show_jadwal
        # )
        self.sidebar.btn_logout.clicked.connect(
            self.logout
        )

        # CONTENT
        content =  self.dashboard_page
        content.setObjectName("rightPanel")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        # HEADER
        header = QFrame()
        header.setObjectName("dashboardHeader")

        header_layout = QHBoxLayout(header)

        left_header = QVBoxLayout()

        title = QLabel("Dashboard Dosen")
        title.setObjectName("labelTitle")

        subtitle = QLabel("Kelola aktivitas akademik dengan lebih mudah.")
        subtitle.setObjectName("labelSub")

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        header_layout.addLayout(left_header)
        header_layout.addStretch()

        # PROFILE CARD
        profile_card = QFrame()
        profile_card.setObjectName("profileCard")
        profile_card.setFixedSize(220, 70)

        profile_layout = QHBoxLayout(profile_card)
        profile_layout.setContentsMargins(12, 10, 12, 10)

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

        # KPI CARDS
        stats = self.get_dashboard_stats()
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        cards_layout.addWidget(
            self.create_kpi_card(
                "📚",
                "Mata Kuliah",
                stats["courses"]
            )
        )

        cards_layout.addWidget(
            self.create_kpi_card(
                "📝",
                "Total Tugas",
                stats["assignments"]
            )
        )

        cards_layout.addWidget(
            self.create_kpi_card(
                "👨‍🎓",
                "Mahasiswa",
                stats["students"]
            )
        )

        cards_layout.addWidget(
            self.create_kpi_card(
                "📅",
                "Jadwal Hari Ini",
                stats["schedules"]
            )
        )

        content_layout.addLayout(cards_layout)

        # AKTIVITAS AKADEMIK
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

        self.stack.addWidget(
            self.dashboard_page
        )

        self.stack.addWidget(
            self.matkul_page
        )
        self.stack.setCurrentWidget(
            self.dashboard_page
        )

        # =====================================
        # ROOT
        # =====================================

        root_layout.addWidget(
            self.sidebar
        )

        root_layout.addWidget(
            self.stack
        )
    
    def load_stylesheet(self):

        qss_path = os.path.join(
            os.path.dirname(__file__),
            "style.qss"
        )

        try:

            with open(
                qss_path,
                "r",
                encoding="utf-8"
            ) as file:

                self.setStyleSheet(
                    file.read()
                )

        except Exception as e:

            print(
                "Gagal load QSS:",
                e
            )

    def create_kpi_card(
        self,
        icon,
        title,
        value
    ):

        card = QFrame()
        card.setObjectName("dashboardCard")
        card.setFixedHeight(75)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)

        icon_label = QLabel(icon)
        icon_label.setObjectName("kpiIcon")

        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)

        value_label = QLabel(str(value))
        value_label.setObjectName("kpiValue")

        title_label = QLabel(title)
        title_label.setObjectName("kpiTitle")

        info_layout.addWidget(value_label)
        info_layout.addWidget(title_label)

        layout.addWidget(icon_label)
        layout.addLayout(info_layout)

        return card
    
    def get_dashboard_stats(self):

        try:

            courses = get_courses()
            assignments = get_assignments()
            schedules = get_schedules()

            total_mahasiswa = 0

            for course in courses:

                enrollments = get_course_enrollments(
                    course["id"]
                )

                total_mahasiswa += len(
                    enrollments
                )

            return {
                "courses": len(courses),
                "assignments": len(assignments),
                "students": total_mahasiswa,
                "schedules": len(schedules)
            }

        except Exception as e:

            print(e)

            return {
                "courses": 0,
                "assignments": 0,
                "students": 0,
                "schedules": 0
            }
    def show_matkul(self):

        self.stack.setCurrentWidget(
            self.matkul_page
        )

    def buka_detail_matkul(
        self,
        course
    ):

        self.detail_page = DetailMataKuliah(
            course
        )

        self.stack.addWidget(
            self.detail_page
        )

        self.stack.setCurrentWidget(
            self.detail_page
        )

        self.detail_page.btn_kembali.clicked.connect(
            lambda:
            self.stack.setCurrentWidget(
                self.matkul_page
            )
        )
        
    def show_dashboard(self):

        self.stack.setCurrentWidget(
            self.dashboard_page
        )

    def logout(self):

        from ui.auth.auth_window import AuthWindow

        self.login_window = AuthWindow()
        self.login_window.show()

        self.close()