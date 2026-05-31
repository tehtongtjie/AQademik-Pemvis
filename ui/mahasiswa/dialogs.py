from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QTextEdit, QPushButton, QDateEdit, QTimeEdit,
    QMessageBox, QWidget
)
from PySide6.QtCore import Qt, QDate, QTime
from logic.validator import Validator

class ProfileEditDialog(QDialog):
    def __init__(self, parent=None, profile_data=None):
        super().__init__(parent)
        self.profile_data = profile_data
        self.setWindowTitle("Edit Profil")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setup_ui()
        from database.db_manager import db_signals
        db_signals.data_changed.connect(self.on_data_changed)
        
        if profile_data:
            self.load_data()
            
    def on_data_changed(self):
        if hasattr(self, 'dashboard_page'):
            self.dashboard_page.refresh_data()
        if hasattr(self, 'tugas_page'):
            self.tugas_page.load_data()
        if hasattr(self, 'profile_page'):
            self.profile_page.refresh_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("✏️ Edit Profil Mahasiswa")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama Lengkap")
        form_layout.addRow("Nama:", self.name_input)
        
        self.nim_input = QLineEdit()
        self.nim_input.setPlaceholderText("NIM")
        self.nim_input.setReadOnly(True)
        form_layout.addRow("NIM:", self.nim_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nomor Telepon")
        form_layout.addRow("Telepon:", self.phone_input)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        self.address_input.setPlaceholderText("Alamat")
        form_layout.addRow("Alamat:", self.address_input)
        
        main_layout.addWidget(form_widget)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Simpan")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
    
    def load_data(self):
        if not self.profile_data:
            return
        self.name_input.setText(self.profile_data.get('name', ''))
        self.nim_input.setText(self.profile_data.get('nim', ''))
        self.email_input.setText(self.profile_data.get('email', ''))
        self.phone_input.setText(self.profile_data.get('phone', ''))
        self.address_input.setText(self.profile_data.get('address', ''))
    
    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'address': self.address_input.toPlainText().strip()
        }
        
class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_id = None
        self.setWindowTitle("Ganti Password")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("🔒 Ganti Password")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        main_layout.addWidget(title)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setPlaceholderText("Password lama")
        form_layout.addRow("Password Lama:", self.old_password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Password baru (min 6 karakter)")
        form_layout.addRow("Password Baru:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Konfirmasi password baru")
        form_layout.addRow("Konfirmasi:", self.confirm_password)
        
        main_layout.addWidget(form_widget)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Ganti Password")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.submit)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
    
    def validate_input(self):
        old = self.old_password.text().strip()
        new = self.new_password.text().strip()
        confirm = self.confirm_password.text().strip()
        
        if not old:
            QMessageBox.warning(self, "Validasi Gagal", "Password lama harus diisi!")
            return False
        
        if len(new) < 6:
            QMessageBox.warning(self, "Validasi Gagal", "Password baru minimal 6 karakter!")
            return False
        
        if new != confirm:
            QMessageBox.warning(self, "Validasi Gagal", "Konfirmasi password baru tidak cocok!")
            return False
        
        return True
    
    def submit(self):
        if not self.validate_input():
            return
        
        from database.db_manager import change_password
        
        success, message = change_password(
            self.user_id,
            self.old_password.text().strip(),
            self.new_password.text().strip()
        )
        
        if success:
            QMessageBox.information(self, "Berhasil", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Gagal", message)
    
    def __init__(self, parent=None, current_password=""):
        super().__init__(parent)
        self.current_password = current_password
        self.setWindowTitle("Ganti Password")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("🔒 Ganti Password")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setPlaceholderText("Password lama")
        form_layout.addRow("Password Lama:", self.old_password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Password baru (min 6 karakter)")
        form_layout.addRow("Password Baru:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Konfirmasi password baru")
        form_layout.addRow("Konfirmasi:", self.confirm_password)
        
        main_layout.addWidget(form_widget)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Ganti Password")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
    
    def get_data(self):
        return {
            'old_password': self.old_password.text().strip(),
            'new_password': self.new_password.text().strip(),
            'confirm_password': self.confirm_password.text().strip()
        }
    
    def validate(self):
        data = self.get_data()
        
        if not data['old_password']:
            QMessageBox.warning(self, "Validasi Gagal", "Password lama harus diisi!")
            return False
        
        if len(data['new_password']) < 6:
            QMessageBox.warning(self, "Validasi Gagal", "Password baru minimal 6 karakter!")
            return False
        
        if data['new_password'] != data['confirm_password']:
            QMessageBox.warning(self, "Validasi Gagal", "Konfirmasi password baru tidak cocok!")
            return False
        
        return True
    
    def submit(self):
        if not self.validate():
            return
        
        from database.db_manager import change_password
        success, message = change_password(
            self.user_id, 
            self.old_password.text(),
            self.new_password.text()
        )
        
        if success:
            QMessageBox.information(self, "Berhasil", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Gagal", message)