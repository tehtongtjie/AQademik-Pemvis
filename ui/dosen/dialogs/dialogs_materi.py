from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFileDialog
)

import os


class DialogMateri(QDialog):

    def __init__(self):
        super().__init__()

        self.file_path = ""

        self.setWindowTitle(
            "Upload Materi"
        )

        self.resize(500, 450)

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
            "Upload Materi"
        )

        title.setObjectName(
            "labelTitle"
        )

        subtitle = QLabel(
            "Upload file PDF materi untuk mahasiswa."
        )

        subtitle.setObjectName(
            "labelSub"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # JUDUL

        label_judul = QLabel(
            "Judul Materi"
        )

        label_judul.setObjectName(
            "labelField"
        )

        self.judul = QLineEdit()

        self.judul.setPlaceholderText(
            "Contoh: Pertemuan 1 - Pengantar"
        )

        layout.addWidget(label_judul)
        layout.addWidget(self.judul)

        # DESKRIPSI

        label_desc = QLabel(
            "Deskripsi"
        )

        label_desc.setObjectName(
            "labelField"
        )

        self.deskripsi = QTextEdit()

        self.deskripsi.setPlaceholderText(
            "Masukkan deskripsi materi..."
        )

        self.deskripsi.setMinimumHeight(
            120
        )

        layout.addWidget(label_desc)
        layout.addWidget(self.deskripsi)

        # FILE PDF

        label_file = QLabel(
            "File PDF"
        )

        label_file.setObjectName(
            "labelField"
        )

        layout.addWidget(label_file)

        self.lbl_file = QLabel(
            "Belum ada file dipilih"
        )

        self.lbl_file.setObjectName(
            "labelSub"
        )

        layout.addWidget(
            self.lbl_file
        )

        self.btn_file = QPushButton(
            "Pilih PDF"
        )

        self.btn_file.setObjectName(
            "btnSecondary"
        )

        self.btn_file.clicked.connect(
            self.pilih_file
        )

        layout.addWidget(
            self.btn_file
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
            "Upload Materi"
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

    def pilih_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih Materi",
            "",
            "Dokumen (*.pdf *.ppt *.pptx *.doc *.docx)"
        )

        if file_path:

            self.file_path = file_path

            self.lbl_file.setText(
                os.path.basename(file_path)
            )

            self.btn_file.setText(
                "Ganti Materi"
            )