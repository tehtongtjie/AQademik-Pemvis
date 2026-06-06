from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QScrollArea, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt

from database.db_manager import get_mahasiswa_list


class MahasiswaPage(QWidget):

    def __init__(self, course):
        super().__init__()
        self.course = course
        self.all_mahasiswa = []
        self.build_ui()
        self.load_mahasiswa()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──
        header = QFrame()
        header.setObjectName("dashboardCard")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 12, 18, 12)

        left = QVBoxLayout()
        left.setSpacing(3)

        title = QLabel("👨‍🎓  Daftar Mahasiswa")
        title.setObjectName("cardTitle")

        matkul_info = QLabel(f"{self.course['nama']}  •  {self.course['kode']}")
        matkul_info.setObjectName("labelSub")

        left.addWidget(title)
        left.addWidget(matkul_info)
        header_layout.addLayout(left)
        header_layout.addStretch()
        root.addWidget(header)

        # ── Toolbar: total + search ──
        toolbar = QFrame()
        toolbar.setObjectName("dashboardCard")

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(18, 10, 18, 10)
        toolbar_layout.setSpacing(12)

        self.lbl_total = QLabel("👨‍🎓  Total: 0 mahasiswa")
        self.lbl_total.setObjectName("cardTitle")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Cari nama atau NIM...")
        self.search.setMinimumWidth(200)
        self.search.setMaximumWidth(300)
        self.search.setFixedHeight(36)
        self.search.textChanged.connect(self._filter_mahasiswa)

        toolbar_layout.addWidget(self.lbl_total)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search)
        root.addWidget(toolbar)

        # ── Kolom header tabel ──
        col_hdr = QFrame()
        col_hdr.setObjectName("dashboardCard")
        ch_layout = QHBoxLayout(col_hdr)
        ch_layout.setContentsMargins(18, 8, 18, 8)
        ch_layout.setSpacing(0)

        for txt, stretch in [("No", 1), ("Nama", 4), ("NIM", 3), ("Email", 4)]:
            lbl = QLabel(txt)
            lbl.setObjectName("sectionLabel")
            ch_layout.addWidget(lbl, stretch)

        root.addWidget(col_hdr)

        # ── Scrollable list ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 6, 0, 6)
        self.list_layout.setSpacing(6)

        self.scroll.setWidget(self.list_widget)
        root.addWidget(self.scroll)

    def _clear_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def load_mahasiswa(self):
        success, mahasiswa = get_mahasiswa_list(self.course["id"])
        self.all_mahasiswa = mahasiswa if success else []
        self.lbl_total.setText(f"👨‍🎓  Total: {len(self.all_mahasiswa)} mahasiswa")
        self._render_list(self.all_mahasiswa)

    def _filter_mahasiswa(self):
        query = self.search.text().lower()
        if not query:
            self._render_list(self.all_mahasiswa)
            return
        filtered = [
            m for m in self.all_mahasiswa
            if query in m["users"]["nama"].lower()
            or query in (m["users"].get("nim_nip") or "").lower()
            or query in (m["users"].get("email") or "").lower()
        ]
        self._render_list(filtered)

    def _render_list(self, mahasiswa_list):
        self._clear_list()

        if not mahasiswa_list:
            empty = QLabel("Tidak ada mahasiswa yang ditemukan.")
            empty.setObjectName("labelSub")
            self.list_layout.addWidget(empty)
            self.list_layout.addStretch()
            return

        for idx, item in enumerate(mahasiswa_list):
            self.list_layout.addWidget(self._build_mahasiswa_row(item, idx + 1))

        self.list_layout.addStretch()

    def _build_mahasiswa_row(self, item, number):
        user = item["users"]

        card = QFrame()
        card.setObjectName("dashboardCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(0)

        # No
        num_badge = QLabel(str(number))
        num_badge.setObjectName("badgeInfo")
        num_badge.setFixedWidth(28)
        num_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(num_badge, 1)

        # Nama (dengan avatar emoji)
        nama_row = QHBoxLayout()
        nama_row.setSpacing(8)
        avatar = QLabel("👤")
        avatar.setObjectName("profileAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        nama_lbl = QLabel(user["nama"])
        nama_lbl.setObjectName("cardTitle")
        nama_lbl.setWordWrap(False)
        nama_row.addWidget(avatar)
        nama_row.addWidget(nama_lbl)
        nama_row.addStretch()
        nama_w = QWidget()
        nama_w.setLayout(nama_row)
        layout.addWidget(nama_w, 4)

        # NIM
        nim_lbl = QLabel(user.get("nim_nip") or "-")
        nim_lbl.setObjectName("labelSub")
        layout.addWidget(nim_lbl, 3)

        # Email — horizontal sejajar
        email_lbl = QLabel(user.get("email") or "-")
        email_lbl.setObjectName("labelSub")
        email_lbl.setWordWrap(False)
        layout.addWidget(email_lbl, 4)

        return card
