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
        self.user_id = user_data.get('id') if user_data else None
        print(f"[DEBUG] MahasiswaMainWindow user_data: {self.user_data}")
        self.setWindowTitle("AkademiQ - Dashboard Mahasiswa")
        self.setMinimumSize(1300, 750)
        self.setup_ui()
        self.load_mahasiswa_stylesheet()
        self.load_user_info()
        db_signals.data_changed.connect(self.on_data_changed)
    
    def on_data_changed(self):
        if hasattr(self, 'dashboard_page'):
            self.dashboard_page.refresh_data()
        if hasattr(self, 'tugas_page'):
            self.tugas_page.load_data()
        if hasattr(self, 'matakuliah_page'):
            self.matakuliah_page.refresh_data()
        if hasattr(self, 'profile_page'):
            self.profile_page.refresh_data()
    
    def load_mahasiswa_stylesheet(self):
        style_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
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
        
        # Content 
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("rightPanel")
        
        self.dashboard_page = DashboardPage(self.user_data)
        self.tugas_page = TugasPage(self.user_data)
        self.matakuliah_page = MatakuliahPage(self.user_data)
        self.profile_page = ProfilePage(self.user_data)
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.tugas_page)
        self.content_stack.addWidget(self.matakuliah_page)
        self.content_stack.addWidget(self.profile_page)
        
        main_layout.addWidget(self.content_stack, 1)
        self.content_stack.setCurrentWidget(self.dashboard_page)
    
    def setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setObjectName("leftPanel")
        self.sidebar.setFixedWidth(360)
        
        root_layout = QVBoxLayout(self.sidebar)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        container = QWidget()
        container.setObjectName("leftPanel")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 48, 40, 48)
        layout.setSpacing(0)
        
        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_frame.setFixedSize(54, 54)
        
        logo_label = QLabel("AQ", logo_frame)
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setGeometry(0, 0, 54, 54)
        
        layout.addWidget(logo_frame)
        layout.addSpacing(20)
        
        app_name = QLabel("AkademiQ")
        app_name.setObjectName("appName")
        layout.addWidget(app_name)
        layout.addSpacing(8)
        
        tagline = QLabel("Platform manajemen akademik terpadu untuk mahasiswa.")
        tagline.setObjectName("tagline")
        tagline.setWordWrap(True)
        layout.addWidget(tagline)
        layout.addSpacing(30)
        
        menu_title = QLabel("MENU")
        menu_title.setObjectName("menuHeader")
        layout.addWidget(menu_title)
        layout.addSpacing(10)
        
        self.btn_dashboard = QPushButton("🏠 Dashboard")
        self.btn_tugas = QPushButton("📋 Tugas")
        self.btn_matkul = QPushButton("📚 Mata Kuliah")
        self.btn_profil = QPushButton("👤 Profil")
        self.btn_logout = QPushButton("🚪 Logout")
        
        for btn in [self.btn_dashboard, self.btn_tugas, self.btn_matkul, self.btn_profil]:
            btn.setObjectName("btnSecondary")
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
            layout.addSpacing(8)
        
        layout.addStretch()
        
        self.btn_logout.setObjectName("btnSecondary")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.btn_logout)
        layout.addSpacing(16)
        
        version = QLabel("Kelompok 4 · v1.0.0")
        version.setObjectName("versionLabel")
        layout.addWidget(version)
        
        root_layout.addWidget(container)
        
        # Connect buttons
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_tugas.clicked.connect(lambda: self.switch_page(1))
        self.btn_matkul.clicked.connect(lambda: self.switch_page(2))
        self.btn_profil.clicked.connect(lambda: self.switch_page(3))
        self.btn_logout.clicked.connect(self.logout)
        
        # Set active style for dashboard button
        self.btn_dashboard.setObjectName("btnPrimary")
    
    def load_user_info(self):
        if self.user_data:
            name = self.user_data.get('nama', 'Mahasiswa')
            # Update user info di sidebar jika diperlukan
            pass
    
    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        
        # Reset all button styles
        for btn in [self.btn_dashboard, self.btn_tugas, self.btn_matkul, self.btn_profil]:
            btn.setObjectName("btnSecondary")
        
        # Set active button style
        active_btn = [self.btn_dashboard, self.btn_tugas, self.btn_matkul, self.btn_profil][index]
        active_btn.setObjectName("btnPrimary")
        
        # Refresh data on switch
        if index == 0:
            self.dashboard_page.refresh_data()
        elif index == 1:
            self.tugas_page.load_data()
        elif index == 2:
            self.matakuliah_page.refresh_data()
        elif index == 3:
            self.profile_page.load_profile()
    
    def show_course_detail(self, course_data, is_enrolled=False):
        from ui.mahasiswa.detail_matakuliah_page import DetailMatakuliahPage
        self.detail_page = DetailMatakuliahPage(
            course_data, 
            is_enrolled=is_enrolled, 
            user_id=self.user_id
        )
        self.content_stack.addWidget(self.detail_page)
        self.content_stack.setCurrentWidget(self.detail_page)
    
    def go_back_to_courses(self):
        self.content_stack.setCurrentWidget(self.matakuliah_page)
    
    def logout(self):
        reply = QMessageBox.question(
            self, "Konfirmasi Logout", 
            "Apakah Anda yakin ingin logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()