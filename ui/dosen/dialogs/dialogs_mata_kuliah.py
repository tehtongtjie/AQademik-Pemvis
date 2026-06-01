from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QPushButton
)


class DialogMataKuliah(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Tambah Mata Kuliah"
        )

        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # KODE

        layout.addWidget(
            QLabel("Kode Mata Kuliah")
        )

        self.kode = QLineEdit()
        layout.addWidget(self.kode)

        # NAMA

        layout.addWidget(
            QLabel("Nama Mata Kuliah")
        )

        self.nama = QLineEdit()
        layout.addWidget(self.nama)

        # SKS

        layout.addWidget(
            QLabel("SKS")
        )

        self.sks = QSpinBox()
        self.sks.setRange(1, 6)

        layout.addWidget(self.sks)


        # DESKRIPSI

        layout.addWidget(
            QLabel("Deskripsi")
        )

        self.deskripsi = QTextEdit()

        layout.addWidget(
            self.deskripsi
        )

        # KODE JOIN

        layout.addWidget(
            QLabel("Kode Join")
        )

        self.kode_join = QLineEdit()

        layout.addWidget(
            self.kode_join
        )

        # BUTTON

        self.btn_simpan = QPushButton(
            "Simpan"
        )

        layout.addWidget(
            self.btn_simpan
        )
        self.btn_simpan.clicked.connect(
            self.accept
        )