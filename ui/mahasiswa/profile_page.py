from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ui.mahasiswa.dialogs import ProfileEditDialog, ChangePasswordDialog
from database.db_manager import (
    get_user_enrolled_courses, update_user_profile, 
    change_password, db_signals, get_user_schedule
)
import os


class ProfilePage(QWidget):
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.user_id = user_data.get('id') if user_data else None
        self.setup_ui()
        self.load_stylesheet()
        
        db_signals.data_changed.connect(self.refresh_data)
        self.load_profile()
    
    def load_stylesheet(self):
        style_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                print(f"[SUKSES] Profile QSS dimuat dari: {style_path}")
            except Exception as e:
                print(f"[ERROR] Gagal membaca QSS profile: {e}")
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        title = QLabel("👤 Profil Saya")
        title.setObjectName("profileTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.edit_btn = QPushButton("✏️ Edit Profil")
        self.edit_btn.setObjectName("secondary_btn")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.setFixedHeight(36)
        self.edit_btn.clicked.connect(self.edit_profile)
        header_layout.addWidget(self.edit_btn)
        
        self.password_btn = QPushButton("🔒 Ganti Password")
        self.password_btn.setObjectName("secondary_btn")
        self.password_btn.setCursor(Qt.PointingHandCursor)
        self.password_btn.setFixedHeight(36)
        self.password_btn.clicked.connect(self.change_password)
        header_layout.addWidget(self.password_btn)
        
        main_layout.addLayout(header_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Profile Card
        profile_card = QFrame()
        profile_card.setObjectName("profileCard")
        card_layout = QHBoxLayout(profile_card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(25)
        
        avatar_container = QFrame()
        avatar_container.setFixedSize(120, 120)
        avatar_container.setObjectName("avatarContainer")
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setAlignment(Qt.AlignCenter)
        
        self.avatar_label = QLabel("👩‍🎓")
        self.avatar_label.setObjectName("avatarLabel")
        avatar_layout.addWidget(self.avatar_label)
        card_layout.addWidget(avatar_container)
        
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(12)
        
        self.name_big = QLabel("-")
        self.name_big.setObjectName("nameBig")
        info_layout.addWidget(self.name_big)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        grid_layout.setColumnMinimumWidth(0, 100)
        
        nim_label = QLabel("NIM")
        nim_label.setObjectName("infoLabel")
        self.nim_value = QLabel("-")
        self.nim_value.setObjectName("infoValue")
        grid_layout.addWidget(nim_label, 0, 0)
        grid_layout.addWidget(self.nim_value, 0, 1)
        
        kelas_label = QLabel("Kelas")
        kelas_label.setObjectName("infoLabel")
        self.kelas_value = QLabel("-")
        self.kelas_value.setObjectName("infoValue")
        grid_layout.addWidget(kelas_label, 0, 2)
        grid_layout.addWidget(self.kelas_value, 0, 3)
        
        email_label = QLabel("Email")
        email_label.setObjectName("infoLabel")
        self.email_value = QLabel("-")
        self.email_value.setObjectName("infoValue")
        grid_layout.addWidget(email_label, 1, 0)
        grid_layout.addWidget(self.email_value, 1, 1)
        
        phone_label = QLabel("Telepon")
        phone_label.setObjectName("infoLabel")
        self.phone_value = QLabel("-")
        self.phone_value.setObjectName("infoValue")
        grid_layout.addWidget(phone_label, 1, 2)
        grid_layout.addWidget(self.phone_value, 1, 3)
        
        alamat_label = QLabel("Alamat")
        alamat_label.setObjectName("infoLabel")
        self.alamat_value = QLabel("-")
        self.alamat_value.setObjectName("infoValue")
        self.alamat_value.setWordWrap(True)
        grid_layout.addWidget(alamat_label, 2, 0)
        grid_layout.addWidget(self.alamat_value, 2, 1, 1, 3)
        
        info_layout.addLayout(grid_layout)
        card_layout.addWidget(info_widget, 1)
        content_layout.addWidget(profile_card)
        
        # Schedule Card
        schedule_card = QFrame()
        schedule_card.setObjectName("scheduleCard")
        schedule_layout = QVBoxLayout(schedule_card)
        schedule_layout.setContentsMargins(20, 20, 20, 20)
        schedule_layout.setSpacing(15)
        
        schedule_header = QHBoxLayout()
        schedule_title = QLabel("📅 Jadwal Kuliah Saya")
        schedule_title.setObjectName("cardTitle")
        schedule_header.addWidget(schedule_title)
        schedule_header.addStretch()
        schedule_layout.addLayout(schedule_header)
        
        self.schedule_table = QTableWidget()
        self.schedule_table.setObjectName("scheduleTable")
        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels(["Hari", "Mata Kuliah", "Jam", "Ruang"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.setMaximumHeight(250)
        schedule_layout.addWidget(self.schedule_table)
        
        content_layout.addWidget(schedule_card)
        
        # Courses Card
        courses_card = QFrame()
        courses_card.setObjectName("scheduleCard")
        courses_layout = QVBoxLayout(courses_card)
        courses_layout.setContentsMargins(20, 20, 20, 20)
        courses_layout.setSpacing(15)
        
        courses_header = QHBoxLayout()
        courses_title = QLabel("📚 Mata Kuliah yang Diambil")
        courses_title.setObjectName("cardTitle")
        courses_header.addWidget(courses_title)
        courses_header.addStretch()
        courses_layout.addLayout(courses_header)
        
        self.courses_grid = QGridLayout()
        self.courses_grid.setSpacing(10)
        courses_layout.addLayout(self.courses_grid)
        
        content_layout.addWidget(courses_card)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def refresh_data(self):
        self.load_profile()
        self.load_schedule()
        self.load_enrolled_courses()
    
    def load_profile(self):
        if not self.user_data:
            return
        
        name = self.user_data.get('nama', 'Mahasiswa')
        nim = self.user_data.get('nim_nip', '-')
        email = self.user_data.get('email', '-')
        phone = self.user_data.get('phone', '-')
        address = self.user_data.get('address', '-')
        
        self.name_big.setText(name)
        self.nim_value.setText(nim)
        self.kelas_value.setText("Pemrograman Visual D")
        self.email_value.setText(email)
        self.phone_value.setText(phone if phone else "-")
        self.alamat_value.setText(address if address else "-")
        self.avatar_label.setText("👩‍🎓")
        
        self.load_schedule()
        self.load_enrolled_courses()
    
    def load_schedule(self):
        if not self.user_id:
            return
            
        success, schedules = get_user_schedule(self.user_id)
        
        if not success or not schedules:
            self.schedule_table.setRowCount(1)
            self.schedule_table.setSpan(0, 0, 1, 4)
            no_item = QTableWidgetItem("✨ Belum ada jadwal untuk mata kuliah yang diambil ✨")
            no_item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(0, 0, no_item)
            return
        
        self.schedule_table.setRowCount(len(schedules))
        
        day_colors = {
            "Senin": "#EFF6FF", "Selasa": "#F0FDF4",
            "Rabu": "#FEF3C7", "Kamis": "#FCE7F3", "Jumat": "#E0E7FF"
        }
        
        for row, schedule in enumerate(schedules):
            hari_item = QTableWidgetItem(schedule.get('day_of_week', '-'))
            matkul_item = QTableWidgetItem(schedule.get('course_name', '-'))
            jam_item = QTableWidgetItem(f"{schedule.get('start_time', '-')} - {schedule.get('end_time', '-')}")
            ruang_item = QTableWidgetItem(schedule.get('room', '-'))
            
            if schedule.get('day_of_week') in day_colors:
                hari_item.setBackground(QColor(day_colors[schedule.get('day_of_week')]))
            
            self.schedule_table.setItem(row, 0, hari_item)
            self.schedule_table.setItem(row, 1, matkul_item)
            self.schedule_table.setItem(row, 2, jam_item)
            self.schedule_table.setItem(row, 3, ruang_item)
        
        self.schedule_table.resizeRowsToContents()
    
    def load_enrolled_courses(self):
        if not self.user_id:
            return
            
        success, enrolled = get_user_enrolled_courses(self.user_id)
        
        while self.courses_grid.count():
            child = self.courses_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not success or not enrolled:
            empty_label = QLabel("✨ Belum ada mata kuliah yang diambil ✨")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94A3B8; padding: 20px;")
            self.courses_grid.addWidget(empty_label, 0, 0)
            return
        
        for i, course in enumerate(enrolled):
            row = i // 2
            col = i % 2
            card = self._create_course_card(course)
            self.courses_grid.addWidget(card, row, col)
    
    def _create_course_card(self, course):
        card = QFrame()
        card.setObjectName("courseCardSmall")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)
        
        course_data = course.get('courses', {}) if 'courses' in course else course
        name_label = QLabel(course_data.get('nama', '-'))
        name_label.setObjectName("courseNameSmall")
        layout.addWidget(name_label)
        
        lecturer_label = QLabel(f"👨‍🏫 {course_data.get('dosen', 'Dosen')}")
        lecturer_label.setObjectName("courseTimeSmall")
        layout.addWidget(lecturer_label)
        
        sks_label = QLabel(f"📚 {course_data.get('sks', 3)} SKS")
        sks_label.setObjectName("courseRoomSmall")
        layout.addWidget(sks_label)
        
        return card
    
    def edit_profile(self):
        profile_data = {
            'name': self.name_big.text(),
            'nim': self.nim_value.text(),
            'email': self.email_value.text(),
            'phone': self.phone_value.text(),
            'address': self.alamat_value.text(),
            'user_id': self.user_id
        }
        dialog = ProfileEditDialog(self, profile_data)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            success, message = update_user_profile(
                self.user_id, data['name'], data['email'], data['phone'], data['address']
            )
            
            if success:
                self.name_big.setText(data['name'])
                self.email_value.setText(data['email'])
                self.phone_value.setText(data['phone'])
                self.alamat_value.setText(data['address'])
                
                self.user_data['nama'] = data['name']
                self.user_data['email'] = data['email']
                self.user_data['phone'] = data['phone']
                self.user_data['address'] = data['address']
                
                QMessageBox.information(self, "Berhasil", "Profil berhasil diupdate!")
            else:
                QMessageBox.warning(self, "Error", f"Gagal update profil: {message}")
    
    def change_password(self):
        dialog = ChangePasswordDialog(self)
        dialog.user_id = self.user_id
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "Info", "Password berhasil diganti!\nSilakan login kembali.")