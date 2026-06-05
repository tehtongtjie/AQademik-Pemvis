import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget, QScrollArea
)
from PySide6.QtCore import Qt
from ui.components.sidebar import Sidebar
from ui.dosen.pages.mata_kuliah import MataKuliah
from database.db_manager import (
    get_courses, get_assignments, get_schedules, get_mahasiswa_list
)
from ui.dosen.pages.detail_mata_kuliah import DetailMataKuliah
from ui.dosen.pages.jadwal_page import JadwalPage
from ui.dosen.pages.profil_page import ProfilPage


class DashboardDosen(QMainWindow):

    def __init__(self, user=None):
        super().__init__()
        self.user = user or {}
        self.load_stylesheet()
        self.setWindowTitle("AkademiQ - Dashboard Dosen")
        self.resize(1220, 680)
        self.setMinimumSize(1040, 620)
        self.build_ui()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ──
        self.sidebar = Sidebar()
        self.stack = QStackedWidget()

        # ── Pages ──
        self.dashboard_page = self._build_dashboard_page()
        self.matkul_page    = MataKuliah(self.user)
        self.jadwal_page    = JadwalPage(self.user)
        self.profil_page    = ProfilPage(self.user)
        self.profil_page.profil_diupdate.connect(self._on_profil_diupdate)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.matkul_page)
        self.stack.addWidget(self.jadwal_page)
        self.stack.addWidget(self.profil_page)
        self.stack.setCurrentWidget(self.dashboard_page)

        # ── Sidebar signals ──
        self.sidebar.btn_dashboard.clicked.connect(self.show_dashboard)
        self.sidebar.btn_matkul.clicked.connect(self.show_matkul)
        self.sidebar.btn_jadwal.clicked.connect(self.show_jadwal)
        self.sidebar.btn_profil.clicked.connect(self.show_profil)
        self.sidebar.btn_logout.clicked.connect(self.logout)

        # ── Active tab highlight ──
        self._nav_btns = [
            self.sidebar.btn_dashboard,
            self.sidebar.btn_matkul,
            self.sidebar.btn_jadwal,
            self.sidebar.btn_profil,
        ]
        self._set_active_nav(self.sidebar.btn_dashboard)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.stack)

    # ──────────────────────────────────────────────────────────
    # DASHBOARD PAGE BUILDER
    # ──────────────────────────────────────────────────────────

    def _build_dashboard_page(self):
        page = QWidget()
        page.setObjectName("rightPanel")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(page)

        wrapper = QWidget()
        wrapper.setObjectName("rightPanel")
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(scroll)

        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(28, 28, 28, 28)
        outer_layout.setSpacing(20)

        # ── Header ──
        header = self._build_header(
            "Dashboard Dosen",
            "Kelola aktivitas akademik dengan lebih mudah."
        )
        outer_layout.addWidget(header)

        # ── KPI Cards ──
        stats = self.get_dashboard_stats()
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(14)

        kpi_data = [
            ("📚", "Mata Kuliah",    stats["courses"],     "#0284C7"),
            ("📝", "Total Tugas",    stats["assignments"],  "#6366F1"),
            ("👨‍🎓", "Mahasiswa",      stats["students"],    "#059669"),
            ("📅", "Jadwal",         stats["schedules"],    "#D97706"),
        ]
        for icon, label, val, color in kpi_data:
            kpi_layout.addWidget(self._create_kpi_card(icon, label, val, color))

        outer_layout.addLayout(kpi_layout)

        # ── Activity ──
        activity_card = self._build_activity_card()
        outer_layout.addWidget(activity_card)
        outer_layout.addStretch()

        return wrapper

    def _build_header(self, title_text, sub_text):
        header = QFrame()
        header.setObjectName("dashboardHeader")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)

        left = QVBoxLayout()
        left.setSpacing(4)

        title = QLabel(title_text)
        title.setObjectName("labelTitle")

        sub = QLabel(sub_text)
        sub.setObjectName("labelSub")

        left.addWidget(title)
        left.addWidget(sub)

        layout.addLayout(left)
        layout.addStretch()
        layout.addWidget(self._build_profile_card())
        return header

    def _build_profile_card(self):
        """Profile card — klik navigasi ke halaman Profil."""
        from PySide6.QtGui import QCursor

        card = QFrame()
        card.setObjectName("profileCard")
        card.setFixedSize(220, 64)
        card.setCursor(QCursor(Qt.PointingHandCursor))
        card.setToolTip("Klik untuk lihat & edit profil")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)

        info = QVBoxLayout()
        info.setSpacing(2)

        self._lbl_profile_nama = QLabel(self.user.get("nama", "Dosen"))
        self._lbl_profile_nama.setObjectName("profileName")

        role = QLabel(self.user.get("role", "Dosen").capitalize())
        role.setObjectName("profileRole")

        info.addWidget(self._lbl_profile_nama)
        info.addWidget(role)

        edit_hint = QLabel("✏")
        edit_hint.setStyleSheet("color:#6366F1; font-size:12px; padding-right:4px;")

        avatar = QLabel("👤")
        avatar.setObjectName("profileAvatar")
        avatar.setAlignment(Qt.AlignCenter)

        layout.addLayout(info)
        layout.addStretch()
        layout.addWidget(edit_hint)
        layout.addWidget(avatar)

        card.mousePressEvent = lambda _: self.show_profil()
        return card

    def _on_profil_diupdate(self, user_baru: dict):
        """Callback setelah profil berhasil diupdate."""
        self.user.update(user_baru)
        if hasattr(self, "_lbl_profile_nama"):
            self._lbl_profile_nama.setText(self.user.get("nama", "Dosen"))

    def _build_activity_card(self):
        card = QFrame()
        card.setObjectName("dashboardCard")

        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        title = QLabel("Aktivitas Akademik")
        title.setObjectName("labelTitle")

        sub = QLabel("Ringkasan aktivitas terbaru hari ini.")
        sub.setObjectName("labelSub")

        layout.addWidget(title)
        layout.addWidget(sub)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #E2E8F0; max-height: 1px; margin: 4px 0;")
        layout.addWidget(divider)

        activities = self.get_recent_activities()

        if not activities:
            empty = QLabel("Belum ada aktivitas.")
            empty.setObjectName("labelSub")
            layout.addWidget(empty)
        else:
            for activity in activities:
                item = QLabel(f"  {activity}")
                item.setObjectName("activityItem")
                layout.addWidget(item)

        layout.addStretch()
        return card

    # ──────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────

    def _create_kpi_card(self, icon, title, value, accent_color):
        card = QFrame()
        card.setObjectName("kpiCard")
        card.setFixedHeight(90)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setObjectName("kpiIcon")
        icon_label.setFixedWidth(36)
        icon_label.setAlignment(Qt.AlignCenter)

        info = QVBoxLayout()
        info.setSpacing(2)

        value_label = QLabel(str(value))
        value_label.setObjectName("kpiValue")
        value_label.setStyleSheet(f"color: {accent_color}; font-size: 26px; font-weight: 700;")

        title_label = QLabel(title)
        title_label.setObjectName("kpiTitle")

        info.addWidget(value_label)
        info.addWidget(title_label)

        card_layout.addWidget(icon_label)
        card_layout.addLayout(info)
        return card

    def load_stylesheet(self):
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Gagal load QSS:", e)

    def get_dashboard_stats(self):
        try:
            success, courses = get_courses(self.user["id"])
            courses = courses if success else []
            course_ids = [c["id"] for c in courses]

            success, assignments = get_assignments()
            assignments = assignments if success else []
            total_tugas = sum(1 for t in assignments if t["course_id"] in course_ids)

            total_mahasiswa = 0
            for course in courses:
                ok, mhs = get_mahasiswa_list(course["id"])
                if ok:
                    total_mahasiswa += len(mhs)

            success, schedules = get_schedules()
            schedules = schedules if success else []
            jadwal_dosen = [j for j in schedules if j["course_id"] in course_ids]

            return {
                "courses": len(courses),
                "assignments": total_tugas,
                "students": total_mahasiswa,
                "schedules": len(jadwal_dosen),
            }
        except Exception as e:
            print(e)
            return {"courses": 0, "assignments": 0, "students": 0, "schedules": 0}

    def get_recent_activities(self):
        activities = []
        try:
            ok, courses = get_courses(self.user["id"])
            if not ok:
                return activities
            course_ids = [c["id"] for c in courses]

            ok, assignments = get_assignments()
            if ok:
                for t in assignments:
                    if t["course_id"] in course_ids:
                        activities.append(f"📝 {t['judul']}")

            ok, schedules = get_schedules()
            if ok:
                for j in schedules:
                    if j["course_id"] in course_ids:
                        activities.append(
                            f"📅 {j['course_name']} — {j['day_of_week']} {j['start_time']}"
                        )
            return activities[:5]
        except Exception:
            return []

    # ──────────────────────────────────────────────────────────
    # NAVIGATION
    # ──────────────────────────────────────────────────────────

    def _set_active_nav(self, active_btn):
        for btn in self._nav_btns:
            btn.setChecked(False)
        active_btn.setChecked(True)

    def show_dashboard(self):
        self._set_active_nav(self.sidebar.btn_dashboard)
        self.stack.setCurrentWidget(self.dashboard_page)

    def show_matkul(self):
        self._set_active_nav(self.sidebar.btn_matkul)
        self.stack.setCurrentWidget(self.matkul_page)

    def show_jadwal(self):
        self._set_active_nav(self.sidebar.btn_jadwal)
        self.stack.setCurrentWidget(self.jadwal_page)

    def show_profil(self):
        self._set_active_nav(self.sidebar.btn_profil)
        self.stack.setCurrentWidget(self.profil_page)

    def buka_detail_matkul(self, course):
        self.detail_page = DetailMataKuliah(course)
        self.stack.addWidget(self.detail_page)
        self.stack.setCurrentWidget(self.detail_page)
        self.detail_page.btn_kembali.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.matkul_page)
        )

    def logout(self):
        from ui.auth.auth_window import AuthWindow
        self.login_window = AuthWindow()
        self.login_window.show()
        self.close()
