from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QGridLayout, QMessageBox, QDialog
)
from PySide6.QtCore import Qt
from ui.mahasiswa.widgets import CourseCard
from ui.mahasiswa.enrollment_dialog import EnrollmentDialog
from database.db_manager import (
    get_all_courses, get_user_enrolled_courses, enroll_user, 
    get_course_by_enroll_code, db_signals
)


class MatakuliahPage(QWidget):
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data or {}
        # Pastikan user_id diambil dengan benar
        self.user_id = user_data.get('id') if user_data else None
        print(f"[DEBUG] MatakuliahPage user_id: {self.user_id}")
        print(f"[DEBUG] MatakuliahPage user_data: {user_data}")
        
        self.show_all = False
        self.all_courses = []
        self.enrolled_course_ids = set()
        self.setup_ui()
        
        # Connect to database signals
        db_signals.data_changed.connect(self.refresh_data)
        
        self.load_courses()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        header = QHBoxLayout()
        title = QLabel("📚 Daftar Mata Kuliah")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        header.addWidget(title)
        header.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari mata kuliah...")
        self.search_input.setFixedWidth(280)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
                padding: 10px 16px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1.5px solid #3B82F6;
            }
        """)
        self.search_input.textChanged.connect(self.filter_courses)
        header.addWidget(self.search_input)
        
        layout.addLayout(header)
        
        # Filter toggle
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.show_all_btn = QPushButton("📚 Semua Mata Kuliah")
        self.show_all_btn.setCheckable(True)
        self.show_all_btn.setCursor(Qt.PointingHandCursor)
        self.show_all_btn.clicked.connect(lambda: self.set_filter(show_all=True))
        self.show_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #64748B;
                border-radius: 20px;
                padding: 6px 16px;
                font-weight: 500;
                border: none;
            }
        """)
        filter_layout.addWidget(self.show_all_btn)
        
        self.show_taking_btn = QPushButton("📖 Sedang Diambil")
        self.show_taking_btn.setCheckable(True)
        self.show_taking_btn.setChecked(True)
        self.show_taking_btn.setCursor(Qt.PointingHandCursor)
        self.show_taking_btn.clicked.connect(lambda: self.set_filter(show_all=False))
        self.show_taking_btn.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF;
                color: #3B82F6;
                border-radius: 20px;
                padding: 6px 16px;
                font-weight: 500;
                border: none;
            }
        """)
        filter_layout.addWidget(self.show_taking_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Grid daftar mata kuliah
        self.courses_scroll = QScrollArea()
        self.courses_scroll.setWidgetResizable(True)
        self.courses_scroll.setFrameShape(QFrame.NoFrame)
        self.courses_scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        self.courses_container = QWidget()
        self.courses_grid = QGridLayout(self.courses_container)
        self.courses_grid.setSpacing(15)
        self.courses_grid.setContentsMargins(0, 10, 0, 10)
        
        self.courses_scroll.setWidget(self.courses_container)
        layout.addWidget(self.courses_scroll)
    
    def refresh_data(self):
        self.load_courses()
    
    def set_filter(self, show_all):
        self.show_all = show_all
        
        if show_all:
            self.show_all_btn.setStyleSheet("background-color: #EFF6FF; color: #3B82F6; border-radius: 20px; padding: 6px 16px; border: none;")
            self.show_taking_btn.setStyleSheet("background-color: #F1F5F9; color: #64748B; border-radius: 20px; padding: 6px 16px; border: none;")
        else:
            self.show_all_btn.setStyleSheet("background-color: #F1F5F9; color: #64748B; border-radius: 20px; padding: 6px 16px; border: none;")
            self.show_taking_btn.setStyleSheet("background-color: #EFF6FF; color: #3B82F6; border-radius: 20px; padding: 6px 16px; border: none;")
        
        self.filter_courses()
    
    def load_courses(self):
        self.all_courses = get_all_courses()
        
        if self.user_id:
            enrolled_courses = get_user_enrolled_courses(self.user_id)
            self.enrolled_course_ids = {c['id'] for c in enrolled_courses}
            print(f"[DEBUG] Enrolled course IDs: {self.enrolled_course_ids}")
        else:
            self.enrolled_course_ids = set()
        
        self.filter_courses()
    
    def filter_courses(self):
        search_text = self.search_input.text().lower()
        filtered = []
        
        for course in self.all_courses:
            if not self.show_all and course['id'] not in self.enrolled_course_ids:
                continue
            if search_text and search_text not in course['nama'].lower() and search_text not in course['dosen'].lower():
                continue
            filtered.append(course)
        
        # Clear grid
        while self.courses_grid.count():
            child = self.courses_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Set grid properties agar card tidak melebar
        self.courses_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.courses_grid.setColumnStretch(0, 0)
        self.courses_grid.setColumnStretch(1, 0)
        
        # Hitung jumlah kolom (2 kolom maksimal)
        cols = 2
        for i, course in enumerate(filtered):
            row = i // cols
            col = i % cols
            is_enrolled = course['id'] in self.enrolled_course_ids
            card = CourseCard(
                course['nama'], course['sks'], 
                course['dosen'], is_enrolled, is_enrolled
            )
            card.setCursor(Qt.PointingHandCursor)
            card.setMinimumWidth(350)  # Lebar minimal card
            card.setMaximumWidth(450)  # Lebar maksimal card
            card.set_click_callback(lambda c=course: self.open_course_detail(c))
            self.courses_grid.addWidget(card, row, col, Qt.AlignTop | Qt.AlignLeft)
        
        # Tambahkan spacer untuk mengisi ruang kosong
        if len(filtered) % cols != 0:
            # Tambah widget kosong sebagai spacer
            empty = QWidget()
            empty.setFixedSize(0, 0)
            self.courses_grid.addWidget(empty, len(filtered) // cols, 1)
        
        if not filtered:
            empty_label = QLabel("✨ Tidak ada mata kuliah yang ditemukan ✨")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94A3B8; padding: 50px;")
            self.courses_grid.addWidget(empty_label, 0, 0, 1, 2, Qt.AlignCenter)
    
    def open_course_detail(self, course):
        is_enrolled = course['id'] in self.enrolled_course_ids
        
        print(f"[DEBUG] open_course_detail - course_id: {course['id']}, is_enrolled: {is_enrolled}")
        
        if is_enrolled:
            # Sudah terdaftar, langsung buka detail
            from ui.mahasiswa.detail_matakuliah_page import DetailMatakuliahPage
            parent = self.parent()
            while parent and not hasattr(parent, 'content_stack'):
                parent = parent.parent()
            if parent and hasattr(parent, 'content_stack'):
                self.detail_page = DetailMatakuliahPage(course, is_enrolled=True)
                parent.content_stack.addWidget(self.detail_page)
                parent.content_stack.setCurrentWidget(self.detail_page)
        else:
            # Belum terdaftar, tampilkan dialog enrollment
            dialog = EnrollmentDialog(course['nama'], course.get('enroll_code', ''), self)
            if dialog.exec() == QDialog.Accepted:
                print(f"[DEBUG] Enrollment accepted for course {course['id']}")
                # Enrollment berhasil, simpan ke database
                success, message = enroll_user(self.user_id, course['id'])
                print(f"[DEBUG] Enrollment result: success={success}, message={message}")
                if success:
                    QMessageBox.information(self, "Berhasil", f"Anda berhasil join mata kuliah {course['nama']}!")
                    # Update local data
                    self.enrolled_course_ids.add(course['id'])
                    # Refresh display
                    self.filter_courses()
                    # Emit signal untuk refresh halaman lain
                    db_signals.data_changed.emit()
                else:
                    QMessageBox.warning(self, "Gagal", message)