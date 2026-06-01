from PySide6.QtWidgets import (
QWidget,
QVBoxLayout,
QHBoxLayout,
QLabel,
QPushButton,
QLineEdit,
QScrollArea,
QFrame,
QMessageBox
)

from database.db_manager import (
add_course,
get_courses
)

from ui.dosen.dialogs.dialogs_mata_kuliah import (
DialogMataKuliah
)

from ui.dosen.logic.validasi_mata_kuliah import (
validasi_mata_kuliah
)

from ui.dosen.detail_mata_kuliah import (
DetailMataKuliah
)

class MataKuliah(QWidget):

    def __init__(self):
        super().__init__()

        self.build_ui()
        self.load_data()

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        main_layout.setSpacing(20)

        # =========================
        # HEADER
        # =========================

        title = QLabel(
            "Kelola Mata Kuliah"
        )

        title.setObjectName(
            "labelTitle"
        )

        subtitle = QLabel(
            "Pilih mata kuliah untuk mengelola materi dan tugas."
        )

        subtitle.setObjectName(
            "labelSub"
        )

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # =========================
        # TOOLBAR
        # =========================

        toolbar = QHBoxLayout()

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Cari mata kuliah..."
        )

        self.btn_tambah = QPushButton(
            "+ Tambah Mata Kuliah"
        )

        self.btn_tambah.setObjectName(
            "btnPrimary"
        )

        self.btn_tambah.clicked.connect(
            self.tambah_mata_kuliah
        )

        toolbar.addWidget(
            self.search
        )

        toolbar.addWidget(
            self.btn_tambah
        )

        main_layout.addLayout(
            toolbar
        )

        # =========================
        # LIST MATA KULIAH
        # =========================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.container = QWidget()

        self.card_layout = QVBoxLayout(
            self.container
        )

        self.card_layout.setSpacing(
            15
        )

        self.scroll.setWidget(
            self.container
        )

        main_layout.addWidget(
            self.scroll
        )

    def load_data(self):

        success, courses = get_courses()

        if not success:
            return

        while self.card_layout.count():

            item = self.card_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        for course in courses:

            card = self.create_course_card(
                course
            )

            self.card_layout.addWidget(
                card
            )

        self.card_layout.addStretch()

    def create_course_card(
        self,
        course
    ):

        card = QFrame()

        card.setObjectName(
            "dashboardCard"
        )

        layout = QVBoxLayout(
            card
        )

        nama = QLabel(
            course["nama"]
        )

        nama.setObjectName(
            "labelTitle"
        )

        info = QLabel(
            f"Kode: {course['kode']} | "
            f"SKS: {course['sks']}"
        )

        tombol_layout = QHBoxLayout()

        btn_buka = QPushButton(
            "Kelola Mata Kuliah"
        )

        btn_buka.setObjectName(
            "btnPrimary"
        )

        btn_buka.clicked.connect(
            lambda _, c=course:
            self.buka_mata_kuliah(c)
        )

        tombol_layout.addStretch()
        tombol_layout.addWidget(
            btn_buka
        )

        layout.addWidget(
            nama
        )

        layout.addWidget(
            info
        )

        layout.addLayout(
            tombol_layout
        )

        return card

    def buka_mata_kuliah(
        self,
        course
    ):

        dashboard = self.window()

        if hasattr(
            dashboard,
            "buka_detail_matkul"
        ):

            dashboard.buka_detail_matkul(
                course
            )

    def tambah_mata_kuliah(self):

        dialog = DialogMataKuliah()

        if not dialog.exec():
            return

        valid, pesan = validasi_mata_kuliah(
            dialog.kode.text(),
            dialog.nama.text(),
            dialog.sks.value(),
            dialog.dosen.text(),
            dialog.kode_join.text()
        )

        if not valid:

            QMessageBox.warning(
                self,
                "Validasi",
                pesan
            )

            return

        sukses, pesan = add_course(
            dialog.kode.text(),
            dialog.nama.text(),
            dialog.sks.value(),
            dialog.dosen.text(),
            dialog.deskripsi.toPlainText(),
            dialog.kode_join.text()
        )

        if sukses:

            QMessageBox.information(
                self,
                "Sukses",
                pesan
            )

            self.load_data()

        else:

            QMessageBox.warning(
                self,
                "Gagal",
                pesan
            )