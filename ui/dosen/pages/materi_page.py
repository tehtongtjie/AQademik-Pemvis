import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QMessageBox, QTextBrowser, QSizePolicy
)
from PySide6.QtCore import Qt

from database.db_manager import get_course_materials, upload_materi, hapus_materi
from ui.dosen.dialogs.dialogs_materi import DialogMateri
from ui.dosen.logic.validasi_materi import validasi_materi


class MateriPage(QWidget):

    def __init__(self, course):
        super().__init__()
        self.course = course
        self.build_ui()
        self.load_materi()

    # ──────────────────────────────────────────────────────────
    # ROOT LAYOUT
    # ──────────────────────────────────────────────────────────

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar (fixed) ──
        header = QFrame()
        header.setObjectName("dashboardCard")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 14)

        left = QVBoxLayout()
        left.setSpacing(3)

        self._title_lbl = QLabel("📚  Materi Perkuliahan")
        self._title_lbl.setObjectName("cardTitle")

        matkul_info = QLabel(
            f"{self.course['nama']}  •  {self.course['kode']}  •  {self.course['sks']} SKS"
        )
        matkul_info.setObjectName("labelSub")

        left.addWidget(self._title_lbl)
        left.addWidget(matkul_info)

        self.btn_upload = QPushButton("＋  Upload Materi")
        self.btn_upload.setObjectName("btnPrimary")
        self.btn_upload.setMinimumHeight(38)
        self.btn_upload.setMinimumWidth(150)
        self.btn_upload.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_upload.clicked.connect(self.tambah_materi)

        header_layout.addLayout(left, 1)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_upload, 0, Qt.AlignVCenter)
        root.addWidget(header)

        # ── Summary bar (fixed) ──
        summary_bar = QFrame()
        summary_bar.setObjectName("dashboardCard")
        sb_layout = QHBoxLayout(summary_bar)
        sb_layout.setContentsMargins(18, 10, 18, 10)

        self.lbl_total = QLabel("📚  Total Materi: 0")
        self.lbl_total.setObjectName("cardTitle")
        sb_layout.addWidget(self.lbl_total)
        sb_layout.addStretch()
        root.addWidget(summary_bar)

        # ── Scrollable area — berisi daftar ATAU detail ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 8, 0, 8)
        self.content_layout.setSpacing(10)

        self.scroll.setWidget(self.content_widget)
        root.addWidget(self.scroll)

    # ──────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _btn(self, label, obj_name, min_w=90):
        b = QPushButton(label)
        b.setObjectName(obj_name)
        b.setMinimumHeight(36)
        b.setMinimumWidth(min_w)
        b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        return b

    # ──────────────────────────────────────────────────────────
    # DAFTAR MATERI
    # ──────────────────────────────────────────────────────────

    def load_materi(self):
        self._clear_content()

        # Tampilkan header + upload button
        self._title_lbl.setText("📚  Materi Perkuliahan")
        self.btn_upload.show()

        success, materi = get_course_materials(self.course["id"])
        count = len(materi) if materi else 0
        self.lbl_total.setText(f"📚  Total Materi: {count}")

        if not success or not materi:
            empty = QLabel("Belum ada materi. Klik '＋ Upload Materi' untuk memulai.")
            empty.setObjectName("labelSub")
            self.content_layout.addWidget(empty)
            self.content_layout.addStretch()
            return

        for item in materi:
            self.content_layout.addWidget(self._build_materi_card(item))

        self.content_layout.addStretch()

    def _build_materi_card(self, item):
        card = QFrame()
        card.setObjectName("dashboardCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        # ── Info ──
        info = QVBoxLayout()
        info.setSpacing(4)

        judul = QLabel(item["judul"])
        judul.setObjectName("cardTitle")
        info.addWidget(judul)

        deskripsi = item.get("deskripsi", "")
        if deskripsi:
            preview = deskripsi if len(deskripsi) <= 80 else deskripsi[:80] + "…"
            desc = QLabel(preview)
            desc.setWordWrap(True)
            desc.setObjectName("labelSub")
            info.addWidget(desc)

        fname = item.get("file_name") or item.get("filename", "")
        if fname:
            file_lbl = QLabel(f"📎  {fname}")
            file_lbl.setObjectName("labelSub")
            info.addWidget(file_lbl)

        layout.addLayout(info, 1)

        # ── Buttons ──
        btns = QHBoxLayout()
        btns.setSpacing(8)

        btn_detail = self._btn("🔍  Detail",  "btnSecondary", 100)
        btn_lihat  = self._btn("👁  Lihat",   "btnPrimary",    90)
        btn_edit   = self._btn("✏  Edit",    "btnSecondary",  80)
        btn_hapus  = self._btn("🗑",          "btnDanger",     44)

        btn_detail.clicked.connect(lambda _, d=item: self.show_detail(d))
        btn_lihat.clicked.connect(lambda _, url=item.get("file_url", ""): self.buka_file(url))
        btn_edit.clicked.connect(lambda _, d=item: self.edit_materi(d))
        btn_hapus.clicked.connect(lambda _, mid=item["id"]: self.hapus_materi_ui(mid))

        btns.addWidget(btn_detail)
        btns.addWidget(btn_lihat)
        btns.addWidget(btn_edit)
        btns.addWidget(btn_hapus)

        layout.addLayout(btns)
        return card

    # ──────────────────────────────────────────────────────────
    # DETAIL MATERI  — inline, sama pola dengan tugas_page
    # ──────────────────────────────────────────────────────────

    def show_detail(self, item):
        self._clear_content()
        self._title_lbl.setText("🔍  Detail Materi")
        self.btn_upload.hide()

        # ── Tombol kembali ──
        btn_back = QPushButton("←  Kembali ke Daftar Materi")
        btn_back.setObjectName("btnSecondary")
        btn_back.setMinimumHeight(36)
        btn_back.setMinimumWidth(210)
        btn_back.clicked.connect(self.load_materi)
        self.content_layout.addWidget(btn_back)

        # ── Card detail ──
        card = QFrame()
        card.setObjectName("dashboardCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        # Judul
        judul = QLabel(item["judul"])
        judul.setObjectName("labelTitle")
        judul.setWordWrap(True)
        layout.addWidget(judul)

        # File badge
        fname = item.get("file_name") or item.get("filename", "")
        if fname:
            dl_row = QHBoxLayout()
            file_badge = QLabel(f"📎  {fname}")
            file_badge.setObjectName("badgeInfo")
            dl_row.addWidget(file_badge)
            dl_row.addStretch()
            layout.addLayout(dl_row)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background:#E2E8F0; max-height:1px; margin:4px 0;")
        layout.addWidget(div)

        # Deskripsi
        sec = QLabel("Deskripsi")
        sec.setObjectName("sectionLabel")
        layout.addWidget(sec)

        deskripsi = item.get("deskripsi", "") or "Tidak ada deskripsi."
        desc_box = QTextBrowser()
        desc_box.setPlainText(deskripsi)
        desc_box.setReadOnly(True)
        desc_box.setMinimumHeight(130)
        desc_box.setStyleSheet(
            "QTextBrowser { background:#F8FAFC; border:1px solid #E2E8F0;"
            " border-radius:10px; padding:10px; color:#475569; font-size:13px; }"
        )
        layout.addWidget(desc_box)

        # Tombol aksi
        act_row = QHBoxLayout()
        act_row.setSpacing(10)
        act_row.addStretch()

        file_url = item.get("file_url", "")
        if file_url:
            btn_buka = QPushButton("🔗  Buka File")
            btn_buka.setObjectName("btnPrimary")
            btn_buka.setMinimumHeight(38)
            btn_buka.clicked.connect(lambda: webbrowser.open(file_url))
            act_row.addWidget(btn_buka)

        btn_edit = QPushButton("✏  Edit Materi")
        btn_edit.setObjectName("btnSecondary")
        btn_edit.setMinimumHeight(38)
        btn_edit.clicked.connect(lambda _, d=item: self.edit_materi(d))
        act_row.addWidget(btn_edit)

        btn_hapus = QPushButton("🗑  Hapus")
        btn_hapus.setObjectName("btnDanger")
        btn_hapus.setMinimumHeight(38)
        btn_hapus.clicked.connect(lambda _, mid=item["id"]: self.hapus_materi_ui(mid))
        act_row.addWidget(btn_hapus)

        layout.addLayout(act_row)
        self.content_layout.addWidget(card)
        self.content_layout.addStretch()

    # ──────────────────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────────────────

    def tambah_materi(self):
        dialog = DialogMateri()
        if not dialog.exec():
            return

        valid, pesan = validasi_materi(dialog.judul.text(), dialog.file_path)
        if not valid:
            QMessageBox.warning(self, "Validasi", pesan)
            return

        success, pesan = upload_materi(
            dialog.file_path, self.course["id"],
            dialog.judul.text(), dialog.deskripsi.toPlainText()
        )
        if not success:
            QMessageBox.warning(self, "Error", pesan)
        self.load_materi()

    def edit_materi(self, materi):
        dialog = DialogMateri()
        dialog.judul.setText(materi["judul"])
        dialog.deskripsi.setPlainText(materi.get("deskripsi", ""))

        if not dialog.exec():
            return

        # update_materi(materi["id"], dialog.judul.text(), dialog.deskripsi.toPlainText())
        self.load_materi()

    def hapus_materi_ui(self, materi_id):
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Yakin ingin menghapus materi ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        hapus_materi(materi_id)
        self.load_materi()

    def buka_file(self, url):
        if url:
            webbrowser.open(url)
