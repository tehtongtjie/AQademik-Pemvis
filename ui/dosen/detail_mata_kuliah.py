from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame
)


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

        main_layout.addWidget(
            btn_kembali
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

        # ======================
        # MENU MATA KULIAH
        # ======================

        materi_card = QFrame()
        materi_card.setObjectName(
            "dashboardCard"
        )

        materi_layout = QVBoxLayout(
            materi_card
        )

        materi_title = QLabel(
            "📚 Materi"
        )

        self.btn_materi = QPushButton(
            "Kelola Materi"
        )

        self.btn_materi.setObjectName(
            "btnPrimary"
        )

        materi_layout.addWidget(
            materi_title
        )

        materi_layout.addWidget(
            self.btn_materi
        )

        main_layout.addWidget(
            materi_card
        )

        tugas_card = QFrame()

        tugas_card.setObjectName(
            "dashboardCard"
        )

        tugas_layout = QVBoxLayout(
            tugas_card
        )

        tugas_title = QLabel(
            "📝 Tugas"
        )

        self.btn_tugas = QPushButton(
            "Kelola Tugas"
        )

        self.btn_tugas.setObjectName(
            "btnPrimary"
        )

        tugas_layout.addWidget(
            tugas_title
        )

        tugas_layout.addWidget(
            self.btn_tugas
        )

        main_layout.addWidget(
            tugas_card
        )

        mahasiswa_card = QFrame()

        mahasiswa_card.setObjectName(
            "dashboardCard"
        )

        mahasiswa_layout = QVBoxLayout(
            mahasiswa_card
        )

        mahasiswa_title = QLabel(
            "👨‍🎓 Mahasiswa"
        )

        self.btn_mahasiswa = QPushButton(
            "Lihat Mahasiswa"
        )

        self.btn_mahasiswa.setObjectName(
            "btnPrimary"
        )

        mahasiswa_layout.addWidget(
            mahasiswa_title
        )

        mahasiswa_layout.addWidget(
            self.btn_mahasiswa
        )

        main_layout.addWidget(
            mahasiswa_card
        )

        main_layout.addStretch()