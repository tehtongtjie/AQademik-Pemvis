from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt


class StatCircleCard(QFrame):
    def __init__(self, title, color="#3498db", parent=None):
        super().__init__(parent)
        self.setObjectName("statCircleCard")
        self.setFixedSize(180, 180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignCenter)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("statCircleTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Container untuk progress
        self.progress_container = QWidget()
        self.progress_container.setFixedSize(120, 120)
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setAlignment(Qt.AlignCenter)
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setObjectName("statCirclePercent")
        self.percentage_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.percentage_label)
        
        layout.addWidget(self.progress_container, 0, Qt.AlignCenter)
        
        self.done_label = QLabel("0 Selesai")
        self.done_label.setObjectName("statCircleSub")
        self.done_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.done_label)
        
        self.pending_label = QLabel("0 Belum")
        self.pending_label.setObjectName("statCircleSub")
        self.pending_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pending_label)
        
        self.color = color
    
    def update_stats(self, done, total):
        percentage = int((done / total) * 100) if total > 0 else 0
        self.percentage_label.setText(f"{percentage}%")
        self.done_label.setText(f"✅ {done} Selesai")
        self.pending_label.setText(f"⏳ {total - done} Belum")


class CourseCard(QFrame):
    def __init__(self, course_name, sks, lecturer, is_taking=True, is_enrolled=False, parent=None):
        super().__init__(parent)
        self.setObjectName("courseCard")
        self.is_enrolled = is_enrolled or is_taking  # Enrolled jika sudah taking atau sudah join
        self.course_name = course_name
        self.sks = sks
        self.lecturer = lecturer
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel(course_name)
        self.name_label.setObjectName("courseCardTitle")
        header_layout.addWidget(self.name_label)
        
        header_layout.addStretch()
        
        sks_label = QLabel(f"{sks} SKS")
        sks_label.setObjectName("courseCardSKS")
        header_layout.addWidget(sks_label)
        
        layout.addLayout(header_layout)
        
        # Lecturer
        lecturer_label = QLabel(f"👨‍🏫 {lecturer}")
        lecturer_label.setObjectName("courseCardLecturer")
        layout.addWidget(lecturer_label)
        
        # Status badge
        if is_taking:
            status_badge = QLabel("● Sedang Diambil")
            status_badge.setObjectName("badgeTaking")
        else:
            status_badge = QLabel("○ Belum Diambil")
            status_badge.setObjectName("badgeNotTaking")
        
        status_badge.setAlignment(Qt.AlignRight)
        layout.addWidget(status_badge)
        
    def mousePressEvent(self, event):
        if hasattr(self, 'click_callback'):
            self.click_callback()
        super().mousePressEvent(event)
    
    def set_click_callback(self, callback):
        self.click_callback = callback


class TugasCard(QFrame):
    def __init__(self, tugas_name, matkul_name, deadline, status, priority, parent=None):
        super().__init__(parent)
        self.setObjectName("tugasCard")
        self.is_expanded = False
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(0)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Expand button
        self.expand_btn = QPushButton("▶")
        self.expand_btn.setObjectName("expandBtn")
        self.expand_btn.setFixedSize(24, 24)
        self.expand_btn.setCursor(Qt.PointingHandCursor)
        self.expand_btn.clicked.connect(self.toggle_expand)
        header_layout.addWidget(self.expand_btn)
        
        # Tugas 
        name_label = QLabel(tugas_name)
        name_label.setObjectName("tugasCardTitle")
        header_layout.addWidget(name_label, 2)
        
        # Matkul
        matkul_label = QLabel(matkul_name)
        matkul_label.setObjectName("tugasCardMatkul")
        header_layout.addWidget(matkul_label, 1)
        
        # Deadline
        deadline_label = QLabel(f"📅 {deadline}")
        deadline_label.setObjectName("tugasCardDeadline")
        header_layout.addWidget(deadline_label, 1)
        
        # Priority badge
        priority_colors = {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"}
        priority_badge = QLabel(priority)
        priority_badge.setObjectName("priorityBadge")
        priority_badge.setStyleSheet(f"background-color: {priority_colors.get(priority, '#95a5a6')}; color: white; border-radius: 20px; padding: 4px 12px; font-size: 11px; font-weight: 600;")
        priority_badge.setAlignment(Qt.AlignCenter)
        priority_badge.setFixedWidth(70)
        header_layout.addWidget(priority_badge)
        
        # Status badge
        status_colors = {
            "Pending": "#f39c12", "Not Started": "#e74c3c", 
            "Doing": "#3498db", "Done": "#2ecc71"
        }
        status_badge = QLabel(status)
        status_badge.setObjectName("statusBadge")
        status_badge.setStyleSheet(f"background-color: {status_colors.get(status, '#95a5a6')}; color: white; border-radius: 20px; padding: 4px 12px; font-size: 11px; font-weight: 600;")
        status_badge.setAlignment(Qt.AlignCenter)
        status_badge.setFixedWidth(100)
        header_layout.addWidget(status_badge)
        
        layout.addLayout(header_layout)
        
        # Expanded content
        self.expand_content = QWidget()
        self.expand_content.setVisible(False)
        expand_layout = QVBoxLayout(self.expand_content)
        expand_layout.setContentsMargins(40, 10, 10, 10)
        expand_layout.setSpacing(8)
        
        # Deskripsi
        desc_label = QLabel(f"📝 Deskripsi: {self._get_description(tugas_name)}")
        desc_label.setObjectName("tugasCardDesc")
        desc_label.setWordWrap(True)
        expand_layout.addWidget(desc_label)
        
        # Waktu deadline detail
        time_label = QLabel(f"⏰ Tenggat: {deadline} 23:59 WIB")
        time_label.setObjectName("tugasCardDetail")
        expand_layout.addWidget(time_label)
        
        layout.addWidget(self.expand_content)
        
        # Store data
        self.tugas_name = tugas_name
        self.deadline = deadline
        self.priority = priority
        self.status = status
    
    def _get_description(self, tugas_name):
        if "Tugas" in tugas_name:
            return "Mengerjakan soal latihan dan mengumpulkan dalam bentuk PDF"
        elif "Quiz" in tugas_name:
            return "Mengerjakan quiz online melalui platform e-learning"
        elif "UTS" in tugas_name or "UAS" in tugas_name:
            return "Ujian tengah/akhir semester, bersifat online/offline"
        else:
            return "Tugas perkuliahan sesuai dengan instruksi dosen"
    
    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        self.expand_content.setVisible(self.is_expanded)
        self.expand_btn.setText("▼" if self.is_expanded else "▶")
        
        self.updateGeometry()
    
    def mousePressEvent(self, event):
        if hasattr(self, 'click_callback'):
            self.click_callback()
        super().mousePressEvent(event)
    
    def set_click_callback(self, callback):
        self.click_callback = callback