from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDateEdit,
    QPushButton
)

from PySide6.QtCore import QDate


class DialogTugas(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Tambah Tugas"
        )

        self.resize(500, 500)

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout.setSpacing(12)

        # HEADER

        title = QLabel(
            "Tambah Tugas"
        )

        title.setObjectName(
            "labelTitle"
        )

        subtitle = QLabel(
            "Buat tugas baru untuk mahasiswa."
        )

        subtitle.setObjectName(
            "labelSub"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # JUDUL

        label_judul = QLabel(
            "Judul Tugas"
        )

        label_judul.setObjectName(
            "labelField"
        )

        self.judul = QLineEdit()

        self.judul.setPlaceholderText(
            "Contoh: Tugas Pertemuan 1"
        )

        layout.addWidget(
            label_judul
        )

        layout.addWidget(
            self.judul
        )

        # DESKRIPSI

        label_desc = QLabel(
            "Deskripsi Tugas"
        )

        label_desc.setObjectName(
            "labelField"
        )

        self.deskripsi = QTextEdit()

        self.deskripsi.setPlaceholderText(
            "Masukkan instruksi atau ketentuan tugas..."
        )

        self.deskripsi.setMinimumHeight(
            140
        )

        layout.addWidget(
            label_desc
        )

        layout.addWidget(
            self.deskripsi
        )

        # DEADLINE

        label_deadline = QLabel(
            "Deadline"
        )

        label_deadline.setObjectName(
            "labelField"
        )

        self.deadline = QDateEdit()

        self.deadline.setDate(
            QDate.currentDate()
        )

        self.deadline.setCalendarPopup(
            True
        )

        self.deadline.setMinimumHeight(
            40
        )

        layout.addWidget(
            label_deadline
        )

        layout.addWidget(
            self.deadline
        )

        layout.addStretch()

        # BUTTON

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
            "Simpan Tugas"
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