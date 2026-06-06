from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QGroupBox, QPushButton, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from ui.mahasiswa.widgets import StatCircleCard, TugasCard, CourseCard
from database.db_manager import get_personal_tasks, get_enrolled_courses, get_courses, get_course_by_id


class DashboardPage(QWidget):
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.user_id = user_data.get('id') if user_data else None
        self.show_all = False
        self.all_courses = []
        self.enrolled_courses = set()
        self.tasks_data = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)
        
        header = QHBoxLayout()
        name = self.user_data.get('nama', 'Mahasiswa')
        greeting = QLabel(f"Hello, {name}!")
        greeting.setObjectName("greetingLabel")
        header.addWidget(greeting)
        header.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari mata kuliah...")
        self.search_input.setFixedWidth(280)
        self.search_input.textChanged.connect(self.filter_courses)
        header.addWidget(self.search_input)
        main_layout.addLayout(header)
        
        top_row = QHBoxLayout()
        top_row.setSpacing(20)
        top_row.setAlignment(Qt.AlignTop)
        
        self.stat_circle = StatCircleCard("Progress Tugas", "#3B82F6")
        self.stat_circle.setMinimumHeight(220)
        self.stat_circle.setMaximumHeight(250)
        self.stat_circle.setFixedWidth(220)
        top_row.addWidget(self.stat_circle)
        
        active_tasks_group = QGroupBox("📋 Tugas Aktif per Mata Kuliah")
        active_tasks_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                font-weight: bold;
                font-size: 14px;
                padding-top: 16px;
                margin-top: 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)
        
        active_tasks_layout = QVBoxLayout(active_tasks_group)
        active_tasks_layout.setContentsMargins(10, 10, 10, 10)
        
        self.active_tasks_scroll = QScrollArea()
        self.active_tasks_scroll.setWidgetResizable(True)
        self.active_tasks_scroll.setFrameShape(QFrame.NoFrame)
        self.active_tasks_scroll.setMaximumHeight(250)
        self.active_tasks_scroll.setMinimumHeight(200)
        
        self.active_tasks_container = QWidget()
        self.active_tasks_layout_inner = QVBoxLayout(self.active_tasks_container)
        self.active_tasks_layout_inner.setSpacing(10)
        self.active_tasks_layout_inner.setContentsMargins(10, 5, 10, 5)
        self.active_tasks_layout_inner.setAlignment(Qt.AlignTop)
        
        self.active_tasks_scroll.setWidget(self.active_tasks_container)
        active_tasks_layout.addWidget(self.active_tasks_scroll)
        
        top_row.addWidget(active_tasks_group, 1)
        main_layout.addLayout(top_row)
        
        courses_group = QGroupBox("📚 Daftar Mata Kuliah")
        courses_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                font-weight: bold;
                font-size: 14px;
                padding-top: 16px;
                margin-top: 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)
        
        courses_layout = QVBoxLayout(courses_group)
        courses_layout.setContentsMargins(10, 10, 10, 10)
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.show_all_btn = QPushButton("📚 Semua Mata Kuliah")
        self.show_all_btn.setCheckable(True)
        self.show_all_btn.setCursor(Qt.PointingHandCursor)
        self.show_all_btn.setFixedHeight(32)
        self.show_all_btn.clicked.connect(lambda: self.set_filter(show_all=True))
        filter_layout.addWidget(self.show_all_btn)
        
        self.show_taking_btn = QPushButton("📖 Sedang Diambil")
        self.show_taking_btn.setCheckable(True)
        self.show_taking_btn.setChecked(True)
        self.show_taking_btn.setCursor(Qt.PointingHandCursor)
        self.show_taking_btn.setFixedHeight(32)
        self.show_taking_btn.clicked.connect(lambda: self.set_filter(show_all=False))
        filter_layout.addWidget(self.show_taking_btn)
        
        filter_layout.addStretch()
        courses_layout.addLayout(filter_layout)
        
        self.courses_scroll = QScrollArea()
        self.courses_scroll.setWidgetResizable(True)
        self.courses_scroll.setFrameShape(QFrame.NoFrame)
        self.courses_scroll.setMinimumHeight(300)
        
        self.courses_container = QWidget()
        self.courses_grid = QGridLayout(self.courses_container)
        self.courses_grid.setSpacing(15)
        self.courses_grid.setContentsMargins(10, 10, 10, 10)
        
        self.courses_scroll.setWidget(self.courses_container)
        courses_layout.addWidget(self.courses_scroll)
        
        main_layout.addWidget(courses_group, 1)
    
    def set_filter(self, show_all):
        self.show_all = show_all
        
        if show_all:
            self.show_all_btn.setStyleSheet("background-color: #EFF6FF; color: #3B82F6; border-radius: 20px; padding: 6px 16px; border: none;")
            self.show_taking_btn.setStyleSheet("background-color: #F1F5F9; color: #64748B; border-radius: 20px; padding: 6px 16px; border: none;")
        else:
            self.show_all_btn.setStyleSheet("background-color: #F1F5F9; color: #64748B; border-radius: 20px; padding: 6px 16px; border: none;")
            self.show_taking_btn.setStyleSheet("background-color: #EFF6FF; color: #3B82F6; border-radius: 20px; padding: 6px 16px; border: none;")
        
        self.filter_courses()
    
    def load_data(self):
        if not self.user_id:
            return
        
        success, tasks = get_personal_tasks(self.user_id)
        if success:
            self.tasks_data = tasks
        else:
            self.tasks_data = []
        
        total = len(self.tasks_data)
        done = len([t for t in self.tasks_data if t.get('status') == 'Done'])
        self.stat_circle.update_stats(done, total)
        
        active_tasks = [t for t in self.tasks_data if t.get('status') != 'Done']
        active_tasks.sort(key=lambda x: x.get('deadline_date', '9999-12-31'))
        
        self._clear_layout(self.active_tasks_layout_inner)
        
        matkul_tasks = {}
        for task in active_tasks:
            matkul = task.get('course_name', 'Unknown')
            if matkul not in matkul_tasks:
                matkul_tasks[matkul] = []
            matkul_tasks[matkul].append(task)
        
        for matkul, tasks in matkul_tasks.items():
            matkul_label = QLabel(f"📚 {matkul}")
            matkul_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 8px 0px 4px 0px;")
            self.active_tasks_layout_inner.addWidget(matkul_label)
            
            for task in tasks:
                tugas_card = TugasCard(
                    task.get('judul', '-'), 
                    task.get('course_name', '-'),
                    task.get('deadline_date', '-'), 
                    task.get('status', 'Pending'),
                    task.get('priority', 'Medium')
                )
                self.active_tasks_layout_inner.addWidget(tugas_card)
        
        if not active_tasks:
            empty_label = QLabel("✨ Tidak ada tugas aktif. Selamat! ✨")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94A3B8; padding: 30px;")
            self.active_tasks_layout_inner.addWidget(empty_label)
        
        self.load_courses()
    
    def load_courses(self):
        success, enrolled = get_enrolled_courses(self.user_id)
        if success and enrolled:
            self.enrolled_courses = {item['courses']['nama'] for item in enrolled if item.get('courses')}
        else:
            self.enrolled_courses = set()
        
        success, courses = get_courses()
        if success:
            self.all_courses = courses
        else:
            self.all_courses = []
        
        self.filter_courses()
    
    def filter_courses(self):
        search_text = self.search_input.text().lower()
        filtered = []
        
        for course in self.all_courses:
            course_nama = course.get('nama', '') if isinstance(course, dict) else ''
            course_dosen = course.get('dosen', '') if isinstance(course, dict) else ''
            
            if not self.show_all and course_nama not in self.enrolled_courses:
                continue
            if search_text and search_text not in course_nama.lower() and search_text not in course_dosen.lower():
                continue
            filtered.append(course)
        
        self._clear_grid(self.courses_grid)
        self.courses_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        for i, course in enumerate(filtered):
            course_nama = course.get('nama', '') if isinstance(course, dict) else ''
            course_sks = course.get('sks', 3) if isinstance(course, dict) else 3
            course_dosen = course.get('dosen', '') if isinstance(course, dict) else ''
            is_enrolled = course_nama in self.enrolled_courses
            
            card = CourseCard(
                course_nama, course_sks, 
                course_dosen, is_enrolled, is_enrolled
            )
            card.setMinimumWidth(400)
            card.setMaximumWidth(600)
            card.setCursor(Qt.PointingHandCursor)
            card.set_click_callback(lambda c=course: self.open_course_detail(c))
            self.courses_grid.addWidget(card, i, 0, Qt.AlignTop | Qt.AlignLeft)
        
        if not filtered:
            empty_label = QLabel("✨ Tidak ada mata kuliah yang ditemukan ✨")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94A3B8; padding: 50px;")
            self.courses_grid.addWidget(empty_label, 0, 0, 1, 1, Qt.AlignCenter)
    
    def open_course_detail(self, course):
        from ui.mahasiswa.detail_matakuliah_page import DetailMatakuliahPage
        
        course_nama = course.get('nama', '') if isinstance(course, dict) else ''
        course_id = course.get('id', 0) if isinstance(course, dict) else 0
        is_enrolled = course_nama in self.enrolled_courses
        
        parent = self.parent()
        while parent and not hasattr(parent, 'content_stack'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'content_stack'):
            success, full_course = get_course_by_id(course_id)
            if success and full_course:
                self.detail_page = DetailMatakuliahPage(full_course, is_enrolled, self.user_id)
                parent.content_stack.addWidget(self.detail_page)
                parent.content_stack.setCurrentWidget(self.detail_page)
    
    def refresh_data(self):
        self.load_data()
    
    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _clear_grid(self, grid):
        while grid.count():
            child = grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()