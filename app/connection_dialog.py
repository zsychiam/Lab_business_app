from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLabel, QLineEdit,
    QSpinBox, QPushButton, QDialogButtonBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config import load_config, save_config
from database import Database

STYLE = """
QDialog { background-color: #f8f9fb; }
QLabel { color: #111111; font-size: 12px; }
QLineEdit, QSpinBox {
    border: 1px solid #c8cdd6; border-radius: 4px;
    padding: 5px 8px; background: white; color: #111111; font-size: 12px;
}
QPushButton { background-color: #1e3a5f; color: white; border: none;
    border-radius: 4px; padding: 7px 16px; font-size: 13px; }
QPushButton:hover { background-color: #2a5080; }
"""

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подключение к базе данных")
        self.setMinimumWidth(380); self.setModal(True)
        self._db = None; self.setStyleSheet(STYLE)
        self._build_ui(); self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(10); root.setContentsMargins(20,20,20,20)

        t = QLabel("Параметры подключения PostgreSQL")
        f = QFont(); f.setBold(True); f.setPointSize(12); t.setFont(f)
        t.setStyleSheet("color: #1e3a5f;"); root.addWidget(t)

        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #c0c4cc;"); root.addWidget(line)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight); form.setSpacing(8)

        self.host = QLineEdit(); self.host.setPlaceholderText("localhost")
        form.addRow("Хост:", self.host)
        self.port = QSpinBox(); self.port.setRange(1, 65535); self.port.setValue(5432)
        form.addRow("Порт:", self.port)
        self.dbname = QLineEdit(); self.dbname.setPlaceholderText("directory_db")
        form.addRow("База данных:", self.dbname)
        self.user = QLineEdit(); self.user.setPlaceholderText("postgres")
        form.addRow("Пользователь:", self.user)
        self.pwd = QLineEdit(); self.pwd.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Пароль:", self.pwd)
        root.addLayout(form)

        self.test_btn = QPushButton("Проверить соединение")
        self.test_btn.clicked.connect(self._test); root.addWidget(self.test_btn)

        self.status = QLabel(""); self.status.setWordWrap(True); root.addWidget(self.status)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Подключиться")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        btns.accepted.connect(self._connect); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _load(self):
        c = load_config()
        self.host.setText(c.get('host','localhost')); self.port.setValue(c.get('port',5432))
        self.dbname.setText(c.get('dbname','directory_db')); self.user.setText(c.get('user','postgres'))
        self.pwd.setText(c.get('password',''))

    def _params(self):
        return {'host': self.host.text().strip() or 'localhost', 'port': self.port.value(),
                'dbname': self.dbname.text().strip() or 'directory_db',
                'user': self.user.text().strip() or 'postgres', 'password': self.pwd.text()}

    def _test(self):
        db = Database()
        try:
            db.connect(**self._params()); db.disconnect()
            self.status.setText('<span style="color:green;">✔ Соединение успешно.</span>')
        except Exception as e:
            self.status.setText(f'<span style="color:red;">✘ {e}</span>')

    def _connect(self):
        p = self._params(); db = Database()
        try:
            db.connect(**p); self._db = db; save_config(p); self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения", str(e))

    def get_database(self): return self._db
