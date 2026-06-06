from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from database.db_manager import enroll_course


class EnrollmentDialog(QDialog):
    def __init__(self, course_name, enroll_code, user_id, parent=None):
        super().__init__(parent)
        self.course_name = course_name
        self.enroll_code = enroll_code
        self.user_id = user_id
        self.setWindowTitle(f"Join Mata Kuliah - {course_name}")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        icon_label = QLabel("🔑")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        main_layout.addWidget(icon_label)
        
        title = QLabel(f"Join Mata Kuliah: {self.course_name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_text = QLabel(
            "Silakan masukkan kode enrollment yang diberikan oleh dosen.\n\n"
            f"💡 Kode enrollment untuk {self.course_name}: {self.enroll_code}"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #64748B; font-size: 12px;")
        info_layout.addWidget(info_text)
        main_layout.addWidget(info_frame)
        
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Masukkan kode enrollment...")
        self.code_input.setStyleSheet("QLineEdit { border: none; padding: 12px; font-size: 14px; }")
        input_layout.addWidget(self.code_input)
        main_layout.addWidget(input_frame)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        
        join_btn = QPushButton("🔓 Join Mata Kuliah")
        join_btn.setObjectName("primary_btn")
        join_btn.clicked.connect(self._handle_join)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(join_btn)
        main_layout.addLayout(btn_layout)
    
    def _handle_join(self):
        code = self.code_input.text().strip().upper()
        
        if not code:
            QMessageBox.warning(self, "Validasi Gagal", "Silakan masukkan kode enrollment!")
            return
        
        success, message = enroll_course(self.user_id, code)
        
        if success:
            QMessageBox.information(self, "Berhasil", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Gagal", message)