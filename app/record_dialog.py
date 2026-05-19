from __future__ import annotations
import datetime
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QDateEdit, QCheckBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

FORM_STYLE = """
QDialog { background-color: #f8f9fb; }
QLabel { color: #111111; font-size: 12px; }
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
    border: 1px solid #c8cdd6;
    border-radius: 4px;
    padding: 5px 8px;
    background-color: white;
    color: #111111;
    font-size: 12px;
}
QLineEdit:read-only, QTextEdit:read-only {
    background-color: #f0f2f5;
    color: #444444;
}
QComboBox {
    border: 1px solid #c8cdd6;
    border-radius: 4px;
    padding: 5px 8px;
    background-color: white;
    color: #111111;
    font-size: 12px;
}
QComboBox QAbstractItemView {
    background-color: white;
    color: #111111;
    selection-background-color: #1e3a5f;
    selection-color: white;
}
QCheckBox { color: #111111; font-size: 12px; }
QPushButton {
    background-color: #1e3a5f; color: white;
    border: none; border-radius: 4px;
    padding: 7px 16px; font-size: 13px;
}
QPushButton:hover { background-color: #2a5080; }
"""

def _sep():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("color: #dde1e8; margin: 4px 0;"); return f

def _bold_label(text):
    l = QLabel(text); f = QFont(); f.setBold(True); l.setFont(f)
    l.setStyleSheet("color: #1e3a5f; margin-top:4px;"); return l


class RecordDialog(QDialog):
    def __init__(self, db, dict_type, mode='add', record=None, parent=None):
        super().__init__(parent)
        self.db = db; self.dict_type = dict_type
        self.mode = mode; self.record = record or {}
        titles = {'add': 'Добавление записи', 'edit': 'Редактирование записи', 'view': 'Просмотр записи'}
        self.setWindowTitle(titles.get(mode, 'Запись'))
        self.setMinimumWidth(520); self.setModal(True)
        self.setStyleSheet(FORM_STYLE)
        self._build_ui()
        if self.record: self._populate()
        if mode == 'view': self._set_readonly()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(4); root.setContentsMargins(16,16,16,16)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(8); form.setContentsMargins(0,0,0,0)
        (self._build_countries if self.dict_type == 'countries' else self._build_cities)(form)
        root.addLayout(form); root.addSpacing(8); root.addWidget(_sep())
        if self.mode == 'view':
            btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            btns.rejected.connect(self.reject)
        else:
            btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            btns.accepted.connect(self._on_accept); btns.rejected.connect(self.reject)
            btns.button(QDialogButtonBox.StandardButton.Ok).setText("Сохранить")
            btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        root.addWidget(btns)

    def _build_countries(self, form):
        self.name_edit = QLineEdit(); self.name_edit.setMaxLength(200)
        self.name_edit.setPlaceholderText("Введите название страны")
        form.addRow("Название *:", self.name_edit)

        self.continent_edit = QLineEdit(); self.continent_edit.setMaxLength(100)
        self.continent_edit.setPlaceholderText("Например: Европа")
        form.addRow("Континент *:", self.continent_edit)

        form.addRow(_sep()); form.addRow(_bold_label("Численные данные"))

        self.population_spin = QSpinBox()
        self.population_spin.setRange(0, 2_000_000_000)
        self.population_spin.setSpecialValueText("Не указано")
        self.population_spin.setSuffix(" чел."); self.population_spin.setGroupSeparatorShown(True)
        form.addRow("Население:", self.population_spin)

        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.0, 20_000_000.0); self.area_spin.setDecimals(2)
        self.area_spin.setSpecialValueText("Не указано")
        self.area_spin.setSuffix(" км²"); self.area_spin.setGroupSeparatorShown(True)
        form.addRow("Площадь:", self.area_spin)

        form.addRow(_sep()); form.addRow(_bold_label("Дата и примечания"))

        dr = QHBoxLayout()
        self.date_check = QCheckBox("Дата известна")
        self.indep_date_edit = QDateEdit()
        self.indep_date_edit.setCalendarPopup(True)
        self.indep_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.indep_date_edit.setDate(QDate.currentDate())
        self.indep_date_edit.setEnabled(False)
        self.date_check.toggled.connect(self.indep_date_edit.setEnabled)
        dr.addWidget(self.date_check); dr.addWidget(self.indep_date_edit); dr.addStretch()
        form.addRow("День независимости:", dr)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Краткое описание страны…")
        self.notes_edit.setMinimumHeight(90); self.notes_edit.setMaximumHeight(140)
        form.addRow("Примечания:", self.notes_edit)

    def _build_cities(self, form):
        self.name_edit = QLineEdit(); self.name_edit.setMaxLength(200)
        self.name_edit.setPlaceholderText("Введите название города")
        form.addRow("Название *:", self.name_edit)

        self.country_combo = QComboBox(); self.country_combo.setMinimumWidth(280)
        self._fill_countries_combo()
        form.addRow("Страна *:", self.country_combo)

        form.addRow(_sep()); form.addRow(_bold_label("Описание"))

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Описание города…")
        self.description_edit.setMinimumHeight(90); self.description_edit.setMaximumHeight(140)
        form.addRow("Описание:", self.description_edit)

        form.addRow(_sep()); form.addRow(_bold_label("Численные данные"))

        self.population_spin = QSpinBox()
        self.population_spin.setRange(0, 100_000_000)
        self.population_spin.setSpecialValueText("Не указано")
        self.population_spin.setSuffix(" чел."); self.population_spin.setGroupSeparatorShown(True)
        form.addRow("Население:", self.population_spin)

        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.0, 50_000.0); self.area_spin.setDecimals(2)
        self.area_spin.setSpecialValueText("Не указано")
        self.area_spin.setSuffix(" км²"); self.area_spin.setGroupSeparatorShown(True)
        form.addRow("Площадь:", self.area_spin)

        form.addRow(_sep()); form.addRow(_bold_label("Дата основания"))

        dr = QHBoxLayout()
        self.date_check = QCheckBox("Дата известна")
        self.founded_date_edit = QDateEdit()
        self.founded_date_edit.setCalendarPopup(True)
        self.founded_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.founded_date_edit.setDate(QDate.currentDate())
        self.founded_date_edit.setMinimumDate(QDate(1, 1, 1))
        self.founded_date_edit.setEnabled(False)
        self.date_check.toggled.connect(self.founded_date_edit.setEnabled)
        dr.addWidget(self.date_check); dr.addWidget(self.founded_date_edit); dr.addStretch()
        form.addRow("Дата основания:", dr)

    def _fill_countries_combo(self):
        self.country_combo.clear()
        self.country_combo.addItem("— Выберите страну —", None)
        try:
            for c in self.db.get_countries_for_dropdown():
                self.country_combo.addItem(c['name'], c['id'])
        except: pass

    def _populate(self):
        r = self.record
        self.name_edit.setText(r.get('name') or "")
        if self.dict_type == 'countries':
            self.continent_edit.setText(r.get('continent') or "")
            self.population_spin.setValue(r.get('population') or 0)
            self.area_spin.setValue(float(r.get('area') or 0.0))
            d = r.get('independence_date')
            if d:
                self.date_check.setChecked(True)
                qd = QDate(d.year, d.month, d.day) if isinstance(d, datetime.date) else QDate.fromString(str(d), Qt.DateFormat.ISODate)
                self.indep_date_edit.setDate(qd)
            self.notes_edit.setPlainText(r.get('notes') or "")
        else:
            self.description_edit.setPlainText(r.get('description') or "")
            self.population_spin.setValue(r.get('population') or 0)
            self.area_spin.setValue(float(r.get('area') or 0.0))
            d = r.get('founded_date')
            if d:
                self.date_check.setChecked(True)
                qd = QDate(d.year, d.month, d.day) if isinstance(d, datetime.date) else QDate.fromString(str(d), Qt.DateFormat.ISODate)
                self.founded_date_edit.setDate(qd)
            cid = r.get('country_id')
            if cid is not None:
                for i in range(self.country_combo.count()):
                    if self.country_combo.itemData(i) == cid:
                        self.country_combo.setCurrentIndex(i); break

    def _set_readonly(self):
        self.name_edit.setReadOnly(True)
        if self.dict_type == 'countries':
            self.continent_edit.setReadOnly(True)
            self.notes_edit.setReadOnly(True)
        else:
            self.description_edit.setReadOnly(True)
            self.country_combo.setEnabled(False)
        self.population_spin.setReadOnly(True)
        self.area_spin.setReadOnly(True)
        self.date_check.setEnabled(False)
        (self.indep_date_edit if self.dict_type == 'countries' else self.founded_date_edit).setReadOnly(True)

    def _on_accept(self):
        errs = []
        if not self.name_edit.text().strip():
            errs.append("Поле «Название» обязательно.")
        if self.dict_type == 'countries':
            if not self.continent_edit.text().strip():
                errs.append("Поле «Континент» обязательно.")
        else:
            if self.country_combo.currentData() is None:
                errs.append("Необходимо выбрать страну.")
        if errs:
            QMessageBox.warning(self, "Ошибка", "\n".join(f"• {e}" for e in errs)); return
        self.accept()

    def get_data(self):
        data = {'name': self.name_edit.text().strip()}
        p = self.population_spin.value(); data['population'] = p if p > 0 else None
        a = self.area_spin.value(); data['area'] = a if a > 0.0 else None
        if self.dict_type == 'countries':
            data['continent'] = self.continent_edit.text().strip()
            if self.date_check.isChecked():
                qd = self.indep_date_edit.date()
                data['independence_date'] = datetime.date(qd.year(), qd.month(), qd.day())
            else:
                data['independence_date'] = None
            data['notes'] = self.notes_edit.toPlainText().strip() or None
        else:
            data['country_id'] = self.country_combo.currentData()
            if self.date_check.isChecked():
                qd = self.founded_date_edit.date()
                data['founded_date'] = datetime.date(qd.year(), qd.month(), qd.day())
            else:
                data['founded_date'] = None
            data['description'] = self.description_edit.toPlainText().strip() or None
        return data
