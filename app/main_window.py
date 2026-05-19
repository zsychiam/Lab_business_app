from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QRadioButton, QButtonGroup, QPushButton, QTableWidget,
    QHeaderView, QMessageBox, QGroupBox, QStatusBar,
    QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor

from database import Database
from record_dialog import RecordDialog
from table_items import (
    make_text_item, make_int_item,
    make_decimal_item, make_date_item
)

STYLESHEET = """
QWidget {
    color: #111111;
    font-family: Arial;
}

QMainWindow { background-color: #f0f2f5; }

QLabel#headerLabel {
    background-color: #1e3a5f;
    color: white;
    font-size: 15px;
    font-weight: bold;
    padding: 14px 20px;
}
QLabel#authorLabel {
    color: #4a7abf;
    font-size: 12px;
    padding: 4px 20px;
    background-color: #f0f2f5;
}

QGroupBox {
    font-weight: bold;
    font-size: 12px;
    border: 1px solid #c8cdd6;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 6px;
    background-color: white;
    color: #111111;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #1e3a5f;
}

QTableWidget {
    background-color: white;
    alternate-background-color: #f5f7fa;
    gridline-color: #e0e4ea;
    font-size: 12px;
    border: 1px solid #c8cdd6;
    border-radius: 4px;
    outline: none;
    color: #111111;
}
QTableWidget::item {
    padding: 4px 8px;
    color: #111111;
    background-color: transparent;
}
QTableWidget::item:alternate {
    background-color: #f5f7fa;
    color: #111111;
}
QTableWidget::item:selected {
    background-color: #1e3a5f;
    color: white;
}
QTableWidget::item:selected:alternate {
    background-color: #1e3a5f;
    color: white;
}

QHeaderView::section {
    background-color: #1e3a5f;
    color: white;
    padding: 7px 8px;
    border: none;
    font-size: 12px;
    font-weight: bold;
}
QHeaderView::section:hover { background-color: #2a4e7c; }

QPushButton {
    background-color: #1e3a5f;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 18px;
    font-size: 13px;
    min-width: 110px;
}
QPushButton:hover    { background-color: #2a5080; color: white; }
QPushButton:pressed  { background-color: #14293f; color: white; }
QPushButton:disabled { background-color: #888888; color: #dddddd; border: 1px solid #777777; }
QPushButton#viewBtn  { background-color: #2e7d52; color: white; }
QPushButton#viewBtn:hover  { background-color: #3a9868; color: white; }
QPushButton#viewBtn:disabled { background-color: #888888; color: #dddddd; border: 1px solid #777777; }
QPushButton#deleteBtn { background-color: #b03a2e; color: white; }
QPushButton#deleteBtn:hover { background-color: #c0392b; color: white; }
QPushButton#deleteBtn:disabled { background-color: #888888; color: #dddddd; border: 1px solid #777777; }

QComboBox {
    border: 1px solid #c8cdd6;
    border-radius: 5px;
    padding: 6px 12px;
    font-size: 13px;
    background-color: white;
    color: #111111;
    min-height: 32px;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background-color: white;
    color: #111111;
    border: 1px solid #c8cdd6;
    selection-background-color: #1e3a5f;
    selection-color: white;
    outline: none;
    padding: 2px;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 4px 8px;
    color: #111111;
    background-color: white;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #1e3a5f;
    color: white;
}

QStatusBar { font-size: 12px; color: #555; background-color: #f0f2f5; }
"""

COUNTRY_COLUMNS = [
    ('id',                'id',                'int',     True),
    ('Название',          'name',              'text',    False),
    ('Континент',         'continent',         'text',    False),
    ('Население (чел.)',  'population',        'int',     False),
    ('Площадь (км²)',     'area',              'decimal', False),
    ('День независимости','independence_date', 'date',    False),
    ('Примечания',        'notes',             'text',    False),
]

CITY_COLUMNS = [
    ('id',               'id',           'int',     True),
    ('Название',         'name',         'text',    False),
    ('country_id',       'country_id',   'int',     True),
    ('Страна',           'country_name', 'text',    False),
    ('Описание',         'description',  'text',    False),
    ('Население (чел.)', 'population',   'int',     False),
    ('Площадь (км²)',    'area',         'decimal', False),
    ('Дата основания',   'founded_date', 'date',    False),
]

DICTS = {
    'Страны': ('countries', COUNTRY_COLUMNS),
    'Города': ('cities',    CITY_COLUMNS),
}


class MainWindow(QMainWindow):

    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        self.setWindowTitle("Справочники и БД")
        self.resize(1100, 680)
        self.setMinimumSize(QSize(800, 500))
        self.setStyleSheet(STYLESHEET)
        self._build_ui()
        self._on_dict_changed(0)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Справочники и БД")
        header.setObjectName("headerLabel")
        root.addWidget(header)

        author = QLabel("Годов Артём  |  3 курс, 2 группа  |  2026 г.")
        author.setObjectName("authorLabel")
        root.addWidget(author)

        content = QWidget()
        content.setStyleSheet("background-color: #f0f2f5;")
        cl = QVBoxLayout(content)
        cl.setSpacing(10)
        cl.setContentsMargins(16, 12, 16, 12)
        root.addWidget(content)

        # Выбор справочника
        dict_group = QGroupBox("Выбор справочника")
        dict_lay = QHBoxLayout(dict_group)
        dict_lay.setContentsMargins(12, 8, 12, 8)

        self._radio_group = QButtonGroup(self)
        for i, name in enumerate(DICTS):
            rb = QRadioButton(name)
            rb.setStyleSheet("QRadioButton { color: #111111; font-size: 13px; spacing: 6px; }")
            if i == 0:
                rb.setChecked(True)
            self._radio_group.addButton(rb, i)
            dict_lay.addWidget(rb)
        self._radio_group.idClicked.connect(self._on_dict_changed)
        dict_lay.addStretch()

        self.record_count_label = QLabel("Записей: 0")
        self.record_count_label.setStyleSheet("color: #666; font-size: 12px;")
        dict_lay.addWidget(self.record_count_label)
        cl.addWidget(dict_group)

        # Таблица
        table_group = QGroupBox("Данные справочника")
        table_lay = QVBoxLayout(table_group)
        table_lay.setContentsMargins(8, 6, 8, 8)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionsClickable(True)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_view)
        self.table.itemSelectionChanged.connect(self._update_buttons)
        table_lay.addWidget(self.table)
        cl.addWidget(table_group)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.add_btn  = QPushButton("➕  Добавить")
        self.edit_btn = QPushButton("✏  Редактировать")
        self.view_btn = QPushButton("👁  Просмотреть")
        self.del_btn  = QPushButton("🗑  Удалить")

        self.view_btn.setObjectName("viewBtn")
        self.del_btn.setObjectName("deleteBtn")

        self.add_btn.clicked.connect(self._on_add)
        self.edit_btn.clicked.connect(self._on_edit)
        self.view_btn.clicked.connect(self._on_view)
        self.del_btn.clicked.connect(self._on_delete)

        self._style_btn(self.add_btn,  '#1e3a5f')
        self._style_btn(self.edit_btn, '#1e3a5f')
        self._style_btn(self.view_btn, '#2e7d52')
        self._style_btn(self.del_btn,  '#b03a2e')

        for btn in (self.add_btn, self.edit_btn, self.view_btn, self.del_btn):
            btn_layout.addWidget(btn)
        btn_layout.addStretch()
        cl.addLayout(btn_layout)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Готово")
        self._update_buttons()

    def _style_btn(self, btn, hex_color: str) -> None:
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        btn.setAutoFillBackground(True)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {hex_color}; color: white; "
            f"border: none; border-radius: 5px; padding: 8px 18px; "
            f"font-size: 13px; min-width: 110px; }}"
            f"QPushButton:hover {{ background-color: rgba({r+30},{g+30},{b+30},255); color: white; }}"
            f"QPushButton:pressed {{ background-color: rgba({max(r-30,0)},{max(g-30,0)},{max(b-30,0)},255); color: white; }}"
        )

    def _update_buttons(self) -> None:
        pass  # кнопки всегда активны

    def _on_dict_changed(self, _=None) -> None:
        self._refresh()

    def _current_dict_name(self) -> str:
        checked = self._radio_group.checkedButton()
        return checked.text() if checked else list(DICTS.keys())[0]

    def _refresh(self) -> None:
        dict_name = self._current_dict_name()
        dict_type, columns = DICTS[dict_name]
        try:
            records = (self.db.get_all_countries() if dict_type == 'countries'
                       else self.db.get_all_cities())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{e}")
            return

        self.table.setSortingEnabled(False)
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([c[0] for c in columns])
        self.table.setRowCount(len(records))

        for ci, col in enumerate(columns):
            if col[3]:
                self.table.hideColumn(ci)
            else:
                self.table.showColumn(ci)

        for row, rec in enumerate(records):
            for ci, (_, key, dtype, _h) in enumerate(columns):
                val = rec.get(key)
                if dtype == 'int':
                    item = make_int_item(val)
                elif dtype == 'decimal':
                    item = make_decimal_item(val)
                elif dtype == 'date':
                    item = make_date_item(val)
                else:
                    item = make_text_item(val)
                # Явно задаём цвет текста для надёжности
                item.setForeground(Qt.GlobalColor.black)
                self.table.setItem(row, ci, item)

        header = self.table.horizontalHeader()
        for ci, col in enumerate(columns):
            if not col[3]:
                if col[2] == 'text':
                    header.setSectionResizeMode(ci, QHeaderView.ResizeMode.Stretch)
                else:
                    header.setSectionResizeMode(ci, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSortingEnabled(True)
        self.record_count_label.setText(f"Записей: {len(records)}")
        self.status.showMessage(f"Справочник \u00ab{dict_name}\u00bb: {len(records)} записей")
        self._update_buttons()

    def _selected_record_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _get_record(self, dict_type, record_id):
        try:
            return (self.db.get_country_by_id(record_id) if dict_type == 'countries'
                    else self.db.get_city_by_id(record_id))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return None

    def _current_dict_type(self):
        return DICTS[self._current_dict_name()][0]

    def _on_add(self) -> None:
        dt = self._current_dict_type()
        dlg = RecordDialog(self.db, dt, mode='add', parent=self)
        if dlg.exec():
            d = dlg.get_data()
            try:
                if dt == 'countries':
                    self.db.create_country(d['name'], d['continent'], d['population'],
                                           d['area'], d['independence_date'], d['notes'])
                else:
                    self.db.create_city(d['name'], d['country_id'], d['description'],
                                        d['population'], d['area'], d['founded_date'])
                self._refresh()
                self.status.showMessage("Запись добавлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def _on_edit(self) -> None:
        rid = self._selected_record_id()
        if rid is None: return
        dt = self._current_dict_type()
        rec = self._get_record(dt, rid)
        if not rec: return
        dlg = RecordDialog(self.db, dt, mode='edit', record=rec, parent=self)
        if dlg.exec():
            d = dlg.get_data()
            try:
                if dt == 'countries':
                    self.db.update_country(rid, d['name'], d['continent'], d['population'],
                                           d['area'], d['independence_date'], d['notes'])
                else:
                    self.db.update_city(rid, d['name'], d['country_id'], d['description'],
                                        d['population'], d['area'], d['founded_date'])
                self._refresh()
                self.status.showMessage("Запись обновлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def _on_view(self) -> None:
        rid = self._selected_record_id()
        if rid is None: return
        dt = self._current_dict_type()
        rec = self._get_record(dt, rid)
        if not rec: return
        RecordDialog(self.db, dt, mode='view', record=rec, parent=self).exec()

    def _on_delete(self) -> None:
        rid = self._selected_record_id()
        if rid is None: return
        dt = self._current_dict_type()
        name_item = self.table.item(self.table.currentRow(), 1)
        name = name_item.text() if name_item else str(rid)

        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение")
        msg.setText(f"Удалить запись «{name}»?\n\nДанные физически останутся в базе (мягкое удаление).")
        msg.setIcon(QMessageBox.Icon.Question)
        yes_btn = msg.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        msg.setDefaultButton(no_btn)
        msg.exec()

        if msg.clickedButton() != yes_btn: return

        try:
            if dt == 'countries':
                self.db.delete_country(rid)
            else:
                self.db.delete_city(rid)
            self._refresh()
            self.status.showMessage(f"Запись «{name}» удалена")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
