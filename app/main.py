import sys
from PyQt6.QtWidgets import QApplication, QDialog, QStyleFactory
from connection_dialog import ConnectionDialog
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setApplicationName("Модуль справочников")
    dlg = ConnectionDialog()
    if dlg.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow(dlg.get_database())
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
