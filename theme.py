"""
theme.py - ONE design system for every CRM window.

Dark navy surfaces + a single cyan accent (same family as the login screen),
amber for admin-only things, red for destructive actions. Every window calls
apply_theme(self) and builds its UI with the helpers below, so colours,
corners, spacing, buttons and tables look identical everywhere.

To re-brand the whole app, change the PALETTE values only.
"""

import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QTableWidgetItem, QVBoxLayout, QWidget,
)

PALETTE = {
    "bg": "#0b1220",            # window
    "bg2": "#111c33",           # window gradient end
    "surface": "#131c2e",       # cards
    "surface_alt": "#162136",   # zebra rows
    "surface2": "#1b2740",      # inputs / raised
    "border": "#26344f",
    "text": "#e6edf7",
    "muted": "#8b9bb4",
    "accent": "#22d3ee",
    "accent_hover": "#67e8f9",
    "accent_press": "#06b6d4",
    "accent_text": "#04222b",
    "accent_dim": "rgba(34, 211, 238, 0.16)",
    "danger": "#f87171",
    "danger_dim": "rgba(248, 113, 113, 0.14)",
    "success": "#34d399",
    "warning": "#fbbf24",
    "warning_dim": "rgba(251, 191, 36, 0.14)",
}

_QSS = """
QWidget#Window {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 @bg, stop:1 @bg2);
}
QWidget {
    color: @text;
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}
QLabel { background: transparent; }
QLabel#title    { font-size: 24px; font-weight: 700; }
QLabel#subtitle { color: @muted; font-size: 13px; }
QLabel#tileTitle { font-size: 15px; font-weight: 600; }
QLabel#tileDesc  { color: @muted; font-size: 12px; }
QLabel#pill {
    background: @accent_dim; color: @accent; font-size: 11px; font-weight: 700;
    border: 1px solid transparent; border-radius: 11px; padding: 4px 12px;
}
QLabel#pill[admin="true"] { background: @warning_dim; color: @warning; }
QLabel#status { color: @muted; font-size: 12px; }
QLabel#status[error="true"] { color: @danger; }

QFrame#card {
    background: @surface; border: 1px solid @border; border-radius: 14px;
}

QLineEdit, QComboBox {
    background: @bg; border: 1px solid @border; border-radius: 10px;
    padding: 10px 14px; min-height: 20px;
    selection-background-color: @accent; selection-color: @accent_text;
}
QLineEdit:hover, QComboBox:hover { border-color: @muted; }
QLineEdit:focus, QComboBox:focus { border: 1px solid @accent; }
QComboBox::drop-down { border: none; width: 30px; }
QComboBox QAbstractItemView {
    background: @surface; border: 1px solid @border; outline: 0; padding: 4px;
    selection-background-color: @accent_dim; selection-color: @text;
}

QPushButton {
    background: @accent; color: @accent_text; border: none; border-radius: 10px;
    padding: 10px 20px; font-weight: 600;
}
QPushButton:hover    { background: @accent_hover; }
QPushButton:pressed  { background: @accent_press; }
QPushButton:disabled { background: @surface2; color: @muted; }

QPushButton[variant="secondary"] {
    background: @surface2; color: @text; border: 1px solid @border;
}
QPushButton[variant="secondary"]:hover   { border-color: @accent; color: @accent; }
QPushButton[variant="secondary"]:pressed { background: @border; }

QPushButton[variant="danger"] {
    background: transparent; color: @danger; border: 1px solid @danger_dim;
}
QPushButton[variant="danger"]:hover   { background: @danger_dim; border-color: @danger; }
QPushButton[variant="danger"]:pressed { background: @danger_dim; }

QPushButton[variant="ghost"] { background: transparent; color: @muted; }
QPushButton[variant="ghost"]:hover { background: @surface2; color: @text; }

QPushButton[variant="chip"] {
    background: @surface2; color: @muted; border: 1px solid @border;
    border-radius: 15px; padding: 7px 16px; font-size: 12px; font-weight: 600;
}
QPushButton[variant="chip"]:hover   { color: @text; border-color: @muted; }
QPushButton[variant="chip"]:checked {
    background: @accent_dim; color: @accent; border: 1px solid @accent;
}

QPushButton[variant="tile"], QPushButton[variant="tile-admin"] {
    background: @surface; color: @text; border: 1px solid @border;
    border-radius: 14px; padding: 0px; text-align: left; min-height: 74px;
}
QPushButton[variant="tile"]:hover       { background: @surface2; border-color: @accent; }
QPushButton[variant="tile-admin"]       { border-color: @warning_dim; background: @warning_dim; }
QPushButton[variant="tile-admin"]:hover { border-color: @warning; }
QPushButton[variant="tile"]:pressed, QPushButton[variant="tile-admin"]:pressed { background: @border; }

QTableWidget {
    background: @surface; alternate-background-color: @surface_alt;
    border: 1px solid @border; border-radius: 12px; outline: 0;
    selection-background-color: @accent_dim; selection-color: @text;
}
QTableWidget::item { padding: 4px 10px; border: none; }
QTableWidget::item:selected { background: @accent_dim; color: @text; }
QHeaderView { background: transparent; }
QHeaderView::section {
    background: @surface2; color: @muted; padding: 11px 12px; border: none;
    border-bottom: 1px solid @border; font-size: 11px; font-weight: 700;
}
QTableCornerButton::section { background: @surface2; border: none; }

QScrollBar:vertical { background: transparent; width: 12px; margin: 2px; }
QScrollBar::handle:vertical { background: @border; border-radius: 5px; min-height: 36px; }
QScrollBar::handle:vertical:hover { background: @muted; }
QScrollBar:horizontal { background: transparent; height: 12px; margin: 2px; }
QScrollBar::handle:horizontal { background: @border; border-radius: 5px; min-width: 36px; }
QScrollBar::handle:horizontal:hover { background: @muted; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QToolTip { background: @surface2; color: @text; border: 1px solid @border; padding: 6px 8px; }
QMessageBox, QDialog { background: @surface; }
QMessageBox QLabel { color: @text; }
"""

_LOGIN_QSS = """
QWidget#LoginWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 @bg, stop:1 @bg2);
}
QWidget { color: @text; font-family: "Segoe UI", "Inter", Arial, sans-serif; }
QLabel { background: transparent; }
QFrame#frmCard { background: @surface; border: 1px solid @border; border-radius: 20px; }
QLabel#lblLogo { font-size: 32px; font-weight: 800; letter-spacing: 4px; color: @text; }
QLabel#lblSubtitle { color: @muted; font-size: 12px; letter-spacing: 1px; }
QLabel#lblUser, QLabel#lblPass {
    color: @muted; font-size: 11px; font-weight: 700; letter-spacing: 1px;
}
QLineEdit {
    background: @bg; color: @text; border: 1px solid @border; border-radius: 12px;
    padding: 11px 14px; font-size: 13px; min-height: 22px;
    selection-background-color: @accent; selection-color: @accent_text;
}
QLineEdit:hover { border-color: @muted; }
QLineEdit:focus { border: 1px solid @accent; }
QCheckBox#chkShow { color: @muted; font-size: 12px; spacing: 8px; }
QCheckBox#chkShow::indicator {
    width: 16px; height: 16px; border-radius: 5px; border: 2px solid @border;
    background: transparent;
}
QCheckBox#chkShow::indicator:hover   { border-color: @accent; }
QCheckBox#chkShow::indicator:checked { background: @accent; border-color: @accent; }
QPushButton#btnLogin {
    background: @accent; color: @accent_text; border: none; border-radius: 12px;
    font-size: 14px; font-weight: 700; padding: 12px; min-height: 40px; letter-spacing: 1px;
}
QPushButton#btnLogin:hover    { background: @accent_hover; }
QPushButton#btnLogin:pressed  { background: @accent_press; }
QPushButton#btnLogin:disabled { background: @surface2; color: @muted; }
QPushButton#btnExit {
    background: transparent; color: @muted; border: 1px solid @border;
    border-radius: 12px; font-size: 13px; font-weight: 600; padding: 10px; min-height: 36px;
}
QPushButton#btnExit:hover { border-color: @danger; color: @danger; }
QLabel#lblForgot { color: @muted; font-size: 12px; }
"""


def _render(template):
    return re.sub(r"@(\w+)", lambda m: PALETTE[m.group(1)], template)


QSS = _render(_QSS)
LOGIN_QSS = _render(_LOGIN_QSS)


# --------------------------------------------------------------------- helpers
def apply_theme(widget):
    """Give a top-level window the CRM look."""
    widget.setObjectName("Window")
    widget.setStyleSheet(QSS)


def center(widget):
    """Centre a window on the screen it will open on."""
    screen = QApplication.primaryScreen()
    if screen:
        area = screen.availableGeometry()
        frame = widget.frameGeometry()
        frame.moveCenter(area.center())
        widget.move(frame.topLeft())


def make_button(text, variant="primary", slot=None, checkable=False):
    """variant: primary | secondary | danger | ghost | chip"""
    btn = QPushButton(text)
    btn.setProperty("variant", variant)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setCheckable(checkable)
    if slot:
        btn.clicked.connect(slot)
    return btn


def make_card(margins=(18, 16, 18, 16), spacing=12):
    """Rounded surface. Returns (frame, layout)."""
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return frame, layout


def page_header(icon, title, subtitle="", badge=None, admin=False):
    """Title + subtitle on the left, optional role pill on the right."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)

    col = QVBoxLayout()
    col.setSpacing(2)
    t = QLabel(f"{icon}  {title}")
    t.setObjectName("title")
    col.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setObjectName("subtitle")
        col.addWidget(s)
    row.addLayout(col)
    row.addStretch()

    if badge:
        pill = QLabel(badge)
        pill.setObjectName("pill")
        pill.setProperty("admin", "true" if admin else "false")
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(pill, 0, Qt.AlignmentFlag.AlignTop)
    return box


def make_status():
    label = QLabel("")
    label.setObjectName("status")
    label.setWordWrap(True)
    return label


def set_status(label, text, error=False):
    label.setProperty("error", "true" if error else "false")
    label.style().unpolish(label)
    label.style().polish(label)
    label.setText(text)


def style_table(table, stretch=False):
    """Modern read-only table. stretch=True fills the width (few columns)."""
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setWordWrap(False)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(40)
    header = table.horizontalHeader()
    header.setHighlightSections(False)
    header.setMinimumSectionSize(90)
    header.setSectionResizeMode(
        QHeaderView.ResizeMode.Stretch if stretch else QHeaderView.ResizeMode.Interactive)
    header.setStretchLastSection(not stretch)
    table._stretch = stretch


def populate(table, headers, rows, max_col=280):
    """Fill a table from a list of dicts. Long text gets a tooltip."""
    table.setUpdatesEnabled(False)
    table.clear()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels([str(h).upper() for h in headers])
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, h in enumerate(headers):
            text = str(row.get(h, ""))
            item = QTableWidgetItem(text)
            if len(text) > 28:
                item.setToolTip(text)
            table.setItem(r, c, item)
    if not getattr(table, "_stretch", False):
        table.resizeColumnsToContents()
        for c in range(len(headers)):
            table.setColumnWidth(c, min(max(table.columnWidth(c), 110), max_col))
    table.setUpdatesEnabled(True)