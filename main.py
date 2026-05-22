import sys
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)

label = QLabel("PySide6 Jalan 🚀")
label.resize(300, 100)
label.show()

sys.exit(app.exec())