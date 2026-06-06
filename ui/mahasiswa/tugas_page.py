from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFileDialog,
    QMessageBox, QHeaderView, QDialog, QFormLayout, QLineEdit,
    QTextEdit, QDateEdit, QDialogButtonBox, QMenu
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QBrush, QAction
from database.db_manager import (
    get_personal_tasks, add_personal_task, update_personal_task,
    hapus_personal_task, db_signals
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
        
        self.judul_input = QLineEdit()
        self.judul_input.setPlaceholderText("Masukkan nama/judul tugas...")
        form_layout.addRow("Nama Tugas:", self.judul_input)
        
        self.matkul_input = QLineEdit()
        self.matkul_input.setPlaceholderText("Masukkan mata kuliah...")
        form_layout.addRow("Mata Kuliah:", self.matkul_input)
        
        self.deskripsi_input = QTextEdit()
        self.deskripsi_input.setPlaceholderText("Detail deskripsi tugas (opsional)...")
        self.deskripsi_input.setFixedHeight(80)
        form_layout.addRow("Deskripsi:", self.deskripsi_input)
        
        self.deadline_date = QDateEdit()
        self.deadline_date.setCalendarPopup(True)
        self.deadline_date.setDate(QDate.currentDate())
        self.deadline_date.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Tenggat Waktu:", self.deadline_date)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setCurrentText("Medium")
        form_layout.addRow("Prioritas:", self.priority_combo)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Not Started", "Doing", "Done"])
        self.status_combo.setCurrentText("Pending")
        form_layout.addRow("Status Awal:", self.status_combo)
        
        main_layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Simpan")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Batal")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
    
    def load_data(self):
        if not self.task_data:
            return
        self.judul_input.setText(self.task_data.get('judul', ''))
        self.matkul_input.setText(self.task_data.get('course_name', ''))
        self.deskripsi_input.setText(self.task_data.get('deskripsi', ''))
        
        deadline = self.task_data.get('deadline_date', '')
        if deadline:
            date = QDate.fromString(deadline, "yyyy-MM-dd")
            if date.isValid():
                self.deadline_date.setDate(date)
        
        self.priority_combo.setCurrentText(self.task_data.get('priority', 'Medium'))
        self.status_combo.setCurrentText(self.task_data.get('status', 'Pending'))
    
    def get_data(self):
        return {
            'judul': self.judul_input.text().strip(),
            'course_name': self.matkul_input.text().strip(),
            'deskripsi': self.deskripsi_input.toPlainText().strip(),
            'deadline_date': self.deadline_date.date().toString("yyyy-MM-dd"),
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
        db_signals.data_changed.connect(self.load_data)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        header = QHBoxLayout()
        title = QLabel("📋 Rekapitulasi Tugas")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch()
        
        self.add_btn = QPushButton("➕ Tambah Tugas")
        self.add_btn.setObjectName("primary_btn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setFixedHeight(38)
        self.add_btn.clicked.connect(self.add_task)
        header.addWidget(self.add_btn)
        layout.addLayout(header)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_label = self._create_stat_badge("📊 Total Tugas", "0", "#3B82F6")
        self.done_label = self._create_stat_badge("✅ Tugas Selesai", "0", "#10B981")
        self.pending_label = self._create_stat_badge("⏳ Belum Selesai", "0", "#EF4444")
        
        stats_layout.addWidget(self.total_label, stretch=1)
        stats_layout.addWidget(self.done_label, stretch=1)
        stats_layout.addWidget(self.pending_label, stretch=1)
        layout.addLayout(stats_layout)
        
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
        
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(6)
        self.tasks_table.setHorizontalHeaderLabels(["📝 Tugas", "📚 Mata Kuliah", "📅 Tenggat", "⚡ Prioritas", "📌 Status", "🔧 Aksi"])
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tasks_table.setMinimumHeight(400)
        
        header_view = self.tasks_table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.tasks_table.verticalHeader().setDefaultSectionSize(60)
        layout.addWidget(self.tasks_table)
        
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.export_btn = QPushButton("📁 Export CSV")
        self.export_btn.setObjectName("secondary_btn")
        self.export_btn.setFixedHeight(34)
        self.export_btn.clicked.connect(self.export_csv)
        export_layout.addWidget(self.export_btn)
        layout.addLayout(export_layout)
    
    def _create_stat_badge(self, title, value, color):
        widget = QWidget()
        widget.setObjectName("statBadge")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setObjectName("statBadgeTitle")
        
        value_label = QLabel(value)
        value_label.setObjectName("statBadgeValue")
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        widget.value_label = value_label
        return widget
    
    def load_data(self):
        if not self.user_id:
            return
        success, tasks = get_personal_tasks(self.user_id)
        if success:
            self.tasks_data = tasks
        else:
            self.tasks_data = []
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
            self.tasks_table.setItem(row, 0, QTableWidgetItem(task.get('judul', '-')))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task.get('course_name', '-')))
            
            deadline_item = QTableWidgetItem(task.get('deadline_date', '-'))
            deadline_item.setTextAlignment(Qt.AlignCenter)
            self.tasks_table.setItem(row, 2, deadline_item)
            
            # Priority ComboBox
            p_container = QWidget()
            p_layout = QHBoxLayout(p_container)
            p_layout.setContentsMargins(12, 0, 12, 0)
            p_layout.setAlignment(Qt.AlignCenter)
            p_combo = QComboBox()
            p_combo.addItems(["Low", "Medium", "High"])
            p_combo.setCurrentText(task.get('priority', 'Medium'))
            p_combo.setFixedSize(90, 32)
            p_combo.setStyleSheet(f"QComboBox {{ background-color: {priority_colors.get(task.get('priority', 'Medium'), '#95a5a6')}; color: white; border-radius: 6px; font-size: 11px; font-weight: bold; }}")
            p_combo.currentTextChanged.connect(lambda new_val, t=task: self.change_priority(t, new_val))
            p_layout.addWidget(p_combo)
            self.tasks_table.setCellWidget(row, 3, p_container)
            
            # Status ComboBox
            s_container = QWidget()
            s_layout = QHBoxLayout(s_container)
            s_layout.setContentsMargins(12, 0, 12, 0)
            s_layout.setAlignment(Qt.AlignCenter)
            s_combo = QComboBox()
            s_combo.addItems(["Pending", "Not Started", "Doing", "Done"])
            s_combo.setCurrentText(task.get('status', 'Pending'))
            s_combo.setFixedSize(105, 32)
            s_combo.setStyleSheet(f"QComboBox {{ background-color: {status_colors.get(task.get('status', 'Pending'), '#95a5a6')}; color: white; border-radius: 6px; font-size: 11px; font-weight: bold; }}")
            s_combo.currentTextChanged.connect(lambda new_val, t=task: self.change_status(t, new_val))
            s_layout.addWidget(s_combo)
            self.tasks_table.setCellWidget(row, 4, s_container)
            
            # Action button
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setAlignment(Qt.AlignCenter)
            
            menu_btn = QPushButton("⋮")
            menu_btn.setFixedSize(30, 32)
            menu_btn.setCursor(Qt.PointingHandCursor)
            
            action_menu = QMenu(menu_btn)
            
            edit_action = QAction("✏️  Edit", self)
            edit_action.triggered.connect(lambda checked, t=task: self.edit_task(t))
            action_menu.addAction(edit_action)
            
            delete_action = QAction("🗑️  Hapus", self)
            delete_action.triggered.connect(lambda checked, t=task: self.delete_task(t))
            action_menu.addAction(delete_action)
            
            menu_btn.setMenu(action_menu)
            action_layout.addWidget(menu_btn)
            self.tasks_table.setCellWidget(row, 5, action_widget)
    
    def filter_tasks(self):
        self.update_table()
    
    def add_task(self):
        dialog = TaskDialog(self, is_edit=False)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            success, msg = add_personal_task(
                self.user_id, data['judul'], data['course_name'],
                data['deskripsi'], data['deadline_date'], data['priority']
            )
            if success:
                QMessageBox.information(self, "Berhasil", "Tugas baru ditambahkan!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", f"Gagal menambah tugas: {msg}")
    
    def edit_task(self, task):
        dialog = TaskDialog(self, task_data=task, is_edit=True)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            update_data = {
                'judul': data['judul'],
                'course_name': data['course_name'],
                'deskripsi': data['deskripsi'],
                'deadline_date': data['deadline_date'],
                'priority': data['priority'],
                'status': data['status']
            }
            success, msg = update_personal_task(task['id'], self.user_id, update_data)
            if success:
                QMessageBox.information(self, "Berhasil", "Tugas berhasil diperbarui!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", f"Gagal update tugas: {msg}")
    
    def delete_task(self, task):
        reply = QMessageBox.question(self, "Konfirmasi", f"Hapus tugas '{task.get('judul')}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = hapus_personal_task(task['id'], self.user_id)
            if success:
                QMessageBox.information(self, "Berhasil", "Tugas berhasil dihapus!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", f"Gagal hapus tugas: {msg}")
    
    def change_status(self, task, new_status):
        update_data = {'status': new_status}
        success, msg = update_personal_task(task['id'], self.user_id, update_data)
        if success:
            task['status'] = new_status
            total = len(self.tasks_data)
            done = len([t for t in self.tasks_data if t.get('status') == 'Done'])
            self.done_label.value_label.setText(str(done))
            self.pending_label.value_label.setText(str(total - done))
    
    def change_priority(self, task, new_priority):
        update_data = {'priority': new_priority}
        success, msg = update_personal_task(task['id'], self.user_id, update_data)
        if success:
            task['priority'] = new_priority
    
    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Tugas", "tugas_export.csv", "CSV Files (*.csv)")
        if file_path:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Tugas', 'Mata Kuliah', 'Tenggat', 'Prioritas', 'Status'])
                for task in self.tasks_data:
                    writer.writerow([
                        task.get('judul', '-'), task.get('course_name', '-'),
                        task.get('deadline_date', '-'), task.get('priority', '-'),
                        task.get('status', '-')
                    ])
            QMessageBox.information(self, "Berhasil", f"Berhasil diexport ke:\n{file_path}")