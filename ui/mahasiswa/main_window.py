from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt
from ui.mahasiswa.dashboard_page import DashboardPage
from ui.mahasiswa.tugas_page import TugasPage
from ui.mahasiswa.matakuliah_page import MatakuliahPage
from ui.mahasiswa.profile_page import ProfilePage
from database.db_manager import db_signals
import os


class MahasiswaMainWindow(QMainWindow):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data or {}
        if 'id' not in self.user_data and 'id' in user_data:
            self.user_data['id'] = user_data['id']
        print(f"[DEBUG] MahasiswaMainWindow user_data: {self.user_data}")
        self.setWindowTitle("AkademiQ - Dashboard Mahasiswa")
        self.setMinimumSize(1300, 750)
        self.setStyleSheet("""QMainWindow {background-color: #F8FAFC;}""")
        self.setup_ui()
        self.load_mahasiswa_stylesheet()
        self.load_user_info()
        db_signals.data_changed.connect(self.on_data_changed)
    
    def on_data_changed(self):
        self.dashboard_page.refresh_data()
        self.tugas_page.load_data()
    
    def load_mahasiswa_stylesheet(self):
        style_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(self.styleSheet() + f.read())
                print(f"[SUKSES] Mahasiswa QSS dimuat dari: {style_path}")
            except Exception as e:
                print(f"[ERROR] Gagal membaca QSS mahasiswa: {e}")
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #F8FAFC;")
        
        # Inisialisasi pages 
        self.dashboard_page = DashboardPage(self.user_data)
        self.tugas_page = TugasPage(self.user_data)
        self.matakuliah_page = MatakuliahPage(self.user_data)  # Kirim user_data
        self.profile_page = ProfilePage(self.user_data)
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.tugas_page)
        self.content_stack.addWidget(self.matakuliah_page)
        self.content_stack.addWidget(self.profile_page)
        
        main_layout.addWidget(self.content_stack, 1)
        
        # Set default page
        self.content_stack.setCurrentWidget(self.dashboard_page)
    
    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E2E8F0;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(20)
        
        # Logo nanti
        logo_label = QLabel("🎓 AkademiQ")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1E293B;
            padding: 10px 0px 20px 0px;
        """)
        sidebar_layout.addWidget(logo_label)
        
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(8)
        
        # Simpan reference buttons untuk styling
        self.nav_buttons = []
        
        nav_items = [
            ("📊", "Dashboard", 0),
            ("📋", "Tugas", 1),
            ("📚", "Mata Kuliah", 2),
            ("👤", "Profil", 3),
        ]
        
        for icon, text, index in nav_items:
            btn = QPushButton(f"  {icon}  {text}")
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(48)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            btn.setStyleSheet("""
                QPushButton#navButton {
                    text-align: left;
                    padding: 12px 16px;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 500;
                    color: #64748B;
                    background-color: transparent;
                    border: none;
                }
                QPushButton#navButton:hover {
                    background-color: #F1F5F9;
                    color: #1E293B;
                }
                QPushButton#navButton:checked {
                    background-color: #EFF6FF;
                    color: #3B82F6;
                }
            """)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        # Set default checked
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
        
        sidebar_layout.addLayout(nav_layout)
        sidebar_layout.addStretch()
        
        # User info di sidebar bottom
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 16px;
                padding: 12px;
            }
        """)
        user_layout = QHBoxLayout(user_frame)
        
        self.avatar_label = QLabel("👨‍🎓")
        self.avatar_label.setStyleSheet("font-size: 32px;")
        user_layout.addWidget(self.avatar_label)
        
        user_text_layout = QVBoxLayout()
        self.user_name_label = QLabel("Mahasiswa")
        self.user_name_label.setStyleSheet("font-weight: bold; color: #1E293B;")
        self.user_role_label = QLabel("Mahasiswa")
        self.user_role_label.setStyleSheet("font-size: 11px; color: #94A3B8;")
        user_text_layout.addWidget(self.user_name_label)
        user_text_layout.addWidget(self.user_role_label)
        user_layout.addLayout(user_text_layout)
        
        user_layout.addStretch()
        
        sidebar_layout.addWidget(user_frame)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setFixedHeight(44)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton#logoutBtn {
                background-color: #FEF2F2;
                color: #DC2626;
                border-radius: 12px;
                font-weight: 600;
                border: none;
                padding: 12px;
            }
            QPushButton#logoutBtn:hover {
                background-color: #FEE2E2;
            }
        """)
        sidebar_layout.addWidget(logout_btn)
    
    def load_user_info(self):
        """Load user info ke sidebar"""
        if self.user_data:
            name = self.user_data.get('nama', 'Mahasiswa')
            self.user_name_label.setText(name[:20] + "..." if len(name) > 20 else name)
            self.user_role_label.setText("Mahasiswa")
            self.avatar_label.setText("👨‍🎓")
    
    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # Refresh page content when switching
        if index == 0:  # Dashboard
            self.dashboard_page.refresh_data()
        elif index == 1:  # Tugas
            self.tugas_page.load_data()
        elif index == 2:  # Mata Kuliah
            self.matakuliah_page.filter_courses()
        elif index == 3:  # Profil
            self.profile_page.load_profile()
    
    def logout(self):
        reply = QMessageBox.question(
            self, "Konfirmasi Logout", 
            "Apakah Anda yakin ingin logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()
            
    def show_course_detail(self, course_data):
        from ui.mahasiswa.detail_matakuliah_page import DetailMatakuliahPage
        self.detail_page = DetailMatakuliahPage(course_data)
        self.content_stack.addWidget(self.detail_page)
        self.content_stack.setCurrentWidget(self.detail_page)
    
    def go_back_to_courses(self):
        self.content_stack.setCurrentWidget(self.matakuliah_page)