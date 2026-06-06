import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QTextEdit, QDialog,
    QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor
from database.db_manager import (
    get_course_materials, get_course_assignments, submit_assignment,
    download_material, get_user_submission, update_submission, delete_submission,
    db_signals
)


class DetailMatakuliahPage(QWidget):
    def __init__(self, course_data=None, is_enrolled=False, user_id=None, parent=None):
        super().__init__(parent)
        self.course_data = course_data or {}
        self.course_id = course_data.get('id') if course_data else None
        self.is_enrolled = is_enrolled
        self.user_id = user_id
        self.materials = []
        self.assignments = []
        self.submissions = {}
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        back_btn = QPushButton("← Kembali ke Daftar Mata Kuliah")
        back_btn.setObjectName("backBtn")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedHeight(40)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        
        # INFO CARD
        info_card = QFrame()
        info_card.setObjectName("infoCard")
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(15)
        info_layout.setContentsMargins(25, 20, 25, 20)
        
        self.course_name_label = QLabel("-")
        self.course_name_label.setObjectName("courseNameLabel")
        info_layout.addWidget(self.course_name_label)
        
        info_row = QHBoxLayout()
        info_row.setSpacing(15)
        
        self.sks_label = QLabel("- SKS")
        self.sks_label.setObjectName("sksBadge")
        info_row.addWidget(self.sks_label)
        
        self.lecturer_label = QLabel("👨‍🏫 -")
        self.lecturer_label.setObjectName("lecturerLabel")
        info_row.addWidget(self.lecturer_label)
        info_row.addStretch()
        info_layout.addLayout(info_row)
        
        line = QFrame()
        line.setObjectName("gradientLine")
        line.setFixedHeight(2)
        info_layout.addWidget(line)
        
        self.deskripsi_label = QLabel()
        self.deskripsi_label.setWordWrap(True)
        self.deskripsi_label.setObjectName("deskripsiText")
        info_layout.addWidget(self.deskripsi_label)
        
        content_layout.addWidget(info_card)
        
        # ENROLLED CONTAINER
        self.enrolled_container = QFrame()
        self.enrolled_container.setObjectName("enrolledContainer")
        enrolled_layout = QVBoxLayout(self.enrolled_container)
        enrolled_layout.setSpacing(20)
        enrolled_layout.setContentsMargins(0, 0, 0, 0)
        
        tab_container = QWidget()
        tab_container.setObjectName("tabContainer")
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        self.materi_btn = QPushButton("📚 Materi Kuliah")
        self.materi_btn.setObjectName("tabBtnLeft")
        self.materi_btn.setCheckable(True)
        self.materi_btn.setChecked(True)
        self.materi_btn.setCursor(Qt.PointingHandCursor)
        self.materi_btn.clicked.connect(lambda: self.switch_tab("materi"))
        
        self.tugas_btn = QPushButton("📋 Daftar Tugas")
        self.tugas_btn.setObjectName("tabBtnRight")
        self.tugas_btn.setCheckable(True)
        self.tugas_btn.setCursor(Qt.PointingHandCursor)
        self.tugas_btn.clicked.connect(lambda: self.switch_tab("tugas"))
        
        tab_layout.addWidget(self.materi_btn)
        tab_layout.addWidget(self.tugas_btn)
        tab_layout.addStretch()
        enrolled_layout.addWidget(tab_container)
        
        self.materi_card = QFrame()
        self.materi_card.setObjectName("contentCard")
        materi_layout_inner = QVBoxLayout(self.materi_card)
        materi_layout_inner.setSpacing(12)
        materi_layout_inner.setContentsMargins(20, 20, 20, 20)
        
        self.materi_list = QVBoxLayout()
        self.materi_list.setSpacing(10)
        materi_layout_inner.addLayout(self.materi_list)
        materi_layout_inner.addStretch()
        enrolled_layout.addWidget(self.materi_card)
        
        self.tugas_card = QFrame()
        self.tugas_card.setObjectName("contentCard")
        self.tugas_card.setVisible(False)
        tugas_layout_inner = QVBoxLayout(self.tugas_card)
        tugas_layout_inner.setSpacing(12)
        tugas_layout_inner.setContentsMargins(20, 20, 20, 20)
        
        self.tugas_list = QVBoxLayout()
        self.tugas_list.setSpacing(10)
        tugas_layout_inner.addLayout(self.tugas_list)
        tugas_layout_inner.addStretch()
        enrolled_layout.addWidget(self.tugas_card)
        
        content_layout.addWidget(self.enrolled_container)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def switch_tab(self, tab):
        if tab == "materi":
            self.materi_btn.setChecked(True)
            self.tugas_btn.setChecked(False)
            self.materi_card.setVisible(True)
            self.tugas_card.setVisible(False)
            self.materi_btn.setObjectName("tabBtnLeftActive")
            self.tugas_btn.setObjectName("tabBtnRight")
        else:
            self.materi_btn.setChecked(False)
            self.tugas_btn.setChecked(True)
            self.materi_card.setVisible(False)
            self.tugas_card.setVisible(True)
            self.materi_btn.setObjectName("tabBtnLeft")
            self.tugas_btn.setObjectName("tabBtnRightActive")
    
    def load_data(self):
        course = self.course_data
        self.course_name_label.setText(course.get('nama', 'Mata Kuliah'))
        self.sks_label.setText(f"{course.get('sks', 3)} SKS")
        
        dosen_id = course.get('dosen_id')
        if dosen_id and course.get('users') and course['users'].get('nama'):
            lecturer_name = course['users']['nama']
        else:
            lecturer_name = course.get('dosen', 'Dosen Pengampu')
        self.lecturer_label.setText(f"👨‍🏫 {lecturer_name}")
        
        deskripsi = course.get('deskripsi', 'Deskripsi mata kuliah belum tersedia.')
        self.deskripsi_label.setText(f"📖 {deskripsi}")
        
        if self.is_enrolled:
            self.enrolled_container.setVisible(True)
            self.load_materi()
            self.load_tugas()
        else:
            self.enrolled_container.setVisible(False)
            self.show_enrollment_required()
    
    def show_enrollment_required(self):
        enrollment_card = QFrame()
        enrollment_card.setObjectName("enrollmentCard")
        
        enrollment_layout = QVBoxLayout(enrollment_card)
        enrollment_layout.setAlignment(Qt.AlignCenter)
        enrollment_layout.setSpacing(15)
        enrollment_layout.setContentsMargins(30, 40, 30, 40)
        
        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setObjectName("enrollmentIcon")
        enrollment_layout.addWidget(icon_label)
        
        title_label = QLabel("Belum Terdaftar di Mata Kuliah Ini")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("enrollmentTitle")
        enrollment_layout.addWidget(title_label)
        
        message_label = QLabel(
            "Silakan kembali ke halaman daftar mata kuliah, klik card mata kuliah,\n"
            "dan masukkan kode enrollment untuk mengakses materi dan tugas."
        )
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setObjectName("enrollmentMessage")
        enrollment_layout.addWidget(message_label)
        
        if self.layout():
            self.layout().insertWidget(2, enrollment_card)
    
    def load_materi(self):
        success, materials = get_course_materials(self.course_id)
        
        if not success or not materials:
            empty_label = QLabel("📭 Belum ada materi untuk mata kuliah ini.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setObjectName("emptyLabel")
            self.materi_list.addWidget(empty_label)
            return
        
        self.materials = materials
        self._clear_layout(self.materi_list)
        
        for materi in materials:
            if isinstance(materi, dict):
                card = self._create_materi_card(materi)
                self.materi_list.addWidget(card)
    
    def _create_materi_card(self, materi):
        card = QFrame()
        card.setObjectName("materiItemCard")
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        
        icon = QLabel("📄")
        icon.setObjectName("materiIcon")
        layout.addWidget(icon)
        
        info_layout = QVBoxLayout()
        judul = QLabel(materi.get('judul', 'Materi'))
        judul.setObjectName("materiJudul")
        deskripsi = QLabel(materi.get('deskripsi', ''))
        deskripsi.setObjectName("materiDeskripsi")
        info_layout.addWidget(judul)
        info_layout.addWidget(deskripsi)
        layout.addLayout(info_layout, 1)
        
        materi_file_path = materi.get('file_path', '')
        materi_filename = materi.get('filename', 'material.pdf')
        
        download_btn = QPushButton("📥 Download")
        download_btn.setObjectName("downloadBtn")
        download_btn.setFixedWidth(100)
        download_btn.clicked.connect(lambda checked, fp=materi_file_path, fn=materi_filename: self.download_material(fp, fn))
        layout.addWidget(download_btn)
        
        return card
    
    def _check_is_late(self, deadline_date, submission_date):
        """Cek apakah pengumpulan terlambat"""
        try:
            # Parse deadline (format: YYYY-MM-DD HH:MM:SS atau YYYY-MM-DD)
            if ' ' in deadline_date:
                deadline = datetime.strptime(deadline_date, '%Y-%m-%d %H:%M:%S')
            else:
                deadline = datetime.strptime(deadline_date, '%Y-%m-%d')
                # Set deadline to end of day if only date provided
                deadline = deadline.replace(hour=23, minute=59, second=59)
            
            # Parse submission date
            if isinstance(submission_date, str):
                if 'T' in submission_date:
                    submission_date = submission_date.replace('T', ' ')
                if '.' in submission_date:
                    submission_date = submission_date.split('.')[0]
                if len(submission_date) > 19:
                    submission_date = submission_date[:19]
                submitted = datetime.strptime(submission_date, '%Y-%m-%d %H:%M:%S')
            else:
                submitted = submission_date
            
            return submitted > deadline, deadline, submitted
        except Exception as e:
            print(f"Error checking late: {e}")
            return False, None, None
    
    def _format_datetime(self, dt_str):
        """Format datetime string menjadi format yang lebih readable"""
        try:
            if isinstance(dt_str, str):
                if 'T' in dt_str:
                    dt_str = dt_str.replace('T', ' ')
                if '.' in dt_str:
                    dt_str = dt_str.split('.')[0]
                if len(dt_str) > 19:
                    dt_str = dt_str[:19]
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                return dt.strftime('%d %B %Y, %H:%M:%S')
            return str(dt_str)
        except:
            return dt_str
    
    def load_tugas(self):
        success, assignments = get_course_assignments(self.course_id)
        
        if not success or not assignments:
            empty_label = QLabel("📭 Belum ada tugas untuk mata kuliah ini.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setObjectName("emptyLabel")
            self.tugas_list.addWidget(empty_label)
            return
        
        self.assignments = assignments
        self._clear_layout(self.tugas_list)
        
        # Load submissions for all assignments
        for tugas in assignments:
            if isinstance(tugas, dict):
                tugas_id = tugas.get('id')
                success, submission = get_user_submission(tugas_id, self.user_id)
                if success and submission:
                    self.submissions[tugas_id] = submission
        
        for tugas in assignments:
            if isinstance(tugas, dict):
                card = self._create_tugas_card(tugas)
                self.tugas_list.addWidget(card)
    
    def _create_tugas_card(self, tugas):
        card = QFrame()
        card.setObjectName("tugasItemCard")
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 12, 15, 12)
        
        header_layout = QHBoxLayout()
        judul = QLabel(tugas.get('judul', 'Tugas'))
        judul.setObjectName("tugasJudul")
        header_layout.addWidget(judul)
        header_layout.addStretch()
        
        # Deadline dengan warna
        deadline_date = tugas.get('deadline_date', '-')
        deadline_label = QLabel(f"📅 Deadline: {deadline_date}")
        deadline_label.setObjectName("tugasDeadline")
        
        # Cek apakah deadline sudah lewat
        try:
            today = datetime.now().date()
            deadline_dt = datetime.strptime(deadline_date, '%Y-%m-%d').date()
            if deadline_dt < today:
                deadline_label.setStyleSheet("color: #EF4444; font-weight: bold;")
        except:
            pass
        
        header_layout.addWidget(deadline_label)
        layout.addLayout(header_layout)
        
        deskripsi = QLabel(tugas.get('deskripsi', ''))
        deskripsi.setWordWrap(True)
        deskripsi.setObjectName("tugasDeskripsi")
        layout.addWidget(deskripsi)
        
        tugas_id = tugas.get('id')
        submission = self.submissions.get(tugas_id)
        
        if submission:
            # Already submitted
            status_layout = QVBoxLayout()
            status_layout.setSpacing(5)
            
            # Status utama
            submitted_at = submission.get('submitted_at', '-')
            submitted_date = self._format_datetime(submitted_at)
            
            # Cek apakah terlambat
            is_late, deadline_dt, submitted_dt = self._check_is_late(deadline_date, submitted_at)
            
            if is_late:
                status_text = f"⚠️ TERLAMBAT! Dikumpulkan pada: {submitted_date}"
                status_label = QLabel(status_text)
                status_label.setObjectName("submittedStatus")
                status_label.setStyleSheet("color: #EF4444; font-weight: bold; background-color: #FEE2E2; padding: 6px; border-radius: 6px;")
            else:
                status_text = f"✅ Sudah dikumpulkan pada: {submitted_date}"
                status_label = QLabel(status_text)
                status_label.setObjectName("submittedStatus")
                status_label.setStyleSheet("color: #10B981; background-color: #D1FAE5; padding: 6px; border-radius: 6px;")
            
            status_layout.addWidget(status_label)
            
            # Tambahan info file
            file_name = submission.get('file_name', '-')
            file_label = QLabel(f"📎 File: {file_name}")
            file_label.setObjectName("fileInfo")
            file_label.setStyleSheet("color: #64748B; font-size: 11px;")
            status_layout.addWidget(file_label)
            
            # Action buttons row
            action_layout = QHBoxLayout()
            action_layout.addStretch()
            
            # Menu button for edit/delete
            menu_btn = QPushButton("⋮")
            menu_btn.setFixedSize(30, 30)
            menu_btn.setCursor(Qt.PointingHandCursor)
            menu_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #64748B;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                    border-radius: 6px;
                }
            """)
            
            menu = QMenu(menu_btn)
            edit_action = QAction("📝 Kumpul Ulang / Edit", self)
            edit_action.triggered.connect(lambda: self.edit_submission(tugas_id, tugas))
            menu.addAction(edit_action)
            
            delete_action = QAction("🗑️ Hapus Pengumpulan", self)
            delete_action.triggered.connect(lambda: self.delete_submission(tugas_id))
            menu.addAction(delete_action)
            
            menu_btn.setMenu(menu)
            action_layout.addWidget(menu_btn)
            
            status_layout.addLayout(action_layout)
            layout.addLayout(status_layout)
        else:
            # Belum dikumpulkan
            submit_layout = QVBoxLayout()
            submit_layout.setSpacing(5)
            
            # Cek apakah deadline sudah lewat (telat)
            try:
                today = datetime.now()
                deadline_dt = datetime.strptime(deadline_date, '%Y-%m-%d')
                if deadline_dt < today:
                    warning_label = QLabel("⚠️ PERINGATAN: Deadline sudah lewat! Silakan segera kumpulkan tugas.")
                    warning_label.setObjectName("warningLabel")
                    warning_label.setStyleSheet("color: #EF4444; font-weight: bold; background-color: #FEE2E2; padding: 6px; border-radius: 6px;")
                    submit_layout.addWidget(warning_label)
            except:
                pass
            
            submit_btn = QPushButton("📝 Kumpulkan Tugas")
            submit_btn.setObjectName("submitBtn")
            submit_btn.clicked.connect(lambda checked, tid=tugas_id, t=tugas: self.show_tugas_detail(tid, t))
            submit_layout.addWidget(submit_btn)
            
            layout.addLayout(submit_layout)
        
        return card
    
    def edit_submission(self, tugas_id, tugas):
        """Edit/re-upload submission"""
        self.show_tugas_detail(tugas_id, tugas, is_edit=True)
    
    def delete_submission(self, tugas_id):
        """Delete submission"""
        reply = QMessageBox.question(
            self, "Konfirmasi", 
            "Apakah Anda yakin ingin menghapus pengumpulan tugas ini?\n\n"
            "File yang sudah dikumpulkan akan dihapus dan Anda harus mengumpulkan ulang.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = delete_submission(tugas_id, self.user_id)
            if success:
                QMessageBox.information(self, "Berhasil", "Pengumpulan tugas berhasil dihapus!")
                if tugas_id in self.submissions:
                    del self.submissions[tugas_id]
                self.load_tugas()
                db_signals.data_changed.emit()
            else:
                QMessageBox.warning(self, "Gagal", f"Gagal menghapus pengumpulan: {message}")
    
    def show_tugas_detail(self, tugas_id, tugas, is_edit=False):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detail Tugas: {tugas.get('judul', 'Tugas')}")
        dialog.setModal(True)
        dialog.setMinimumWidth(550)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel(tugas.get('judul', 'Tugas'))
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        deadline_date = tugas.get('deadline_date', '-')
        deadline_time = tugas.get('deadline_time', '23:59')
        
        # Tampilkan deadline dengan warning jika lewat
        deadline_layout = QHBoxLayout()
        deadline_label = QLabel(f"📅 Tenggat: {deadline_date} {deadline_time} WIB")
        deadline_label.setObjectName("deadlineLabel")
        
        # Cek apakah deadline sudah lewat
        today = datetime.now()
        try:
            deadline_dt = datetime.strptime(f"{deadline_date} {deadline_time}", '%Y-%m-%d %H:%M:%S')
            if deadline_dt < today:
                deadline_label.setStyleSheet("color: #EF4444; font-weight: bold;")
                warning_icon = QLabel("⚠️")
                warning_icon.setStyleSheet("color: #EF4444; font-size: 14px;")
                deadline_layout.addWidget(warning_icon)
        except:
            pass
        
        deadline_layout.addWidget(deadline_label)
        deadline_layout.addStretch()
        layout.addLayout(deadline_layout)
        
        desc_label = QLabel("Deskripsi Tugas:")
        desc_label.setObjectName("sectionLabel")
        layout.addWidget(desc_label)
        
        deskripsi = QLabel(tugas.get('deskripsi', '-'))
        deskripsi.setWordWrap(True)
        deskripsi.setObjectName("deskripsiBox")
        layout.addWidget(deskripsi)
        
        # Show current file if editing
        current_submission = self.submissions.get(tugas_id)
        if current_submission and is_edit:
            submitted_at = self._format_datetime(current_submission.get('submitted_at', '-'))
            current_file_label = QLabel(f"📎 File saat ini: {current_submission.get('file_name', '-')}\n📅 Dikumpulkan: {submitted_at}")
            current_file_label.setObjectName("sectionLabel")
            current_file_label.setStyleSheet("color: #10B981; margin-top: 10px; padding: 8px; background-color: #F0FDF4; border-radius: 8px;")
            layout.addWidget(current_file_label)
        
        upload_frame = QFrame()
        upload_frame.setObjectName("uploadFrame")
        upload_layout = QHBoxLayout(upload_frame)
        
        self.selected_file_label = QLabel("Belum ada file dipilih" if not is_edit else "Pilih file baru untuk mengganti...")
        self.selected_file_label.setObjectName("selectedFileLabel")
        upload_layout.addWidget(self.selected_file_label, 1)
        
        upload_btn = QPushButton("📂 Pilih File")
        upload_btn.setObjectName("small_btn")
        upload_btn.clicked.connect(self.select_file)
        upload_layout.addWidget(upload_btn)
        layout.addWidget(upload_frame)
        
        catatan_label = QLabel("💬 Catatan (Opsional):")
        catatan_label.setObjectName("sectionLabel")
        layout.addWidget(catatan_label)
        
        self.catatan_input = QTextEdit()
        self.catatan_input.setPlaceholderText("Tulis catatan untuk dosen...")
        
        if current_submission and current_submission.get('catatan'):
            self.catatan_input.setText(current_submission.get('catatan'))
        
        self.catatan_input.setMaximumHeight(80)
        layout.addWidget(self.catatan_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(dialog.reject)
        
        submit_text = "Update Tugas" if is_edit else "Kumpulkan Tugas"
        submit_btn = QPushButton(f"📤 {submit_text}")
        submit_btn.setObjectName("primary_btn")
        submit_btn.clicked.connect(lambda: self.submit_tugas(dialog, tugas_id, is_edit))
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Tugas", "", "PDF Files (*.pdf);;All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            self.selected_file_label.setText(os.path.basename(file_path))
    
    def submit_tugas(self, dialog, tugas_id, is_edit=False):
        if not hasattr(self, 'selected_file') or not self.selected_file:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih file tugas terlebih dahulu!")
            return
        
        if is_edit:
            submission = self.submissions.get(tugas_id)
            if submission:
                success, message = update_submission(
                    submission['id'], self.user_id, self.selected_file, 
                    self.catatan_input.toPlainText()
                )
            else:
                success, message = False, "Submission tidak ditemukan"
        else:
            success, message = submit_assignment(
                tugas_id, self.user_id, self.selected_file, 
                self.catatan_input.toPlainText()
            )
        
        if success:
            QMessageBox.information(self, "Berhasil", f"Tugas berhasil {'diupdate' if is_edit else 'dikumpulkan'}!")
            dialog.accept()
            success, submission = get_user_submission(tugas_id, self.user_id)
            if success and submission:
                self.submissions[tugas_id] = submission
            self.load_tugas()
            db_signals.data_changed.emit()
        else:
            QMessageBox.warning(self, "Gagal", f"Gagal mengumpulkan tugas: {message}")
        
        if hasattr(self, 'selected_file'):
            delattr(self, 'selected_file')
    
    def download_material(self, file_path, filename):
        if not file_path:
            QMessageBox.warning(self, "Gagal", "File tidak ditemukan")
            return
        
        success, file_data = download_material(file_path)
        if success:
            save_path, _ = QFileDialog.getSaveFileName(self, "Simpan File", filename, "PDF Files (*.pdf)")
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(file_data)
                QMessageBox.information(self, "Berhasil", f"File berhasil disimpan ke:\n{save_path}")
        else:
            QMessageBox.warning(self, "Gagal", f"Gagal download materi: {file_data}")
    
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
                
                