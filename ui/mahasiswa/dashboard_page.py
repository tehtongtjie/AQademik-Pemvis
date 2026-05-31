from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QGroupBox, QPushButton, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from ui.mahasiswa.widgets import StatCircleCard, TugasCard, CourseCard
from database.db_manager import get_all_tasks, get_user_enrolled_courses


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
        
        # Header dengan greeting
        header = QHBoxLayout()
        
        name = self.user_data.get('nama', 'Mahasiswa')
        greeting = QLabel(f"Hello, {name}!")
        greeting.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        header.addWidget(greeting)
        
        header.addStretch()
        
        # Search bar
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
        
        main_layout.addLayout(header)
        
        # Konten bagian atas: dua kotak (stat + tugas aktif)
        top_content = QHBoxLayout()
        top_content.setSpacing(20)
        
        # Kiri: Diag tgs selesai
        self.stat_circle = StatCircleCard("Progress Tugas", "#3B82F6")
        self.stat_circle.setMinimumHeight(220)
        top_content.addWidget(self.stat_circle)
        
        # Kanan: List mata kuliah tugas
        active_tasks_group = QGroupBox("📋 Tugas Aktif per Mata Kuliah")
        active_tasks_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                font-weight: bold;
                font-size: 14px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)
        
        active_tasks_layout = QVBoxLayout(active_tasks_group)
        
        # Scroll area untuk tugas aktif
        self.active_tasks_scroll = QScrollArea()
        self.active_tasks_scroll.setWidgetResizable(True)
        self.active_tasks_scroll.setFrameShape(QFrame.NoFrame)
        self.active_tasks_scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        self.active_tasks_scroll.setMaximumHeight(300)
        
        self.active_tasks_container = QWidget()
        self.active_tasks_layout = QVBoxLayout(self.active_tasks_container)
        self.active_tasks_layout.setSpacing(10)
        self.active_tasks_layout.setContentsMargins(10, 10, 10, 10)
        self.active_tasks_layout.setAlignment(Qt.AlignTop)
        
        self.active_tasks_scroll.setWidget(self.active_tasks_container)
        active_tasks_layout.addWidget(self.active_tasks_scroll)
        
        top_content.addWidget(active_tasks_group, 1)
        
        main_layout.addLayout(top_content)
        
        # Matkul
        courses_group = QGroupBox("📚 Daftar Mata Kuliah")
        courses_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                font-weight: bold;
                font-size: 14px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)
        
        courses_layout = QVBoxLayout(courses_group)
        
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
        courses_layout.addLayout(filter_layout)
        
        # Scroll area untuk daftar mata kuliah
        self.courses_scroll = QScrollArea()
        self.courses_scroll.setWidgetResizable(True)
        self.courses_scroll.setFrameShape(QFrame.NoFrame)
        self.courses_scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
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
        
        # Ambil data tugas dari database
        self.tasks_data = get_all_tasks(self.user_id)
        
        # Hitung statistik
        total = len(self.tasks_data)
        done = len([t for t in self.tasks_data if t.get('status') == 'Done'])
        
        # Update stat circle
        self.stat_circle.update_stats(done, total)
        
        # Tugas aktif (belum selesai)
        active_tasks = [t for t in self.tasks_data if t.get('status') != 'Done']
        active_tasks.sort(key=lambda x: x.get('deadline', '9999-12-31'))
        
        # Clear container
        self._clear_layout(self.active_tasks_layout)
        
        # Tampilkan tugas aktif per mata kuliah
        matkul_tasks = {}
        for task in active_tasks:
            matkul = task.get('matkul', 'Unknown')
            if matkul not in matkul_tasks:
                matkul_tasks[matkul] = []
            matkul_tasks[matkul].append(task)
        
        for matkul, tasks in matkul_tasks.items():
            matkul_label = QLabel(f"📚 {matkul}")
            matkul_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 8px 0px;")
            self.active_tasks_layout.addWidget(matkul_label)
            
            for task in tasks:
                tugas_card = TugasCard(
                    task.get('tugas', '-'), 
                    task.get('matkul', '-'),
                    task.get('deadline', '-'), 
                    task.get('status', 'Pending'),
                    task.get('priority', 'Medium')
                )
                self.active_tasks_layout.addWidget(tugas_card)
        
        if not active_tasks:
            empty_label = QLabel("✨ Tidak ada tugas aktif. Selamat! ✨")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94A3B8; padding: 30px;")
            self.active_tasks_layout.addWidget(empty_label)
        
        # Load daftar mata kuliah
        self.load_courses()
    
    def load_courses(self):
        from database.db_manager import get_all_courses
        
        # Ambil mata kuliah yang sudah di-enroll
        enrolled = get_user_enrolled_courses(self.user_id)
        self.enrolled_courses = {c['nama'] for c in enrolled}
        
        # Ambil semua mata kuliah dari database
        db_courses = get_all_courses()
        
        # Konversi ke format yang digunakan dashboard
        self.all_courses = []
        for course in db_courses:
            self.all_courses.append({
                "id": course['id'],
                "nama": course['nama'],
                "sks": course['sks'],
                "dosen": course['dosen'],
                "taking": course['id'] in [c['id'] for c in enrolled]  # enrolled = taking
            })
        
        self.filter_courses()
    
    def filter_courses(self):
        search_text = self.search_input.text().lower()
        filtered = []
        
        for course in self.all_courses:
            if not self.show_all and not course['taking']:
                continue
            if search_text and search_text not in course['nama'].lower() and search_text not in course['dosen'].lower():
                continue
            filtered.append(course)
        
        self._clear_grid(self.courses_grid)
        
        # Set grid alignment agar tidak stretch
        self.courses_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        for i, course in enumerate(filtered):
            row = i
            col = 0
            is_enrolled = course['nama'] in self.enrolled_courses
            card = CourseCard(
                course['nama'], course['sks'], 
                course['dosen'], course['taking'], is_enrolled
            )
            card.setMinimumWidth(400)  
            card.setMaximumWidth(600)  
            card.setCursor(Qt.PointingHandCursor)
            card.set_click_callback(lambda c=course: self.open_course_detail(c))
            self.courses_grid.addWidget(card, row, col, Qt.AlignTop | Qt.AlignLeft)
        
        if not filtered:
            empty_label = QLabel("✨ Tidak ada mata kuliah yang ditemukan ✨")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #94A3B8; padding: 50px;")
            self.courses_grid.addWidget(empty_label, 0, 0, 1, 1, Qt.AlignCenter)
        
    def open_course_detail(self, course):
        from ui.mahasiswa.detail_matakuliah_page import DetailMatakuliahPage
        
        # Cek apakah sudah terdaftar
        is_enrolled = course['nama'] in self.enrolled_courses
        
        parent = self.parent()
        while parent and not hasattr(parent, 'content_stack'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'content_stack'):
            # Cari data course lengkap dari database
            from database.db_manager import get_course_by_id
            full_course = get_course_by_id(course['id'])
            if full_course:
                self.detail_page = DetailMatakuliahPage(full_course, is_enrolled)
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
    
    def refresh_data(self):
        self.load_data()