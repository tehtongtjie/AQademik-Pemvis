from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTimeEdit,
    QPushButton
)

from PySide6.QtCore import QTime


class DialogJadwal(QDialog):

    def __init__(self, courses=None):
        super().__init__()

        self.courses = courses or []

        self.setWindowTitle(
            "Tambah Jadwal"
        )

        self.resize(
            500,
            550
        )

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout.setSpacing(
            12
        )

        # =====================
        # HEADER
        # =====================

        title = QLabel(
            "Tambah Jadwal"
        )

        title.setObjectName(
            "labelTitle"
        )

        subtitle = QLabel(
            "Tambahkan jadwal perkuliahan."
        )

        subtitle.setObjectName(
            "labelSub"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            10
        )

        # =====================
        # HARI
        # =====================
        label_matkul = QLabel(
            "Mata Kuliah"
        )

        label_matkul.setObjectName(
            "labelField"
        )

        self.matkul = QComboBox()

        for course in self.courses:

            self.matkul.addItem(
                course["nama"],
                course
            )

        layout.addWidget(
            label_matkul
        )

        layout.addWidget(
            self.matkul
        )

        label_hari = QLabel(
            "Hari"
        )

        label_hari.setObjectName(
            "labelField"
        )

        self.hari = QComboBox()

        self.hari.addItems([
            "Senin",
            "Selasa",
            "Rabu",
            "Kamis",
            "Jumat",
            "Sabtu",
            "Minggu"
        ])

        layout.addWidget(
            label_hari
        )

        layout.addWidget(
            self.hari
        )

        # =====================
        # JAM MULAI
        # =====================

        label_mulai = QLabel(
            "Jam Mulai"
        )

        label_mulai.setObjectName(
            "labelField"
        )

        self.jam_mulai = QTimeEdit()

        self.jam_mulai.setTime(
            QTime(8, 0)
        )

        self.jam_mulai.setDisplayFormat(
            "HH:mm"
        )

        self.jam_mulai.setMinimumHeight(
            40
        )

        layout.addWidget(
            label_mulai
        )

        layout.addWidget(
            self.jam_mulai
        )

        # =====================
        # JAM SELESAI
        # =====================

        label_selesai = QLabel(
            "Jam Selesai"
        )

        label_selesai.setObjectName(
            "labelField"
        )

        self.jam_selesai = QTimeEdit()

        self.jam_selesai.setTime(
            QTime(10, 0)
        )

        self.jam_selesai.setDisplayFormat(
            "HH:mm"
        )

        self.jam_selesai.setMinimumHeight(
            40
        )

        layout.addWidget(
            label_selesai
        )

        layout.addWidget(
            self.jam_selesai
        )

        # =====================
        # RUANGAN
        # =====================

        label_ruangan = QLabel(
            "Ruangan"
        )

        label_ruangan.setObjectName(
            "labelField"
        )

        self.ruangan = QLineEdit()

        self.ruangan.setPlaceholderText(
            "Contoh: Lab Komputer 1"
        )

        layout.addWidget(
            label_ruangan
        )

        layout.addWidget(
            self.ruangan
        )

        # =====================
        # BUTTON
        # =====================

        layout.addStretch()

        button_layout = QHBoxLayout()

        btn_batal = QPushButton(
            "Batal"
        )

        btn_batal.setObjectName(
            "btnSecondary"
        )

        btn_batal.clicked.connect(
            self.reject
        )

        self.btn_simpan = QPushButton(
            "Simpan Jadwal"
        )

        self.btn_simpan.setObjectName(
            "btnPrimary"
        )

        self.btn_simpan.clicked.connect(
            self.accept
        )

        button_layout.addWidget(
            btn_batal
        )

        button_layout.addWidget(
            self.btn_simpan
        )

        layout.addLayout(
            button_layout
        )