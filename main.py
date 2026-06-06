import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from ui.auth.auth_window import AuthWindow
except ModuleNotFoundError:
    try:
        from ui.auth.auth_window import AuthWindow
    except ModuleNotFoundError as e:
        print(f"[CRITICAL] auth_window.py tidak ditemukan: {e}")
        sys.exit(1)


def load_stylesheet(app):
    paths = [
        os.path.join(BASE_DIR, "ui", "style.qss"),
        os.path.join(BASE_DIR, "ui", "auth", "style.qss"),
        os.path.join(BASE_DIR, "style.qss"),
    ]
    
    target_qss = None
    for path in paths:
        if os.path.exists(path):
            target_qss = path
            break

    if target_qss:
        try:
            with open(target_qss, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            print(f"[SUKSES] QSS dimuat dari: {target_qss}")
        except Exception as e:
            print(f"[ERROR] Gagal membaca QSS: {e}")
    else:
        print("[GAGAL] style.qss tidak ditemukan")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    load_stylesheet(app)

    # Buat window auth terlebih dahulu
    auth_window = AuthWindow()
    
    # Definisikan callback setelah window dibuat
    def on_login_success(user_data):
        print(f"[LOGIN] {user_data.get('nama')} - {user_data.get('role')}")
        
        # Tutup window auth
        auth_window.close()
        
        # Buka main window berdasarkan role
        if user_data.get('role') == 'mahasiswa':
            try:
                from ui.mahasiswa.main_window import MahasiswaMainWindow
                main_window = MahasiswaMainWindow(user_data)
                main_window.show()
                print("[INFO] Dashboard mahasiswa ditampilkan")
            except ImportError as e:
                print(f"[ERROR] Gagal import MahasiswaMainWindow: {e}")
                QMessageBox.critical(None, "Error", "Gagal memuat dashboard mahasiswa.")
                sys.exit(1)
        else:
            # Role dosen (untuk pengembangan berikutnya)
            QMessageBox.information(
                None, 
                "Info", 
                f"Selamat datang Dosen {user_data.get('nama')}!\n"
                "Fitur untuk dosen sedang dalam pengembangan."
            )
            sys.exit(0)
    
    # Set callback
    auth_window.on_login_success = on_login_success
    
    # Tampilkan window auth
    auth_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()