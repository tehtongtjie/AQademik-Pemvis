from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt

from ui.dosen.pages.materi_page import MateriPage
from ui.dosen.pages.tugas_page import TugasPage
from ui.dosen.pages.mahasiswa_page import MahasiswaPage


class DetailMataKuliah(QWidget):

    def __init__(self, course):
        super().__init__()
        self.course = course
        self._active_btn = None
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(16)

        # ── Top bar ──
        top = QHBoxLayout()

        self.btn_kembali = QPushButton("←  Kembali")
        self.btn_kembali.setObjectName("btnSecondary")
        self.btn_kembali.setFixedWidth(110)
        self.btn_kembali.setFixedHeight(36)

        top.addWidget(self.btn_kembali)
        top.addStretch()
        top.addWidget(self._build_profile_card())
        main_layout.addLayout(top)

        # ── Page header ──
        title = QLabel("Kelola Mata Kuliah")
        title.setObjectName("labelTitle")

        sub = QLabel("Kelola materi, tugas, dan mahasiswa pada mata kuliah.")
        sub.setObjectName("labelSub")

        main_layout.addWidget(title)
        main_layout.addWidget(sub)

        # ── Course info card ──
        info_card = QFrame()
        info_card.setObjectName("dashboardCard")
        info_layout = QHBoxLayout(info_card)
        info_layout.setContentsMargins(18, 14, 18, 14)

        left_info = QVBoxLayout()
        left_info.setSpacing(4)

        nama_matkul = QLabel(self.course["nama"])
        nama_matkul.setObjectName("cardTitle")

        detail_matkul = QLabel(f"🏷  {self.course['kode']}  •  {self.course['sks']} SKS")
        detail_matkul.setObjectName("labelSub")

        left_info.addWidget(nama_matkul)
        left_info.addWidget(detail_matkul)

        info_layout.addLayout(left_info)
        info_layout.addStretch()

        # SKS badge
        sks_badge = QLabel(f"{self.course['sks']} SKS")
        sks_badge.setObjectName("badgeInfo")
        info_layout.addWidget(sks_badge, 0, Qt.AlignVCenter)

        main_layout.addWidget(info_card)

        # ── Tab menu ──
        menu_card = QFrame()
        menu_card.setObjectName("dashboardCard")
        menu_card.setFixedHeight(56)

        menu_layout = QHBoxLayout(menu_card)
        menu_layout.setContentsMargins(12, 8, 12, 8)
        menu_layout.setSpacing(8)

        self.btn_materi = QPushButton("📚  Materi")
        self.btn_tugas = QPushButton("📝  Tugas")
        self.btn_mahasiswa = QPushButton("👨‍🎓  Mahasiswa")

        for btn in (self.btn_materi, self.btn_tugas, self.btn_mahasiswa):
            btn.setMinimumHeight(36)
            btn.setObjectName("btnSecondary")
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        main_layout.addWidget(menu_card)

        # ── Content area (stacked) ──
        self.content_stack = QStackedWidget()
        self.page_materi = MateriPage(self.course)
        self.page_tugas = TugasPage(self.course)
        self.page_mahasiswa = MahasiswaPage(self.course)

        self.content_stack.addWidget(self.page_materi)
        self.content_stack.addWidget(self.page_tugas)
        self.content_stack.addWidget(self.page_mahasiswa)

        main_layout.addWidget(self.content_stack)

        # ── Signals ──
        self.btn_materi.clicked.connect(self.show_materi)
        self.btn_tugas.clicked.connect(self.show_tugas)
        self.btn_mahasiswa.clicked.connect(self.show_mahasiswa)

        self.show_materi()

    def _build_profile_card(self):
        card = QFrame()
        card.setObjectName("profileCard")
        card.setFixedSize(210, 64)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)

        info = QVBoxLayout()
        info.setSpacing(2)

        nama_dosen = QLabel(
            self.course["users"]["nama"] if "users" in self.course else "Dosen"
        )
        nama_dosen.setObjectName("profileName")

        role = QLabel("Dosen")
        role.setObjectName("profileRole")

        info.addWidget(nama_dosen)
        info.addWidget(role)

        avatar = QLabel("👤")
        avatar.setObjectName("profileAvatar")
        avatar.setAlignment(Qt.AlignCenter)

        layout.addLayout(info)
        layout.addStretch()
        layout.addWidget(avatar)
        return card

    def _set_active_tab(self, active_btn):
        for btn in (self.btn_materi, self.btn_tugas, self.btn_mahasiswa):
            btn.setObjectName("btnSecondary")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        active_btn.setObjectName("btnPrimary")
        active_btn.style().unpolish(active_btn)
        active_btn.style().polish(active_btn)

    def show_materi(self):
        self._set_active_tab(self.btn_materi)
        self.content_stack.setCurrentWidget(self.page_materi)

    def show_tugas(self):
        self._set_active_tab(self.btn_tugas)
        self.content_stack.setCurrentWidget(self.page_tugas)

    def show_mahasiswa(self):
        self._set_active_tab(self.btn_mahasiswa)
        self.content_stack.setCurrentWidget(self.page_mahasiswa)
