import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QMessageBox,
    QLineEdit, QSizePolicy, QTextBrowser
)
from PySide6.QtCore import Qt

from database.db_manager import (
    add_assignment, update_assignment, hapus_assignment,
    get_course_assignments, get_mahasiswa_list, get_submissions,
    beri_nilai
)
from ui.dosen.dialogs.dialogs_tugas import DialogTugas
from ui.dosen.logic.validasi_tugas import validasi_tugas


class TugasPage(QWidget):

    def __init__(self, course):
        super().__init__()
        self.course = course
        self.build_ui()
        self.load_tugas()

    # ──────────────────────────────────────────────────────────
    # ROOT LAYOUT  (sama struktur dengan MateriPage)
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

        self._title_lbl = QLabel("📝  Daftar Tugas")
        self._title_lbl.setObjectName("cardTitle")

        matkul_info = QLabel(
            f"{self.course['nama']}  •  {self.course['kode']}  •  {self.course['sks']} SKS"
        )
        matkul_info.setObjectName("labelSub")

        left.addWidget(self._title_lbl)
        left.addWidget(matkul_info)

        self.btn_tambah = QPushButton("＋  Tambah Tugas")
        self.btn_tambah.setObjectName("btnPrimary")
        self.btn_tambah.setMinimumHeight(38)
        self.btn_tambah.setMinimumWidth(140)
        self.btn_tambah.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.btn_tambah.clicked.connect(self.tambah_tugas)

        header_layout.addLayout(left, 1)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_tambah, 0, Qt.AlignVCenter)
        root.addWidget(header)

        # ── Summary bar (fixed) ──
        summary_bar = QFrame()
        summary_bar.setObjectName("dashboardCard")
        sb_layout = QHBoxLayout(summary_bar)
        sb_layout.setContentsMargins(18, 10, 18, 10)

        self.lbl_total = QLabel("📝  Total Tugas: 0")
        self.lbl_total.setObjectName("cardTitle")
        sb_layout.addWidget(self.lbl_total)
        sb_layout.addStretch()
        root.addWidget(summary_bar)

        # ── Scrollable content ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(0, 8, 0, 8)
        self.main_layout.setSpacing(10)

        self.scroll.setWidget(self.content_widget)
        root.addWidget(self.scroll)

    def _clear_content(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ──────────────────────────────────────────────────────────
    # DAFTAR TUGAS  (grid card, konsisten dengan MateriPage)
    # ──────────────────────────────────────────────────────────

    def _btn(self, label, obj_name, min_w=90):
        b = QPushButton(label)
        b.setObjectName(obj_name)
        b.setMinimumHeight(36)
        b.setMinimumWidth(min_w)
        b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        return b

    def load_tugas(self):
        self._clear_content()
        self._title_lbl.setText("📝  Daftar Tugas")
        self.btn_tambah.show()

        success, tugas = get_course_assignments(self.course["id"])
        self._tugas_list = tugas if (success and tugas) else []
        count = len(self._tugas_list)
        self.lbl_total.setText(f"📝  Total Tugas: {count}")

        if not count:
            empty = QLabel("Belum ada tugas. Klik '＋ Tambah Tugas' untuk membuat tugas baru.")
            empty.setObjectName("labelSub")
            self.main_layout.addWidget(empty)
            self.main_layout.addStretch()
            return

        for item in self._tugas_list:
            self.main_layout.addWidget(self._build_tugas_card(item))

        self.main_layout.addStretch()

    def _build_tugas_card(self, item):
        card = QFrame()
        card.setObjectName("dashboardCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        # ── Info (kiri) ──
        info = QVBoxLayout()
        info.setSpacing(4)

        judul = QLabel(item["judul"])
        judul.setObjectName("cardTitle")
        info.addWidget(judul)

        deadline = QLabel(f"⏰  {item['deadline_date']}")
        deadline.setObjectName("badgeWarning")
        info.addWidget(deadline)

        deskripsi = item.get("deskripsi", "") or ""
        if deskripsi:
            preview = deskripsi if len(deskripsi) <= 80 else deskripsi[:80] + "…"
            desc = QLabel(preview)
            desc.setWordWrap(True)
            desc.setObjectName("labelSub")
            info.addWidget(desc)

        layout.addLayout(info, 1)

        # ── Buttons (kanan) ──
        btns = QHBoxLayout()
        btns.setSpacing(8)

        btn_detail = self._btn("🔍  Detail", "btnSecondary", 100)
        btn_nilai  = self._btn("📥  Nilai",  "btnPrimary",    90)
        btn_edit   = self._btn("✏  Edit",   "btnSecondary",  80)
        btn_hapus  = self._btn("🗑",         "btnDanger",     44)

        btn_detail.clicked.connect(lambda _, d=item: self.show_detail_tugas(d))
        btn_nilai.clicked.connect(lambda _, aid=item["id"]: self.show_submissions(aid))
        btn_edit.clicked.connect(lambda _, d=item: self.edit_tugas(d))
        btn_hapus.clicked.connect(lambda _, aid=item["id"]: self.hapus_tugas_ui(aid))

        btns.addWidget(btn_detail)
        btns.addWidget(btn_nilai)
        btns.addWidget(btn_edit)
        btns.addWidget(btn_hapus)

        layout.addLayout(btns)
        return card

    # ──────────────────────────────────────────────────────────
    # DETAIL TUGAS  (konsisten dengan MateriPage.show_detail)
    # ──────────────────────────────────────────────────────────

    def show_detail_tugas(self, tugas):
        self._clear_content()
        self._title_lbl.setText("📄  Detail Tugas")
        self.btn_tambah.hide()

        # Tombol kembali
        btn_back = QPushButton("←  Kembali ke Daftar Tugas")
        btn_back.setObjectName("btnSecondary")
        btn_back.setMinimumHeight(36)
        btn_back.setMinimumWidth(210)
        btn_back.clicked.connect(self.load_tugas)
        self.main_layout.addWidget(btn_back)

        # Card detail
        card = QFrame()
        card.setObjectName("dashboardCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Judul
        judul = QLabel(tugas["judul"])
        judul.setObjectName("labelTitle")
        judul.setWordWrap(True)
        layout.addWidget(judul)

        # Deadline badge
        dl_row = QHBoxLayout()
        dl_badge = QLabel(f"⏰  Deadline: {tugas['deadline_date']}")
        dl_badge.setObjectName("badgeWarning")
        dl_row.addWidget(dl_badge)
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

        desc_box = QTextBrowser()
        desc_box.setPlainText(tugas.get("deskripsi", "") or "Tidak ada deskripsi.")
        desc_box.setReadOnly(True)
        desc_box.setMinimumHeight(120)
        desc_box.setStyleSheet(
            "QTextBrowser { background:#F8FAFC; border:1px solid #E2E8F0;"
            " border-radius:10px; padding:10px; color:#475569; font-size:13px; }"
        )
        layout.addWidget(desc_box)

        # Stats
        layout.addSpacing(6)
        ok_sub, submissions = get_submissions(tugas["id"])
        total_submit = len(submissions) if ok_sub else 0
        ok_mhs, mahasiswa = get_mahasiswa_list(self.course["id"])
        total_mhs = len(mahasiswa) if ok_mhs else 0

        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        for icon, lbl, val in [
            ("👨‍🎓", "Total Mahasiswa", total_mhs),
            ("📥", "Sudah Submit",    total_submit),
            ("❌", "Belum Submit",    max(0, total_mhs - total_submit)),
        ]:
            sf = QFrame()
            sf.setObjectName("kpiCard")
            sl = QVBoxLayout(sf)
            sl.setContentsMargins(14, 10, 14, 10)
            sl.setSpacing(2)
            num = QLabel(str(val))
            num.setObjectName("kpiValue")
            num.setStyleSheet("font-size:20px; font-weight:700;")
            ll = QLabel(f"{icon}  {lbl}")
            ll.setObjectName("labelSub")
            sl.addWidget(num)
            sl.addWidget(ll)
            stats_row.addWidget(sf)
        layout.addLayout(stats_row)

        # Aksi bawah
        act_row = QHBoxLayout()
        act_row.addStretch()
        btn_ke_nilai = QPushButton("📥  Lihat Pengumpulan & Nilai")
        btn_ke_nilai.setObjectName("btnPrimary")
        btn_ke_nilai.setMinimumHeight(38)
        btn_ke_nilai.clicked.connect(lambda _, aid=tugas["id"]: self.show_submissions(aid))
        act_row.addWidget(btn_ke_nilai)

        btn_edit = QPushButton("✏  Edit Tugas")
        btn_edit.setObjectName("btnSecondary")
        btn_edit.setMinimumHeight(38)
        btn_edit.clicked.connect(lambda _, d=tugas: self.edit_tugas(d))
        act_row.addWidget(btn_edit)

        btn_hapus = QPushButton("🗑  Hapus")
        btn_hapus.setObjectName("btnDanger")
        btn_hapus.setMinimumHeight(38)
        btn_hapus.clicked.connect(lambda _, aid=tugas["id"]: self.hapus_tugas_ui(aid))
        act_row.addWidget(btn_hapus)

        layout.addLayout(act_row)
        self.main_layout.addWidget(card)
        self.main_layout.addStretch()

    # ──────────────────────────────────────────────────────────
    # PENGUMPULAN & INPUT NILAI
    # ──────────────────────────────────────────────────────────

    def show_submissions(self, assignment_id):
        self._clear_content()
        self._title_lbl.setText("📥  Pengumpulan & Penilaian")
        self.btn_tambah.hide()

        # Tombol kembali
        btn_back = QPushButton("←  Kembali ke Daftar Tugas")
        btn_back.setObjectName("btnSecondary")
        btn_back.setMinimumHeight(36)
        btn_back.setMinimumWidth(210)
        btn_back.clicked.connect(self.load_tugas)
        self.main_layout.addWidget(btn_back)

        # Fetch data
        ok_mhs, mahasiswa  = get_mahasiswa_list(self.course["id"])
        ok_sub, submissions = get_submissions(assignment_id)
        submission_map = {s["user_id"]: s for s in submissions} if ok_sub else {}

        total_mhs    = len(mahasiswa) if ok_mhs else 0
        total_submit = len(submission_map)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        for icon, lbl, val in [
            ("👨‍🎓", "Mahasiswa",  total_mhs),
            ("✅",   "Submit",     total_submit),
            ("❌",   "Belum",      max(0, total_mhs - total_submit)),
        ]:
            sf = QFrame()
            sf.setObjectName("kpiCard")
            sf.setFixedHeight(72)
            sl = QHBoxLayout(sf)
            sl.setContentsMargins(14, 8, 14, 8)
            sl.setSpacing(10)
            ico = QLabel(icon)
            ico.setObjectName("kpiIcon")
            info = QVBoxLayout()
            info.setSpacing(0)
            v = QLabel(str(val))
            v.setObjectName("kpiValue")
            v.setStyleSheet("font-size:18px; font-weight:700;")
            t = QLabel(lbl)
            t.setObjectName("kpiTitle")
            info.addWidget(v)
            info.addWidget(t)
            sl.addWidget(ico)
            sl.addLayout(info)
            stats_row.addWidget(sf)
        stats_w = QWidget()
        stats_w.setLayout(stats_row)
        self.main_layout.addWidget(stats_w)

        # Kolom header tabel
        col_hdr = QFrame()
        col_hdr.setObjectName("dashboardCard")
        ch = QHBoxLayout(col_hdr)
        ch.setContentsMargins(18, 8, 18, 8)
        for txt, st in [("Mahasiswa", 3), ("NIM", 2), ("Status", 2), ("Nilai (0–100)", 2), ("Aksi", 3)]:
            l = QLabel(txt)
            l.setObjectName("sectionLabel")
            ch.addWidget(l, st)
        self.main_layout.addWidget(col_hdr)

        # Baris per mahasiswa
        if ok_mhs and mahasiswa:
            for item in mahasiswa:
                user       = item["users"]
                submission = submission_map.get(user["id"])
                self.main_layout.addWidget(
                    self._build_submission_row(user, submission, assignment_id)
                )
        else:
            self.main_layout.addWidget(QLabel("Belum ada mahasiswa terdaftar."))

        self.main_layout.addStretch()

    def _build_submission_row(self, user, submission, assignment_id):
        card = QFrame()
        card.setObjectName("dashboardCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(10)

        # Nama
        nama = QLabel(f"👤  {user['nama']}")
        nama.setObjectName("cardTitle")
        nama.setWordWrap(False)
        layout.addWidget(nama, 3)

        # NIM
        nim = QLabel(user.get("nim_nip", "-"))
        nim.setObjectName("labelSub")
        layout.addWidget(nim, 2)

        # Status
        if submission:
            status = QLabel("✅  Submit")
            status.setObjectName("badgeSuccess")
        else:
            status = QLabel("❌  Belum")
            status.setObjectName("badgeDanger")
        layout.addWidget(status, 2)

        # Input nilai
        nilai_input = QLineEdit()
        nilai_input.setObjectName("nilaiInput")
        nilai_input.setPlaceholderText("0–100")
        nilai_input.setFixedWidth(72)
        nilai_input.setFixedHeight(32)
        if submission and submission.get("nilai") is not None:
            nilai_input.setText(str(submission["nilai"]))
        if not submission:
            nilai_input.setEnabled(False)
            nilai_input.setPlaceholderText("–")
        layout.addWidget(nilai_input, 2)

        # Tombol aksi
        btn_col = QHBoxLayout()
        btn_col.setSpacing(6)

        if submission:
            btn_simpan = QPushButton("💾 Simpan")
            btn_simpan.setObjectName("btnSuccess")
            btn_simpan.setMinimumHeight(32)
            btn_simpan.setMinimumWidth(80)
            btn_simpan.clicked.connect(
                lambda _, sub=submission, ni=nilai_input: self._simpan_nilai(sub, ni)
            )
            btn_col.addWidget(btn_simpan)

            btn_file = QPushButton("👁 File")
            btn_file.setObjectName("btnSecondary")
            btn_file.setMinimumHeight(32)
            btn_file.setMinimumWidth(70)
            btn_file.clicked.connect(
                lambda _, url=submission.get("file_url", ""): self.buka_file(url)
            )
            btn_col.addWidget(btn_file)
        else:
            lbl_dash = QLabel("–")
            lbl_dash.setObjectName("labelSub")
            btn_col.addWidget(lbl_dash)

        btn_w = QWidget()
        btn_w.setLayout(btn_col)
        layout.addWidget(btn_w, 3)

        return card

    def _simpan_nilai(self, submission, nilai_input):
        nilai_text = nilai_input.text().strip()
        if not nilai_text:
            QMessageBox.warning(self, "Validasi", "Nilai tidak boleh kosong.")
            return
        try:
            nilai_int = int(nilai_text)
            if not (0 <= nilai_int <= 100):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Validasi", "Nilai harus berupa angka bulat 0–100.")
            return

        success, pesan = beri_nilai(submission["id"], nilai_text)
        if success:
            QMessageBox.information(self, "Berhasil", f"Nilai {nilai_int} berhasil disimpan.")
        else:
            QMessageBox.warning(self, "Gagal", pesan)

    # ──────────────────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────────────────

    def tambah_tugas(self):
        dialog = DialogTugas()
        if not dialog.exec():
            return

        valid, pesan = validasi_tugas(dialog.judul.text(), dialog.deskripsi.toPlainText())
        if not valid:
            QMessageBox.warning(self, "Validasi", pesan)
            return

        add_assignment(
            self.course["id"],
            dialog.judul.text(),
            dialog.deskripsi.toPlainText(),
            dialog.deadline.date().toString("yyyy-MM-dd")
        )
        self.load_tugas()

    def edit_tugas(self, tugas):
        dialog = DialogTugas()
        dialog.judul.setText(tugas["judul"])
        dialog.deskripsi.setPlainText(tugas.get("deskripsi", ""))
        if not dialog.exec():
            return

        update_assignment(tugas["id"], {
            "judul":         dialog.judul.text(),
            "deskripsi":     dialog.deskripsi.toPlainText(),
            "deadline_date": dialog.deadline.date().toString("yyyy-MM-dd")
        })
        self.load_tugas()

    def hapus_tugas_ui(self, tugas_id):
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            "Yakin ingin menghapus tugas ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        hapus_assignment(tugas_id)
        self.load_tugas()

    def buka_file(self, url):
        if url:
            webbrowser.open(url)
