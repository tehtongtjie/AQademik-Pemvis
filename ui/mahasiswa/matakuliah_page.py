from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QGridLayout, QMessageBox, QDialog
)
from PySide6.QtCore import Qt
from ui.mahasiswa.widgets import CourseCard
from ui.mahasiswa.enrollment_dialog import EnrollmentDialog
from database.db_manager import get_courses, get_enrolled_courses, enroll_course, db_signals


class MatakuliahPage(QWidget):
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.user_id = user_data.get('id') if user_data else None
        self.show_all = False
        self.all_courses = []
        self.enrolled_course_ids = set()
        self.setup_ui()
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
        self.search_input.textChanged.connect(self.filter_courses)
        header.addWidget(self.search_input)
        layout.addLayout(header)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.show_all_btn = QPushButton("📚 Semua Mata Kuliah")
        self.show_all_btn.setCheckable(True)
        self.show_all_btn.setCursor(Qt.PointingHandCursor)
        self.show_all_btn.clicked.connect(lambda: self.set_filter(show_all=True))
        filter_layout.addWidget(self.show_all_btn)
        
        self.show_taking_btn = QPushButton("📖 Sedang Diambil")
        self.show_taking_btn.setCheckable(True)
        self.show_taking_btn.setChecked(True)
        self.show_taking_btn.setCursor(Qt.PointingHandCursor)
        self.show_taking_btn.clicked.connect(lambda: self.set_filter(show_all=False))
        filter_layout.addWidget(self.show_taking_btn)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        self.courses_scroll = QScrollArea()
        self.courses_scroll.setWidgetResizable(True)
        self.courses_scroll.setFrameShape(QFrame.NoFrame)
        
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
        # Get all courses from database
        success, courses = get_courses()
        if success:
            self.all_courses = courses
        else:
            self.all_courses = []
            print(f"[ERROR] Gagal ambil courses: {courses}")
        
        # Get user's enrolled courses
        if self.user_id:
            success, enrolled = get_enrolled_courses(self.user_id)
            if success and enrolled:
                # enrolled adalah list dengan item yang punya key 'courses'
                self.enrolled_course_ids = {item['courses']['id'] for item in enrolled if item.get('courses')}
            else:
                self.enrolled_course_ids = set()
            print(f"[DEBUG] Enrolled course IDs: {self.enrolled_course_ids}")
        else:
            self.enrolled_course_ids = set()
        
        self.filter_courses()
    
    def filter_courses(self):
        search_text = self.search_input.text().lower()
        filtered = []
        
        for course in self.all_courses:
            course_id = course.get('id', 0)
            course_nama = course.get('nama', '')
            course_dosen = course.get('dosen', '')
            
            if not self.show_all and course_id not in self.enrolled_course_ids:
                continue
            if search_text and search_text not in course_nama.lower() and search_text not in course_dosen.lower():
                continue
            filtered.append(course)
        
        # Clear grid
        while self.courses_grid.count():
            child = self.courses_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.courses_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        for i, course in enumerate(filtered):
            course_id = course.get('id', 0)
            course_nama = course.get('nama', '')
            course_sks = course.get('sks', 3)
            course_dosen = course.get('dosen', '')
            
            is_enrolled = course_id in self.enrolled_course_ids
            
            card = CourseCard(
                course_nama, course_sks, 
                course_dosen, is_enrolled, is_enrolled
            )
            card.setMinimumWidth(350)
            card.setMaximumWidth(450)
            card.setCursor(Qt.PointingHandCursor)
            card.set_click_callback(lambda c=course: self.open_course_detail(c))
            self.courses_grid.addWidget(card, i, 0, Qt.AlignTop | Qt.AlignLeft)
        
        if not filtered:
            empty_label = QLabel("✨ Tidak ada mata kuliah yang ditemukan ✨")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94A3B8; padding: 50px;")
            self.courses_grid.addWidget(empty_label, 0, 0, 1, 1, Qt.AlignCenter)
    
    def open_course_detail(self, course):
        course_id = course.get('id', 0)
        is_enrolled = course_id in self.enrolled_course_ids
        
        if is_enrolled:
            from ui.mahasiswa.detail_matakuliah_page import DetailMatakuliahPage
            parent = self.parent()
            while parent and not hasattr(parent, 'content_stack'):
                parent = parent.parent()
            if parent and hasattr(parent, 'content_stack'):
                self.detail_page = DetailMatakuliahPage(course, is_enrolled=True, user_id=self.user_id)
                parent.content_stack.addWidget(self.detail_page)
                parent.content_stack.setCurrentWidget(self.detail_page)
        else:
            enroll_code = course.get('enroll_code', '')
            dialog = EnrollmentDialog(course.get('nama', 'Mata Kuliah'), enroll_code, self.user_id, self)
            if dialog.exec() == QDialog.Accepted:
                # Refresh enrolled courses
                success, enrolled = get_enrolled_courses(self.user_id)
                if success and enrolled:
                    self.enrolled_course_ids = {item['courses']['id'] for item in enrolled if item.get('courses')}
                self.filter_courses()
                db_signals.data_changed.emit()