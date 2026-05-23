import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from ui.auth.auth_window import AuthWindow
except ModuleNotFoundError:
    try:
        from ui.auth_window import AuthWindow
    except ModuleNotFoundError as e:
        print(f"[CRITICAL] auth_window.py tidak ditemukan: {e}")
        sys.exit(1)


def load_stylesheet(app):
    """Mencari dan menerapkan file style.qss secara global."""
    path_a = os.path.join(BASE_DIR, "ui", "style.qss")
    path_b = os.path.join(BASE_DIR, "ui", "auth", "style.qss")
    
    target_qss = path_a if os.path.exists(path_a) else (path_b if os.path.exists(path_b) else None)

    if target_qss:
        try:
            with open(target_qss, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            print(f"[SUKSES] QSS dimuat dari: {target_qss}")
        except Exception as e:
            print(f"[ERROR] Gagal membaca QSS: {e}")
    else:
        print("[GAGAL] style.qss tidak ditemukan di folder ui/ maupun ui/auth/")
        QMessageBox.warning(None, "Style Hilang", "Aplikasi berjalan tanpa tema pastel.")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    load_stylesheet(app)

    window = AuthWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()