from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QTextEdit
)
from PySide6.QtCore import Qt


class DetailMatakuliahPage(QWidget):
    def __init__(self, course_data=None, is_enrolled=False, parent=None):
        super().__init__(parent)
        self.course_data = course_data or {}
        self.is_enrolled = is_enrolled
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        # Back button
        back_btn = QPushButton("← Kembali ke Daftar Mata Kuliah")
        back_btn.setObjectName("secondary_btn")
        back_btn.setFixedHeight(35)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Header mata kuliah
        self.header_card = QFrame()
        self.header_card.setObjectName("courseDetailCard")
        self.header_card.setStyleSheet("""
            QFrame#courseDetailCard {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #E2E8F0;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(self.header_card)
        
        self.course_name_label = QLabel("-")
        self.course_name_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        header_layout.addWidget(self.course_name_label)
        
        info_layout = QHBoxLayout()
        self.sks_label = QLabel("- SKS")
        self.sks_label.setStyleSheet("color: #3B82F6; background-color: #EFF6FF; padding: 4px 12px; border-radius: 20px;")
        info_layout.addWidget(self.sks_label)
        
        self.lecturer_label = QLabel("👨‍🏫 -")
        self.lecturer_label.setStyleSheet("color: #64748B;")
        info_layout.addWidget(self.lecturer_label)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        # Deskripsi singkat mata kuliah (bisa diakses tanpa enrollment)
        self.deskripsi_label = QLabel()
        self.deskripsi_label.setWordWrap(True)
        self.deskripsi_label.setStyleSheet("color: #64748B; padding: 10px 0;")
        header_layout.addWidget(self.deskripsi_label)
        
        content_layout.addWidget(self.header_card)
        
        # Bagian untuk yang sudah terdaftar
        self.enrolled_content = QWidget()
        enrolled_layout = QVBoxLayout(self.enrolled_content)
        
        # Tab section (Materi & Tugas)
        tab_layout = QHBoxLayout()
        
        self.materi_btn = QPushButton("📚 Materi Kuliah")
        self.materi_btn.setCheckable(True)
        self.materi_btn.setChecked(True)
        self.materi_btn.setCursor(Qt.PointingHandCursor)
        self.materi_btn.clicked.connect(lambda: self.switch_tab("materi"))
        
        self.tugas_btn = QPushButton("📋 Daftar Tugas")
        self.tugas_btn.setCheckable(True)
        self.tugas_btn.setCursor(Qt.PointingHandCursor)
        self.tugas_btn.clicked.connect(lambda: self.switch_tab("tugas"))
        
        tab_layout.addWidget(self.materi_btn)
        tab_layout.addWidget(self.tugas_btn)
        tab_layout.addStretch()
        
        enrolled_layout.addLayout(tab_layout)
        
        # Materi content
        self.materi_content = QWidget()
        materi_layout = QVBoxLayout(self.materi_content)
        self.materi_list = QVBoxLayout()
        self.materi_list.setSpacing(10)
        materi_layout.addLayout(self.materi_list)
        materi_layout.addStretch()
        
        # Tugas content
        self.tugas_content = QWidget()
        self.tugas_content.setVisible(False)
        tugas_layout = QVBoxLayout(self.tugas_content)
        self.tugas_list = QVBoxLayout()
        self.tugas_list.setSpacing(10)
        tugas_layout.addLayout(self.tugas_list)
        tugas_layout.addStretch()
        
        enrolled_layout.addWidget(self.materi_content)
        enrolled_layout.addWidget(self.tugas_content)
        
        content_layout.addWidget(self.enrolled_content)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def switch_tab(self, tab):
        if tab == "materi":
            self.materi_btn.setChecked(True)
            self.tugas_btn.setChecked(False)
            self.materi_content.setVisible(True)
            self.tugas_content.setVisible(False)
            
            self.materi_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
            """)
            self.tugas_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    color: #64748B;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: 500;
                }
            """)
        else:
            self.materi_btn.setChecked(False)
            self.tugas_btn.setChecked(True)
            self.materi_content.setVisible(False)
            self.tugas_content.setVisible(True)
            
            self.tugas_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
            """)
            self.materi_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    color: #64748B;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: 500;
                }
            """)
    
    def load_data(self):
        course = self.course_data
        self.course_name_label.setText(course.get('nama', 'Mata Kuliah'))
        self.sks_label.setText(f"{course.get('sks', 3)} SKS")
        self.lecturer_label.setText(f"👨‍🏫 {course.get('dosen', 'Dosen Pengampu')}")
        
        # Deskripsi mata kuliah (bisa diakses tanpa enrollment)
        deskripsi_text = f"""
        📖 Deskripsi Mata Kuliah:
        
        Mata kuliah {course.get('nama', 'ini')} membahas tentang konsep fundamental dan implementasi praktis 
        dalam bidang terkait. Mahasiswa akan mempelajari teori dan praktik secara komprehensif.
        
        Capaian Pembelajaran:
        • Memahami konsep dasar {course.get('nama', 'mata kuliah')}
        • Mampu mengimplementasikan solusi menggunakan teknologi terkini
        • Mengembangkan proyek akhir sebagai portofolio
        """
        self.deskripsi_label.setText(deskripsi_text)
        
        if self.is_enrolled:
            self.load_materi()
            self.load_tugas()
        else:
            # Tampilkan pesan bahwa perlu enrollment
            self.show_enrollment_required()
    
    def show_enrollment_required(self):
        # Sembunyikan content yang memerlukan enrollment
        self.enrolled_content.setVisible(False)
        
        # Tampilkan pesan enrollment
        enrollment_frame = QFrame()
        enrollment_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border-radius: 16px;
                border: 1px solid #FDE68A;
                padding: 30px;
            }
        """)
        
        enrollment_layout = QVBoxLayout(enrollment_frame)
        enrollment_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        enrollment_layout.addWidget(icon_label)
        
        title_label = QLabel("Belum Terdaftar di Mata Kuliah Ini")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #92400E;")
        enrollment_layout.addWidget(title_label)
        
        message_label = QLabel(
            "Anda belum terdaftar di mata kuliah ini.\n\n"
            "Silakan kembali ke halaman daftar mata kuliah, klik card mata kuliah, "
            "dan masukkan kode enrollment yang benar untuk mengakses materi dan tugas."
        )
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #92400E;")
        enrollment_layout.addWidget(message_label)
        
        # Cari parent scroll area untuk menambahkan pesan enrollment
        parent_widget = self.findChild(QScrollArea)
        if parent_widget:
            # Cari widget container di dalam scroll area
            scroll = self.findChild(QScrollArea)
            if scroll:
                container = scroll.widget()
                if container:
                    container.layout().addWidget(enrollment_frame)
    
    def load_materi(self):
        materi_list = [
            {"judul": "Bab 1: Pengantar", "file": "bab1.pdf", "deskripsi": "Materi pengantar mata kuliah"},
            {"judul": "Bab 2: Konsep Dasar", "file": "bab2.pdf", "deskripsi": "Konsep dasar yang perlu dipahami"},
            {"judul": "Bab 3: Implementasi", "file": "bab3.pdf", "deskripsi": "Implementasi praktis"},
            {"judul": "Slide Presentasi", "file": "slides.pptx", "deskripsi": "Slide presentasi perkuliahan"},
        ]
        
        self._clear_layout(self.materi_list)
        
        for materi in materi_list:
            card = self._create_materi_card(materi)
            self.materi_list.addWidget(card)
    
    def _create_materi_card(self, materi):
        card = QFrame()
        card.setObjectName("materiCard")
        card.setStyleSheet("""
            QFrame#materiCard {
                background-color: #F8FAFC;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                padding: 15px;
            }
            QFrame#materiCard:hover {
                background-color: #F1F5F9;
            }
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        
        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon)
        
        info_layout = QVBoxLayout()
        judul = QLabel(materi['judul'])
        judul.setStyleSheet("font-weight: bold; color: #1E293B;")
        deskripsi = QLabel(materi['deskripsi'])
        deskripsi.setStyleSheet("font-size: 11px; color: #64748B;")
        info_layout.addWidget(judul)
        info_layout.addWidget(deskripsi)
        layout.addLayout(info_layout, 1)
        
        download_btn = QPushButton("📥 Download")
        download_btn.setObjectName("small_btn")
        download_btn.setFixedWidth(100)
        download_btn.setCursor(Qt.PointingHandCursor)
        download_btn.clicked.connect(lambda: self.download_file(materi['file']))
        layout.addWidget(download_btn)
        
        return card
    
    def load_tugas(self):
        tugas_list = [
            {"judul": "Tugas 1", "deadline": "2025-06-10", "status": "Belum Dikumpul", "deskripsi": "Kerjakan soal latihan bab 1-3"},
            {"judul": "Tugas 2", "deadline": "2025-06-20", "status": "Belum Dikumpul", "deskripsi": "Buat proyek sederhana"},
            {"judul": "UTS", "deadline": "2025-06-25", "status": "Belum Dikumpul", "deskripsi": "Ujian Tengah Semester"},
        ]
        
        self._clear_layout(self.tugas_list)
        
        for tugas in tugas_list:
            card = self._create_tugas_card(tugas)
            self.tugas_list.addWidget(card)
    
    def _create_tugas_card(self, tugas):
        card = QFrame()
        card.setObjectName("tugasDetailCard")
        card.setStyleSheet("""
            QFrame#tugasDetailCard {
                background-color: #F8FAFC;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        judul = QLabel(tugas['judul'])
        judul.setStyleSheet("font-weight: bold; font-size: 14px; color: #1E293B;")
        header_layout.addWidget(judul)
        header_layout.addStretch()
        
        deadline = QLabel(f"📅 Deadline: {tugas['deadline']}")
        deadline.setStyleSheet("font-size: 11px; color: #EF4444;")
        header_layout.addWidget(deadline)
        
        layout.addLayout(header_layout)
        
        deskripsi = QLabel(tugas['deskripsi'])
        deskripsi.setStyleSheet("font-size: 12px; color: #64748B;")
        deskripsi.setWordWrap(True)
        layout.addWidget(deskripsi)
        
        detail_btn = QPushButton("📝 Lihat Detail & Kumpul")
        detail_btn.setObjectName("secondary_btn")
        detail_btn.setCursor(Qt.PointingHandCursor)
        detail_btn.clicked.connect(lambda: self.show_tugas_detail(tugas))
        layout.addWidget(detail_btn)
        
        return card
    
    def show_tugas_detail(self, tugas):
        from PySide6.QtWidgets import QDialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detail Tugas: {tugas['judul']}")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel(tugas['judul'])
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title)
        
        deadline = QLabel(f"📅 Tenggat Pengumpulan: {tugas['deadline']} 23:59 WIB")
        deadline.setStyleSheet("color: #EF4444; padding: 5px 0;")
        layout.addWidget(deadline)
        
        desc_label = QLabel("Deskripsi Tugas:")
        desc_label.setStyleSheet("font-weight: bold; color: #1E293B; margin-top: 10px;")
        layout.addWidget(desc_label)
        
        deskripsi = QLabel(tugas['deskripsi'])
        deskripsi.setWordWrap(True)
        deskripsi.setStyleSheet("color: #64748B; padding: 10px; background-color: #F8FAFC; border-radius: 8px;")
        layout.addWidget(deskripsi)
        
        lampiran_label = QLabel("📎 Lampiran / File Tugas:")
        lampiran_label.setStyleSheet("font-weight: bold; color: #1E293B; margin-top: 10px;")
        layout.addWidget(lampiran_label)
        
        upload_frame = QFrame()
        upload_frame.setStyleSheet("background-color: #F8FAFC; border-radius: 8px; border: 1px dashed #CBD5E1; padding: 10px;")
        upload_layout = QHBoxLayout(upload_frame)
        
        self.selected_file_label = QLabel("Belum ada file dipilih")
        self.selected_file_label.setStyleSheet("color: #64748B;")
        upload_layout.addWidget(self.selected_file_label, 1)
        
        upload_btn = QPushButton("📂 Pilih File")
        upload_btn.setObjectName("small_btn")
        upload_btn.clicked.connect(lambda: self.select_file())
        upload_layout.addWidget(upload_btn)
        
        layout.addWidget(upload_frame)
        
        catatan_label = QLabel("💬 Catatan (Opsional):")
        catatan_label.setStyleSheet("font-weight: bold; color: #1E293B; margin-top: 10px;")
        layout.addWidget(catatan_label)
        
        self.catatan_input = QTextEdit()
        self.catatan_input.setPlaceholderText("Tulis catatan untuk dosen...")
        self.catatan_input.setMaximumHeight(80)
        layout.addWidget(self.catatan_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(dialog.reject)
        
        submit_btn = QPushButton("📤 Kumpulkan Tugas")
        submit_btn.setObjectName("primary_btn")
        submit_btn.clicked.connect(lambda: self.submit_tugas(dialog, tugas))
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Tugas", "", 
            "PDF Files (*.pdf);;Word Files (*.docx);;Zip Files (*.zip);;All Files (*.*)"
        )
        if file_path:
            import os
            self.selected_file = file_path
            self.selected_file_label.setText(os.path.basename(file_path))
    
    def submit_tugas(self, dialog, tugas):
        if not hasattr(self, 'selected_file') or not self.selected_file:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih file tugas terlebih dahulu!")
            return
        
        QMessageBox.information(
            self, "Berhasil", 
            f"Tugas '{tugas['judul']}' berhasil dikumpulkan!\n"
            f"File: {self.selected_file.split('/')[-1]}\n"
            f"Catatan: {self.catatan_input.toPlainText()[:50]}..."
        )
        dialog.accept()
    
    def download_file(self, filename):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan File", filename, "All Files (*.*)"
        )
        if save_path:
            QMessageBox.information(self, "Berhasil", f"File berhasil disimpan ke:\n{save_path}")
    
    def go_back(self):
        if self.parent():
            parent = self.parent()
            while parent and not hasattr(parent, 'switch_page'):
                parent = parent.parent()
            if parent and hasattr(parent, 'switch_page'):
                parent.switch_page(2)
    
    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()