from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame
)

from database.db_manager import (
    get_course_materials,
    get_course_assignments,
    get_mahasiswa_list,
    get_submissions,
    upload_materi,
    hapus_materi
)
from ui.dosen.dialogs.dialogs_materi import DialogMateri

class DetailMataKuliah(QWidget):

    def __init__(self, course):
        super().__init__()

        self.course = course

        self.build_ui()

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        main_layout.setSpacing(20)

        # ======================
        # HEADER
        # ======================

        btn_kembali = QPushButton(
            "← Kembali"
        )

        btn_kembali.setObjectName(
            "btnSecondary"
        )

        self.btn_kembali = btn_kembali

        top_layout = QHBoxLayout()

        btn_kembali.setFixedWidth(
            120
        )

        top_layout.addWidget(
            btn_kembali
        )

        top_layout.addStretch()

        main_layout.addLayout(
            top_layout
        )

        title = QLabel(
            self.course["nama"]
        )

        title.setObjectName(
            "labelTitle"
        )

        subtitle = QLabel(
            f"Kode: {self.course['kode']} | "
            f"SKS: {self.course['sks']}"
        )

        subtitle.setObjectName(
            "labelSub"
        )

        main_layout.addWidget(
            title
        )

        main_layout.addWidget(
            subtitle
        )

        # ======================
        # INFORMASI
        # ======================

        info_card = QFrame()

        info_card.setObjectName(
            "dashboardCard"
        )

        info_layout = QVBoxLayout(
            info_card
        )

        info_layout.addWidget(
            QLabel(
                f"Dosen : {self.course['users']['nama']}"
            )
        )

        info_layout.addWidget(
            QLabel(
                f"Kode Join : {self.course.get('enroll_code', '-')}"
            )
        )

        info_layout.addWidget(
            QLabel(
                f"Deskripsi : {self.course.get('deskripsi', '-')}"
            )
        )

        main_layout.addWidget(
            info_card
        )

        menu_layout = QHBoxLayout()

        self.btn_materi = QPushButton(
            "📚 Materi"
        )

        self.btn_tugas = QPushButton(
            "📝 Tugas"
        )

        self.btn_mahasiswa = QPushButton(
            "👨‍🎓 Mahasiswa"
        )

        for btn in [
            self.btn_materi,
            self.btn_tugas,
            self.btn_mahasiswa
        ]:
            btn.setObjectName(
                "btnPrimary"
            )

            btn.setMinimumHeight(
                42
            )

            menu_layout.addWidget(
                btn
            )

        main_layout.addLayout(
            menu_layout
        )

        self.content_area = QFrame()

        self.content_area.setObjectName(
            "dashboardCard"
        )

        self.content_layout = QVBoxLayout(
            self.content_area
        )

        main_layout.addWidget(
            self.content_area
        )

        self.btn_materi.clicked.connect(
            self.show_materi
        )

        self.btn_tugas.clicked.connect(
            self.show_tugas
        )

        self.btn_mahasiswa.clicked.connect(
            self.show_mahasiswa
        )

        self.show_materi()
    
    def clear_content(self):

        while self.content_layout.count():

            item = self.content_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

    def show_materi(self):

        self.clear_content()

        header = QHBoxLayout()

        title = QLabel(
            "📚 Materi Perkuliahan"
        )

        title.setObjectName(
            "labelTitle"
        )

        btn_upload = QPushButton(
            "+ Upload Materi"
        )

        btn_upload.setObjectName(
            "btnPrimary"
        )

        btn_upload.setFixedWidth(
            180
        )

        btn_upload.clicked.connect(
            self.tambah_materi
        )

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_upload)

        self.content_layout.addLayout(
            header
        )

        success, materi = get_course_materials(
            self.course["id"]
        )

        if not success or not materi:

            print("SUCCESS:", success)
            print("MATERI:", materi)

            self.content_layout.addWidget(
                QLabel("Belum ada materi.")
            )

            return

        for item in materi:

            card = QFrame()
            card.setObjectName("dashboardCard")

            layout = QVBoxLayout(card)

            judul = QLabel(
                item["judul"]
            )

            judul.setObjectName(
                "labelTitle"
            )

            layout.addWidget(
                judul
            )

            deskripsi = QLabel(
                item.get(
                    "deskripsi",
                    "-"
                )
            )

            deskripsi.setWordWrap(
                True
            )

            layout.addWidget(
                deskripsi
            )

            button_layout = QHBoxLayout()

            btn_buka = QPushButton(
                "📄 Buka"
            )

            btn_buka.setObjectName(
                "btnPrimary"
            )

            btn_hapus = QPushButton(
                "🗑 Hapus"
            )

            btn_hapus.setObjectName(
                "btnSecondary"
            )

            button_layout.addWidget(
                btn_buka
            )

            button_layout.addWidget(
                btn_hapus
            )

            layout.addLayout(
                button_layout
            )

            btn_hapus.clicked.connect(
                lambda _, mid=item["id"]:
                self.hapus_materi_ui(mid)
            )

            self.content_layout.addWidget(
                card
            )

    def show_tugas(self):

        self.clear_content()

        title = QLabel("Daftar Tugas")
        title.setObjectName("labelTitle")

        self.content_layout.addWidget(title)

        success, tugas = get_course_assignments(
            self.course["id"]
        )

        if not success or not tugas:

            self.content_layout.addWidget(
                QLabel("Belum ada tugas.")
            )

            return

        for item in tugas:

            card = QFrame()
            card.setObjectName(
                "dashboardCard"
            )

            layout = QVBoxLayout(card)

            judul = QLabel(
                item["judul"]
            )

            judul.setObjectName(
                "labelTitle"
            )

            layout.addWidget(
                judul
            )

            deadline = QLabel(
                f"⏰ Deadline: {item['deadline_date']}"
            )

            deadline.setObjectName(
                "labelSub"
            )

            layout.addWidget(
                deadline
            )

            btn_lihat = QPushButton(
                "📥 Lihat Pengumpulan"
            )

            btn_lihat.setObjectName(
                "btnPrimary"
            )

            btn_lihat.clicked.connect(
                lambda _, aid=item["id"]:
                self.show_submissions(aid)
            )

            layout.addWidget(
                btn_lihat
            )

            self.content_layout.addWidget(
                card
            )

    def show_mahasiswa(self):

        self.clear_content()

        title = QLabel(
            "Daftar Mahasiswa"
        )

        title.setObjectName(
            "labelTitle"
        )

        self.content_layout.addWidget(
            title
        )

        success, mahasiswa = get_mahasiswa_list(
            self.course["id"]
        )

        if not success or not mahasiswa:

            self.content_layout.addWidget(
                QLabel(
                    "Belum ada mahasiswa."
                )
            )

            return

        for item in mahasiswa:

            user = item["users"]

            card = QFrame()

            card.setObjectName(
                "dashboardCard"
            )

            layout = QVBoxLayout(
                card
            )

            nama = QLabel(
                user["nama"]
            )

            nama.setObjectName(
                "labelTitle"
            )

            layout.addWidget(
                nama
            )

            nim = QLabel(
                f"NIM: {user['nim_nip']}"
            )

            nim.setObjectName(
                "labelSub"
            )

            layout.addWidget(
                nim
            )

            self.content_layout.addWidget(
                card
            )

    def show_submissions(
        self,
        assignment_id
    ):

        self.clear_content()

        title = QLabel(
            "Pengumpulan Tugas"
        )

        title.setObjectName(
            "labelTitle"
        )

        self.content_layout.addWidget(
            title
        )

        success, submissions = get_submissions(
            assignment_id
        )

        if not success or not submissions:

            self.content_layout.addWidget(
                QLabel(
                    "Belum ada pengumpulan."
                )
            )

            return

        for sub in submissions:

            card = QFrame()

            card.setObjectName(
                "dashboardCard"
            )

            layout = QVBoxLayout(
                card
            )

            user = sub["users"]

            nama = QLabel(
                user["nama"]
            )

            nama.setObjectName(
                "labelTitle"
            )

            layout.addWidget(
                nama
            )

            layout.addWidget(
                QLabel(
                    f"NIM: {user['nim_nip']}"
                )
            )

            layout.addWidget(
                QLabel(
                    f"📄 {sub['file_name']}"
                )
            )

            layout.addWidget(
                QLabel(
                    f"⭐ Nilai: {sub.get('nilai', '-')}"
                )
            )

            self.content_layout.addWidget(
                card
            )
    
    def tambah_materi(self):

        dialog = DialogMateri()

        if not dialog.exec():
            return

        if not dialog.file_path:
            return

        success, pesan = upload_materi(
            dialog.file_path,
            self.course["id"],
            dialog.judul.text(),
            dialog.deskripsi.toPlainText()
        )

        print(success)
        print(pesan)

        self.show_materi()

    def hapus_materi_ui(
        self,
        materi_id
    ):

        hapus_materi(
            materi_id
        )

        self.show_materi()