from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea,
    QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from database.db_manager import add_course, get_courses
from ui.dosen.dialogs.dialogs_mata_kuliah import DialogMataKuliah
from ui.dosen.logic.validasi_mata_kuliah import validasi_mata_kuliah
from ui.dosen.pages.detail_mata_kuliah import DetailMataKuliah


class MataKuliah(QWidget):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.build_ui()
        self.load_data()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # ── Header ──
        header = QFrame()
        header.setObjectName("dashboardHeader")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 14)

        left = QVBoxLayout()
        left.setSpacing(3)

        title = QLabel("Kelola Mata Kuliah")
        title.setObjectName("labelTitle")

        sub = QLabel("Pilih mata kuliah untuk mengelola materi dan tugas.")
        sub.setObjectName("labelSub")

        left.addWidget(title)
        left.addWidget(sub)

        header_layout.addLayout(left)
        header_layout.addStretch()
        header_layout.addWidget(self._build_profile_card())
        main_layout.addWidget(header)

        # ── Toolbar ──
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Cari mata kuliah...")
        self.search.textChanged.connect(self.load_data)
        self.search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_tambah = QPushButton("＋  Tambah Mata Kuliah")
        self.btn_tambah.setObjectName("btnPrimary")
        self.btn_tambah.setFixedHeight(38)
        self.btn_tambah.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btn_tambah.clicked.connect(self.tambah_mata_kuliah)

        toolbar.addWidget(self.search)
        toolbar.addWidget(self.btn_tambah)
        main_layout.addLayout(toolbar)

        # ── Stats bar ──
        stats_card = QFrame()
        stats_card.setObjectName("dashboardCard")
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(16, 8, 16, 8)

        self.lbl_total = QLabel("📚  Total Mata Kuliah: 0")
        self.lbl_total.setObjectName("cardTitle")

        stats_layout.addWidget(self.lbl_total)
        stats_layout.addStretch()
        main_layout.addWidget(stats_card)

        # ── Grid ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.container = QWidget()
        self.card_layout = QGridLayout(self.container)
        self.card_layout.setSpacing(12)

        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

    def _build_profile_card(self):
        card = QFrame()
        card.setObjectName("profileCard")
        card.setFixedSize(220, 64)
        card.setCursor(QCursor(Qt.PointingHandCursor))
        card.setToolTip("Klik untuk lihat & edit profil")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)

        info = QVBoxLayout()
        info.setSpacing(2)

        self._lbl_nama = QLabel(self.user.get("nama", "Dosen"))
        self._lbl_nama.setObjectName("profileName")

        role = QLabel(self.user.get("role", "Dosen").capitalize())
        role.setObjectName("profileRole")

        info.addWidget(self._lbl_nama)
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

        card.mousePressEvent = lambda _: self._goto_profil()
        return card

    def _goto_profil(self):
        dashboard = self.window()
        if hasattr(dashboard, "show_profil"):
            dashboard.show_profil()

    def load_data(self):
        success, courses = get_courses(self.user["id"])

        query = self.search.text().lower() if hasattr(self, "search") else ""
        if query:
            courses = [c for c in courses if query in c["nama"].lower() or query in c["kode"].lower()]

        self.lbl_total.setText(f"📚  Total Mata Kuliah: {len(courses)}")
        if not success:
            return

        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        vp_width = self.scroll.viewport().width()
        columns = 1 if vp_width < 600 else (2 if vp_width < 1000 else 3)

        for idx, course in enumerate(courses):
            row, col = divmod(idx, columns)
            self.card_layout.addWidget(self.create_course_card(course), row, col)

        for i in range(columns):
            self.card_layout.setColumnStretch(i, 1)

        last_row = (len(courses) // columns) + 1
        self.card_layout.setRowStretch(last_row, 1)

    def create_course_card(self, course):
        card = QFrame()
        card.setObjectName("dashboardCard")
        card.setMinimumHeight(120)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(5)

        # Header row: nama + kode badge
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        nama = QLabel(course["nama"])
        nama.setObjectName("cardTitle")
        nama.setWordWrap(True)

        badge = QLabel(course["kode"])
        badge.setObjectName("badgeInfo")
        badge.setFixedHeight(22)

        top_row.addWidget(nama, 1)
        top_row.addWidget(badge, 0, Qt.AlignTop)
        layout.addLayout(top_row)

        sks_label = QLabel(f"⚡  {course['sks']} SKS")
        sks_label.setObjectName("labelSub")
        layout.addWidget(sks_label)

        if course.get("deskripsi"):
            desc = QLabel(course["deskripsi"])
            desc.setWordWrap(True)
            desc.setObjectName("labelSub")
            layout.addWidget(desc)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_buka = QPushButton("Kelola  →")
        btn_buka.setObjectName("btnPrimary")
        btn_buka.setMinimumHeight(36)
        btn_buka.setMinimumWidth(100)
        btn_buka.clicked.connect(lambda _, c=course: self.buka_mata_kuliah(c))

        btn_row.addWidget(btn_buka)
        layout.addLayout(btn_row)
        return card

    def buka_mata_kuliah(self, course):
        dashboard = self.window()
        if hasattr(dashboard, "buka_detail_matkul"):
            dashboard.buka_detail_matkul(course)

    def tambah_mata_kuliah(self):
        dialog = DialogMataKuliah()
        if not dialog.exec():
            return

        valid, pesan = validasi_mata_kuliah(
            dialog.kode.text(), dialog.nama.text(),
            dialog.sks.value(), dialog.kode_join.text()
        )
        if not valid:
            QMessageBox.warning(self, "Validasi", pesan)
            return

        sukses, pesan = add_course(
            dialog.kode.text(), dialog.nama.text(),
            dialog.sks.value(), self.user["id"],
            dialog.deskripsi.toPlainText(), dialog.kode_join.text()
        )

        if sukses:
            QMessageBox.information(self, "Sukses", pesan)
            self.load_data()
        else:
            QMessageBox.warning(self, "Gagal", pesan)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.load_data()