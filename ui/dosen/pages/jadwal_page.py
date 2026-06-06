from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QCursor

from database.db_manager import (
    get_courses, get_schedules, add_schedule,
    update_schedule, hapus_schedule
)
from ui.dosen.dialogs.dialogs_jadwal import DialogJadwal
from ui.dosen.logic.validasi_jadwal import validasi_jadwal

# ── Day ordering helper ──
DAY_ORDER = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


class JadwalPage(QWidget):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.build_ui()
        self.load_jadwal()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(20)

        # ── Page header ──
        header_frame = QFrame()
        header_frame.setObjectName("dashboardHeader")

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 16, 20, 16)

        left = QVBoxLayout()
        left.setSpacing(4)

        title = QLabel("Kelola Jadwal")
        title.setObjectName("labelTitle")

        sub = QLabel("Atur jadwal perkuliahan setiap mata kuliah.")
        sub.setObjectName("labelSub")

        left.addWidget(title)
        left.addWidget(sub)

        self.btn_tambah = QPushButton("＋  Tambah Jadwal")
        self.btn_tambah.setObjectName("btnPrimary")
        self.btn_tambah.setFixedHeight(38)
        self.btn_tambah.setMinimumWidth(140)
        self.btn_tambah.clicked.connect(self.tambah_jadwal)

        header_layout.addLayout(left)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_tambah)
        header_layout.addSpacing(12)
        header_layout.addWidget(self._build_profile_card())

        root.addWidget(header_frame)

        # ── Scrollable content ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(12)

        self.scroll.setWidget(self.content_widget)
        root.addWidget(self.scroll)

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

    def _clear_content(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ──────────────────────────────────────────────────────────
    # LOAD
    # ──────────────────────────────────────────────────────────

    def load_jadwal(self):
        self._clear_content()

        success, courses = get_courses(self.user["id"])
        course_ids = [c["id"] for c in courses] if success else []

        ok, schedules = get_schedules()
        jadwal_list = [j for j in schedules if j["course_id"] in course_ids] if ok else []

        if not ok or not jadwal_list:
            empty = QLabel("📅  Belum ada jadwal. Klik '+ Tambah Jadwal' untuk memulai.")
            empty.setObjectName("labelSub")
            self.main_layout.addWidget(empty)
            self.main_layout.addStretch()
            return

        # Sort by day order
        jadwal_list.sort(key=lambda j: DAY_ORDER.index(j["day_of_week"])
                         if j["day_of_week"] in DAY_ORDER else 99)

        for jadwal in jadwal_list:
            self.main_layout.addWidget(self._build_jadwal_card(jadwal))

        self.main_layout.addStretch()

    def _build_jadwal_card(self, jadwal):
        card = QFrame()
        card.setObjectName("dashboardCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(16)

        # ── Day badge ──
        day_badge = QLabel(jadwal.get("day_of_week", "-"))
        day_badge.setObjectName("badgeInfo")
        day_badge.setFixedWidth(64)
        day_badge.setAlignment(Qt.AlignCenter)

        layout.addWidget(day_badge, 0, Qt.AlignVCenter)

        # ── Info ──
        info = QVBoxLayout()
        info.setSpacing(3)

        matkul_lbl = QLabel(jadwal.get("course_name", "-"))
        matkul_lbl.setObjectName("cardTitle")
        info.addWidget(matkul_lbl)

        detail_lbl = QLabel(
            f"🕐  {jadwal['start_time']} – {jadwal['end_time']}   "
            f"🏫  {jadwal['room']}   "
            f"👤  {jadwal['lecturer']}"
        )
        detail_lbl.setObjectName("labelSub")
        info.addWidget(detail_lbl)

        layout.addLayout(info, 1)

        # ── Buttons ──
        btn_edit = QPushButton("✏  Edit")
        btn_edit.setObjectName("btnSecondary")
        btn_edit.setMinimumHeight(36)
        btn_edit.setMinimumWidth(80)

        btn_hapus = QPushButton("🗑  Hapus")
        btn_hapus.setObjectName("btnDanger")
        btn_hapus.setMinimumHeight(36)
        btn_hapus.setMinimumWidth(80)

        btn_edit.clicked.connect(lambda _, d=jadwal: self.edit_jadwal(d))
        btn_hapus.clicked.connect(lambda _, sid=jadwal["id"]: self.hapus_jadwal(sid))

        btn_group = QHBoxLayout()
        btn_group.setSpacing(8)
        btn_group.addWidget(btn_edit)
        btn_group.addWidget(btn_hapus)

        layout.addLayout(btn_group)
        return card

    # ──────────────────────────────────────────────────────────
    # TAMBAH
    # ──────────────────────────────────────────────────────────

    def tambah_jadwal(self):
        success, courses = get_courses(self.user["id"])
        if not success:
            QMessageBox.warning(self, "Error", "Gagal mengambil mata kuliah.")
            return

        if not courses:
            QMessageBox.warning(self, "Validasi", "Belum ada mata kuliah yang dibuat.")
            return

        dialog = DialogJadwal(courses)
        if not dialog.exec():
            return

        valid, pesan = validasi_jadwal(
            dialog.hari.currentText(),
            dialog.jam_mulai.time(),
            dialog.jam_selesai.time(),
            dialog.ruangan.text()
        )
        if not valid:
            QMessageBox.warning(self, "Validasi", pesan)
            return

        course = dialog.matkul.currentData()
        success, pesan = add_schedule(
            dialog.hari.currentText(),
            course["id"], course["nama"],
            self.user["nama"],
            dialog.jam_mulai.time().toString("HH:mm"),
            dialog.jam_selesai.time().toString("HH:mm"),
            dialog.ruangan.text()
        )

        if not success:
            QMessageBox.warning(self, "Error", pesan)
            return

        self.load_jadwal()

    # ──────────────────────────────────────────────────────────
    # EDIT
    # ──────────────────────────────────────────────────────────

    def edit_jadwal(self, jadwal):
        success, courses = get_courses(self.user["id"])
        dialog = DialogJadwal(courses)

        dialog.hari.setCurrentText(jadwal["day_of_week"])
        dialog.jam_mulai.setTime(QTime.fromString(jadwal["start_time"], "HH:mm"))
        dialog.jam_selesai.setTime(QTime.fromString(jadwal["end_time"], "HH:mm"))
        dialog.ruangan.setText(jadwal["room"])

        if not dialog.exec():
            return

        valid, pesan = validasi_jadwal(
            dialog.hari.currentText(),
            dialog.jam_mulai.time(),
            dialog.jam_selesai.time(),
            dialog.ruangan.text()
        )
        if not valid:
            QMessageBox.warning(self, "Validasi", pesan)
            return

        success, pesan = update_schedule(jadwal["id"], {
            "day_of_week": dialog.hari.currentText(),
            "start_time":  dialog.jam_mulai.time().toString("HH:mm"),
            "end_time":    dialog.jam_selesai.time().toString("HH:mm"),
            "room":        dialog.ruangan.text()
        })

        if not success:
            QMessageBox.warning(self, "Error", pesan)
            return

        self.load_jadwal()

    # ──────────────────────────────────────────────────────────
    # HAPUS
    # ──────────────────────────────────────────────────────────

    def hapus_jadwal(self, jadwal_id):
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Yakin ingin menghapus jadwal ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        success, pesan = hapus_schedule(jadwal_id)
        if not success:
            QMessageBox.warning(self, "Error", pesan)
            return

        self.load_jadwal()