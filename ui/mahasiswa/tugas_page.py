from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFileDialog,
    QMessageBox, QHeaderView, QDialog, QFormLayout, QLineEdit,
    QTextEdit, QDateEdit, QDialogButtonBox, QMenu
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QBrush, QAction
from database.db_manager import (
    get_all_tasks, add_personal_task, update_personal_task, 
    delete_personal_task, update_task_status, update_task_priority
)

class TaskDialog(QDialog):
    def __init__(self, parent=None, task_data=None, is_edit=False):
        super().__init__(parent)
        self.task_data = task_data
        self.is_edit = is_edit
        self.setWindowTitle("✏️ Edit Tugas" if is_edit else "➕ Tambah Tugas Baru")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setup_ui()
        
        if is_edit and task_data:
            self.load_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        input_style = """
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px;
                background-color: white;
                color: #1E293B;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #3B82F6;
            }
        """
        
        self.judul_input = QLineEdit()
        self.judul_input.setPlaceholderText("Masukkan nama/judul tugas...")
        self.judul_input.setStyleSheet(input_style)
        form_layout.addRow("Nama Tugas:", self.judul_input)
        
        self.matkul_input = QLineEdit()
        self.matkul_input.setPlaceholderText("Masukkan mata kuliah...")
        self.matkul_input.setStyleSheet(input_style)
        form_layout.addRow("Mata Kuliah:", self.matkul_input)
        
        self.deskripsi_input = QTextEdit()
        self.deskripsi_input.setPlaceholderText("Detail deskripsi tugas (opsional)...")
        self.deskripsi_input.setFixedHeight(80)
        self.deskripsi_input.setStyleSheet(input_style)
        form_layout.addRow("Deskripsi:", self.deskripsi_input)
        
        self.deadline_date = QDateEdit()
        self.deadline_date.setCalendarPopup(True)
        self.deadline_date.setDate(QDate.currentDate())
        self.deadline_date.setDisplayFormat("yyyy-MM-dd")
        self.deadline_date.setStyleSheet(input_style)
        form_layout.addRow("Tenggat Waktu:", self.deadline_date)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setCurrentText("Medium")
        self.priority_combo.setStyleSheet(input_style)
        form_layout.addRow("Prioritas:", self.priority_combo)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Not Started", "Doing", "Done"])
        self.status_combo.setCurrentText("Pending")
        self.status_combo.setStyleSheet(input_style)
        form_layout.addRow("Status Awal:", self.status_combo)
        
        main_layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Simpan")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Batal")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.button_box.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
        """)
        main_layout.addWidget(self.button_box)
        
    def load_data(self):
        if not self.task_data:
            return
        self.judul_input.setText(self.task_data.get('tugas', ''))
        self.matkul_input.setText(self.task_data.get('matkul', ''))
        self.deskripsi_input.setText(self.task_data.get('deskripsi', ''))
        
        deadline = self.task_data.get('deadline', '')
        if deadline:
            date = QDate.fromString(deadline, "yyyy-MM-dd")
            if date.isValid():
                self.deadline_date.setDate(date)
        
        self.priority_combo.setCurrentText(self.task_data.get('priority', 'Medium'))
        self.status_combo.setCurrentText(self.task_data.get('status', 'Pending'))
    
    def get_data(self):
        return {
            'judul': self.judul_input.text().strip(),
            'matkul': self.matkul_input.text().strip(),
            'deskripsi': self.deskripsi_input.toPlainText().strip(),
            'deadline': self.deadline_date.date().toString("yyyy-MM-dd"),
            'priority': self.priority_combo.currentText(),
            'status': self.status_combo.currentText()
        }


class TugasPage(QWidget):
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.user_id = user_data.get('id') if user_data else None
        self.tasks_data = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        # Header Utama
        header = QHBoxLayout()
        title = QLabel("📋 Rekapitulasi Tugas")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        header.addWidget(title)
        header.addStretch()
        
        self.add_btn = QPushButton("➕ Tambah Tugas")
        self.add_btn.setObjectName("primary_btn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setFixedHeight(38)
        self.add_btn.setStyleSheet("""
            QPushButton#primary_btn {
                background-color: #3B82F6;
                color: white;
                border-radius: 10px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton#primary_btn:hover {
                background-color: #2563EB;
            }
        """)
        self.add_btn.clicked.connect(self.add_task)
        header.addWidget(self.add_btn)
        layout.addLayout(header)
        
        # Statistik card
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)  # Jarak antar card agak lebar agar lega
        
        self.total_label = self._create_stat_badge("📊 Total Tugas", "0", "#3B82F6")
        self.done_label = self._create_stat_badge("✅ Tugas Selesai", "0", "#10B981")
        self.pending_label = self._create_stat_badge("⏳ Belum Selesai", "0", "#EF4444")
        
        # parameter stretch=1 agar membagi rata dari kiri ke kanan secara penuh
        stats_layout.addWidget(self.total_label, stretch=1)
        stats_layout.addWidget(self.done_label, stretch=1)
        stats_layout.addWidget(self.pending_label, stretch=1)
        
        layout.addLayout(stats_layout)
        
        # Area Filter
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        filter_layout.addWidget(QLabel("🔍 Filter Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("Semua")
        for status in ["Pending", "Not Started", "Doing", "Done"]:
            self.status_filter.addItem(status)
        self.status_filter.setFixedWidth(120)
        self.status_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addWidget(QLabel("Filter Prioritas:"))
        self.priority_filter = QComboBox()
        self.priority_filter.addItem("Semua")
        for priority in ["Low", "Medium", "High"]:
            self.priority_filter.addItem(priority)
        self.priority_filter.setFixedWidth(100)
        self.priority_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(self.priority_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Pembuatan QTableWidget
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(7)
        self.tasks_table.setHorizontalHeaderLabels(["📝 Tugas", "📚 Mata Kuliah", "📅 Tenggat", "⚡ Prioritas", "📌 Status", "📎 Sumber", "🔧 Aksi"])
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tasks_table.setMinimumHeight(400)
        
        # Penyesuaian kolom otomatis 
        header_view = self.tasks_table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)              
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)              
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)     
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)     
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)     
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)     
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)     
        
        self.tasks_table.verticalHeader().setDefaultSectionSize(60)
        
        self.tasks_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #1E293B;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                font-weight: 600;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.tasks_table)
        
        # Tombol export CSV
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.export_btn = QPushButton("📁 Export CSV")
        self.export_btn.setObjectName("secondary_btn")
        self.export_btn.setFixedHeight(34)
        self.export_btn.setStyleSheet("""
            QPushButton#secondary_btn {
                background-color: #F1F5F9;
                color: #1E293B;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton#secondary_btn:hover {
                background-color: #E2E8F0;
            }
        """)
        self.export_btn.clicked.connect(self.export_csv)
        export_layout.addWidget(self.export_btn)
        
        layout.addLayout(export_layout)
    
    def _create_stat_badge(self, title, value, color):
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget { 
                background-color: white; 
                border-radius: 12px; 
                border: 1px solid #E2E8F0; 
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #64748B; border: none;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color}; border: none;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        widget.value_label = value_label
        return widget
    
    def load_data(self):
        if not self.user_id:
            return
        self.tasks_data = get_all_tasks(self.user_id)
        self.update_table()
               
    def update_table(self):
        status = self.status_filter.currentText()
        priority = self.priority_filter.currentText()
        
        filtered = [t for t in self.tasks_data]
        if status != "Semua":
            filtered = [t for t in filtered if t.get('status') == status]
        if priority != "Semua":
            filtered = [t for t in filtered if t.get('priority') == priority]
        
        self.tasks_table.setRowCount(len(filtered))
        
        total = len(self.tasks_data)
        done = len([t for t in self.tasks_data if t.get('status') == 'Done'])
        self.total_label.value_label.setText(str(total))
        self.done_label.value_label.setText(str(done))
        self.pending_label.value_label.setText(str(total - done))
        
        priority_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
        status_colors = {"Pending": "#F59E0B", "Not Started": "#EF4444", "Doing": "#3B82F6", "Done": "#10B981"}
        
        for row, task in enumerate(filtered):
            source = task.get('source', 'personal')
            is_personal = source == 'personal'
            
            self.tasks_table.setItem(row, 0, QTableWidgetItem(task.get('tugas', '-')))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task.get('matkul', '-')))
            
            deadline_item = QTableWidgetItem(task.get('deadline', '-'))
            deadline_item.setTextAlignment(Qt.AlignCenter)
            self.tasks_table.setItem(row, 2, deadline_item)
            
            # Container ComboBox Prioritas
            p_container = QWidget()
            p_layout = QHBoxLayout(p_container)
            p_layout.setContentsMargins(12, 0, 12, 0)
            p_layout.setAlignment(Qt.AlignCenter)
            p_combo = QComboBox()
            p_combo.addItems(["Low", "Medium", "High"])
            p_combo.setCurrentText(task.get('priority', 'Medium'))
            p_combo.setFixedSize(90, 32)
            p_combo.setStyleSheet(f"QComboBox {{ background-color: {priority_colors.get(task.get('priority', 'Medium'))}; color: white; border-radius: 6px; font-size: 11px; font-weight: bold; padding-left: 8px; }} QComboBox::drop-down {{ border: none; }}")
            p_combo.currentTextChanged.connect(lambda new_val, t=task: self.change_priority(t, new_val))
            p_layout.addWidget(p_combo)
            self.tasks_table.setCellWidget(row, 3, p_container)
            
            # Container ComboBox Status
            s_container = QWidget()
            s_layout = QHBoxLayout(s_container)
            s_layout.setContentsMargins(12, 0, 12, 0)
            s_layout.setAlignment(Qt.AlignCenter)
            s_combo = QComboBox()
            s_combo.addItems(["Pending", "Not Started", "Doing", "Done"])
            s_combo.setCurrentText(task.get('status', 'Pending'))
            s_combo.setFixedSize(105, 32)
            s_combo.setStyleSheet(f"QComboBox {{ background-color: {status_colors.get(task.get('status', 'Pending'))}; color: white; border-radius: 6px; font-size: 11px; font-weight: bold; padding-left: 8px; }} QComboBox::drop-down {{ border: none; }}")
            s_combo.currentTextChanged.connect(lambda new_val, t=task, s=source: self.change_status(t, new_val, s))
            s_layout.addWidget(s_combo)
            self.tasks_table.setCellWidget(row, 4, s_container)
            
            source_item = QTableWidgetItem("📝 Personal" if is_personal else "📚 Dosen")
            source_item.setTextAlignment(Qt.AlignCenter)
            self.tasks_table.setItem(row, 5, source_item)
            
            # Tombol aksi dengan menu dropdown
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setAlignment(Qt.AlignCenter)
            
            menu_btn = QPushButton("⋮")
            menu_btn.setFixedSize(30, 32)
            menu_btn.setCursor(Qt.PointingHandCursor)
            menu_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #64748B;
                    border: none;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                    color: #1E293B;
                }
                QPushButton::menu-indicator { image: none; }
            """)
            
            action_menu = QMenu(menu_btn)
            action_menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #E2E8F0;
                    border-radius: 6px;
                    padding: 4px 0px;
                }
                QMenu::item {
                    padding: 6px 20px 6px 12px;
                    color: #1E293B;
                    font-size: 12px;
                }
                QMenu::item:selected {
                    background-color: #F1F5F9;
                    color: #3B82F6;
                }
            """)
            
            if is_personal:
                edit_action = QAction("✏️  Edit", self)
                edit_action.triggered.connect(lambda checked, t=task: self.edit_task(t))
                action_menu.addAction(edit_action)
                
                delete_action = QAction("🗑️  Hapus", self)
                delete_action.triggered.connect(lambda checked, t=task: self.delete_task(t))
                action_menu.addAction(delete_action)
            else:
                info_action = QAction("🔒 Tugas Terkunci", self)
                info_action.setEnabled(False)
                action_menu.addAction(info_action)
            
            menu_btn.setMenu(action_menu)
            action_layout.addWidget(menu_btn)
            self.tasks_table.setCellWidget(row, 6, action_widget)

    def filter_tasks(self):
        self.update_table()

    def add_task(self):
        dialog = TaskDialog(self, is_edit=False)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            success, result = add_personal_task(self.user_id, data['judul'], data['matkul'], data['deskripsi'], data['deadline'], data['priority'], data['status'])
            if success:
                QMessageBox.information(self, "Berhasil", "Tugas baru ditambahkan!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", f"Gagal menambah tugas: {result}")
                

    def edit_task(self, task):
        dialog = TaskDialog(self, task_data=task, is_edit=True)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            success, result = update_personal_task(task['id'], self.user_id, data['judul'], data['matkul'], data['deskripsi'], data['deadline'], data['priority'], data['status'])
            if success:
                QMessageBox.information(self, "Berhasil", "Tugas berhasil diperbarui!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", f"Gagal update tugas: {result}")

    def delete_task(self, task):
        reply = QMessageBox.question(self, "Konfirmasi", f"Hapus tugas '{task.get('tugas')}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, result = delete_personal_task(task['id'], self.user_id)
            if success:
                QMessageBox.information(self, "Berhasil", "Tugas berhasil dihapus!")
                self.load_data()

    def change_status(self, task, new_status, source):
        success, _ = update_task_status(task['id'], self.user_id, new_status, source)
        if success:
            task['status'] = new_status
            total = len(self.tasks_data)
            done = len([t for t in self.tasks_data if t.get('status') == 'Done'])
            self.done_label.value_label.setText(str(done))
            self.pending_label.value_label.setText(str(total - done))
            
            status_colors = {"Pending": "#F59E0B", "Not Started": "#EF4444", "Doing": "#3B82F6", "Done": "#10B981"}
            sender_combo = self.sender()
            if sender_combo:
                sender_combo.setStyleSheet(f"QComboBox {{ background-color: {status_colors.get(new_status)}; color: white; border-radius: 6px; font-size: 11px; font-weight: bold; padding-left: 8px; }} QComboBox::drop-down {{ border: none; }}")

    def change_priority(self, task, new_priority):
        success, _ = update_task_priority(task['id'], self.user_id, new_priority, 'personal')
        if success:
            task['priority'] = new_priority
            
            priority_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
            sender_combo = self.sender()
            if sender_combo:
                sender_combo.setStyleSheet(f"QComboBox {{ background-color: {priority_colors.get(new_priority)}; color: white; border-radius: 6px; font-size: 11px; font-weight: bold; padding-left: 8px; }} QComboBox::drop-down {{ border: none; }}")

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Tugas", "tugas_export.csv", "CSV Files (*.csv)")
        if file_path:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Tugas', 'Mata Kuliah', 'Tenggat', 'Prioritas', 'Status', 'Sumber'])
                for task in self.tasks_data:
                    writer.writerow([task.get('tugas', '-'), task.get('matkul', '-'), task.get('deadline', '-'), task.get('priority', '-'), task.get('status', '-'), "Personal" if task.get('source') == 'personal' else "Dosen"])
            QMessageBox.information(self, "Berhasil", f"Berhasil diexport ke:\n{file_path}")