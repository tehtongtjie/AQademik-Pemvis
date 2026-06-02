from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QPushButton,
    QHBoxLayout
)


class DialogMataKuliah(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Tambah Mata Kuliah"
        )

        self.resize(500, 550)

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
            "Tambah Mata Kuliah"
        )

        title.setObjectName(
            "labelTitle"
        )

        subtitle = QLabel(
            "Lengkapi informasi mata kuliah yang akan dibuat."
        )

        subtitle.setObjectName(
            "labelSub"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # KODE

        kode_label = QLabel(
            "Kode Mata Kuliah"
        )

        kode_label.setObjectName(
            "labelField"
        )

        self.kode = QLineEdit()

        self.kode.setPlaceholderText(
            "Contoh: IF401"
        )

        layout.addWidget(kode_label)
        layout.addWidget(self.kode)

        # NAMA

        nama_label = QLabel(
            "Nama Mata Kuliah"
        )

        nama_label.setObjectName(
            "labelField"
        )

        self.nama = QLineEdit()

        self.nama.setPlaceholderText(
            "Contoh: Pemrograman Visual"
        )

        layout.addWidget(nama_label)
        layout.addWidget(self.nama)

        # SKS

        sks_label = QLabel(
            "Jumlah SKS"
        )

        sks_label.setObjectName(
            "labelField"
        )

        self.sks = QSpinBox()

        self.sks.setRange(1, 6)

        layout.addWidget(sks_label)
        layout.addWidget(self.sks)

        # DESKRIPSI

        deskripsi_label = QLabel(
            "Deskripsi Mata Kuliah"
        )

        deskripsi_label.setObjectName(
            "labelField"
        )

        self.deskripsi = QTextEdit()

        self.deskripsi.setPlaceholderText(
            "Masukkan deskripsi singkat mata kuliah..."
        )

        self.deskripsi.setMinimumHeight(
            120
        )

        layout.addWidget(deskripsi_label)
        layout.addWidget(self.deskripsi)

        # KODE JOIN

        join_label = QLabel(
            "Kode Join"
        )

        join_label.setObjectName(
            "labelField"
        )

        self.kode_join = QLineEdit()

        self.kode_join.setPlaceholderText(
            "Contoh: PEMVIS2026"
        )

        layout.addWidget(join_label)
        layout.addWidget(self.kode_join)

        layout.addSpacing(10)

        # BUTTONS

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
            "Simpan Mata Kuliah"
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