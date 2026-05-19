from __future__ import annotations
import datetime
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

class SortableItem(QTableWidgetItem):
    def __init__(self, display_text, sort_value=None):
        super().__init__(display_text)
        self._sort_value = sort_value if sort_value is not None else display_text
        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def __lt__(self, other):
        my = self._sort_value
        ot = other._sort_value if isinstance(other, SortableItem) else other.text()
        if my is None: return True
        if ot is None: return False
        try: return my < ot
        except TypeError: return str(my) < str(ot)

def make_text_item(v):
    t = str(v) if v is not None else ""
    return SortableItem(t, t.lower())

def make_int_item(v):
    if v is None: return SortableItem("", None)
    formatted = f"{int(v):,}".replace(",", "\u2009")
    return SortableItem(formatted, int(v))

def make_decimal_item(v):
    if v is None: return SortableItem("", None)
    fv = float(v)
    ip, fp = f"{fv:.2f}".split(".")
    return SortableItem(f"{int(ip):,}".replace(",", "\u2009") + "." + fp, fv)

def make_date_item(v):
    if v is None: return SortableItem("", None)
    if isinstance(v, datetime.date):
        return SortableItem(v.strftime("%d.%m.%Y"), v)
    return SortableItem(str(v), v)
