"""
Interviews Page
Author: Dana (logic) - restyled with the shared theme.
Data comes from Google Drive; search filters the loaded rows instantly
(names / surnames STARTING with the typed letters, e.g. "As").
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QButtonGroup, QHBoxLayout, QLineEdit, QTableWidget, QVBoxLayout, QWidget,
)

from services.data_service import (
    get_all_interviews, get_projects_received, get_projects_sent,
    get_last_error, name_matches,
)
from theme import (
    apply_theme, center, make_button, make_card, make_status, page_header,
    populate, set_status, style_table,
)

# Columns in the Interviews sheet
COLS = ["Full Name", "Project Sent Date", "Project Received Date"]
NAME_COL = "Full Name"


class InterviewsPage(QWidget):
    def __init__(self, is_admin=False):
        super().__init__()
        self.is_admin = is_admin
        self.rows = []              # rows of the active filter (before search)
        apply_theme(self)
        self.setWindowTitle("CRM - Interviews")
        self.resize(1000, 660)
        center(self)
        self.init_ui()
        self.load(get_all_interviews, chip=self.all_chip)

    # --------------------------------------------------
    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 26, 30, 22)
        root.setSpacing(16)
        root.addWidget(page_header(
            "📋", "Interviews", "Project follow-up for interviewed candidates",
            "ADMIN" if self.is_admin else "USER", self.is_admin))

        toolbar, tl = make_card()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search by name or surname — e.g. “As”")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.render)       # live search
        tl.addWidget(self.search_input)

        self.group = QButtonGroup(self)
        chips = QHBoxLayout()
        chips.setSpacing(8)
        self.all_chip = self._chip("All Interviews", lambda: self.load(lambda: get_all_interviews(refresh=True)), chips)
        self.sent_chip = self._chip("Projects Sent", lambda: self.load(get_projects_sent), chips)
        self.recv_chip = self._chip("Projects Received", lambda: self.load(get_projects_received), chips)
        chips.addStretch()
        tl.addLayout(chips)
        root.addWidget(toolbar)

        self.table = QTableWidget(0, len(COLS))
        style_table(self.table, stretch=True)
        root.addWidget(self.table, 1)

        footer = QHBoxLayout()
        self.status = make_status()
        footer.addWidget(self.status, 1)
        footer.addWidget(make_button("←  Return to Preferences Screen", "secondary", self.go_back))
        root.addLayout(footer)

    def _chip(self, text, slot, row):
        chip = make_button(text, "chip", None, checkable=True)
        chip.clicked.connect(lambda _=False: slot())
        self.group.addButton(chip)
        row.addWidget(chip)
        return chip

    # --------------------------------------------------
    def load(self, func, chip=None):
        """Fetch rows for a filter, clear the search, show them."""
        if chip:
            chip.setChecked(True)
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.rows = func()
        finally:
            QApplication.restoreOverrideCursor()
        self.render()

    def render(self):
        q = self.search_input.text().strip()
        rows = [r for r in self.rows if name_matches(q, r.get(NAME_COL, ""))] if q else self.rows
        populate(self.table, COLS, rows)
        err = get_last_error()
        if err:
            set_status(self.status, f"⚠  {err}", True)
        elif q:
            set_status(self.status, f"{len(rows)} of {len(self.rows)} record(s) match “{q}”")
        else:
            set_status(self.status, f"{len(rows)} record(s)")

    # --------------------------------------------------
    def go_back(self):
        if self.is_admin:
            from preferences_admin import PreferencesAdmin
            self.next_window = PreferencesAdmin()
        else:
            from preferences_menu import PreferencesMenu
            self.next_window = PreferencesMenu()
        self.next_window.show()
        self.close()