"""
Mentor Interview Page
Author: Dana
UI loaded from ui/mentor_interview_page.ui
Search filters the loaded rows instantly (names STARTING with typed letters).
"""

import os
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidgetItem,
)
from services.postgres_data_service import PostgreSQLDataService
from services.search_utils import name_matches
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidgetItem, QMessageBox,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLS = [
    "Date", "VIT Group", "Candidate Name", "Mentor Name",
    "Score", "Recommendation", "Secondary Score", "Notes",
]
NAME_COL = "Candidate Name"


class MentorInterviewPage(QWidget):
    def __init__(self, is_admin=False):
        super().__init__()
        self.is_admin = is_admin
        self.rows = []
        self.postgres_service = PostgreSQLDataService()

        # ---------- Load .ui ----------
        ui_path = os.path.join(BASE_DIR, "ui", "mentor_interview_page.ui")
        uic.loadUi(ui_path, self)

        # ---------- Aliases ----------
        self.search_input = self.searchInput
        self.all_btn      = self.allConversationsButton
        self.combo        = self.categoryComboBox
        self.table        = self.conversationsTable
        self.status       = self.statusLabel
        self.return_btn   = self.returnButton

        # ---------- Role badge ----------
        self.headerBadge.setProperty("admin", "true" if is_admin else "false")
        self.headerBadge.setText("ADMIN" if is_admin else "USER")

        # ---------- Signals ----------
        self.search_input.textChanged.connect(self.render)   # live search
        self.all_btn.clicked.connect(self.on_all)
        self.combo.currentTextChanged.connect(self.on_combo_changed)
        self.return_btn.clicked.connect(self.go_back)

        # ---------- Initial load ----------
        self.load(self.postgres_service.get_all_conversations)

    # --------------------------------------------------
    def load(self, func):
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        error_message = None

        try:
            self.rows = func()

        except Exception as error:
            self.rows = []
            error_message = str(error)

        finally:
            QApplication.restoreOverrideCursor()

        self.render()

        if error_message:
            self.status.setProperty("error", "true")
            self.status.setText("⚠ Database connection error")

            self.status.style().unpolish(self.status)
            self.status.style().polish(self.status)

            QMessageBox.warning(
                self,
                "Database Error",
                f"Could not load mentor interviews:\n{error_message}"
            )

    def render(self):
        q = self.search_input.text().strip()
        rows = (
            [r for r in self.rows if name_matches(q, r.get(NAME_COL, ""))]
            if q else self.rows
        )

        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, col in enumerate(COLS):
                self.table.setItem(r, c, QTableWidgetItem(str(row.get(col, ""))))

        self.status.setProperty("error", "false")

        if q:
            self.status.setText(
                f"{len(rows)} of {len(self.rows)} record(s) match “{q}”"
            )
        else:
            self.status.setText(f"{len(rows)} record(s)")

        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    # --------------------------------------------------
    def on_all(self):
        self.combo.blockSignals(True)
        self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)
        self.load(self.postgres_service.get_all_conversations)

    def on_combo_changed(self, value):
        

        if value == "All Recommendations":
            self.load(self.postgres_service.get_all_conversations)
        else:
            self.load(
                lambda: self.postgres_service.get_conversations_by_recommendation(value)
            )

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