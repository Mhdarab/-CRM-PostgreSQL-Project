"""
Admin Menu
Author: Waseem (logic) - restyled with the shared theme.
Google Calendar events + e-mail to the participants of the selected event.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QMessageBox, QTableWidget, QVBoxLayout, QWidget,
)

from services.google_calendar_service import fetch_events
from services.email_service import send_event_emails
from theme import (
    apply_theme, center, make_button, make_card, make_status, page_header,
    populate, set_status, style_table,
)

HEADERS = ["Event ID", "Title", "Date", "Time", "Participants"]


class AdminMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.events = []
        apply_theme(self)
        self.setWindowTitle("CRM - Admin Menu")
        self.resize(1120, 700)
        center(self)
        self.init_ui()
        self.load_events()   # auto-load on open

    # --------------------------------------------------
    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 26, 30, 22)
        root.setSpacing(16)
        root.addWidget(page_header(
            "🛡️", "Admin Menu", "Google Calendar events and participant e-mails",
            "ADMIN", True))

        toolbar, tl = make_card()
        row = QHBoxLayout()
        row.setSpacing(10)
        self.event_btn = make_button("📅  Event Record", "secondary", self.load_events)
        self.mail_btn = make_button("✉️  Send Emails to Participants", "primary", self.send_emails)
        row.addWidget(self.event_btn)
        row.addWidget(self.mail_btn)
        row.addStretch()
        tl.addLayout(row)
        self.info = make_status()
        tl.addWidget(self.info)
        root.addWidget(toolbar)

        self.table = QTableWidget(0, len(HEADERS))
        style_table(self.table)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        root.addWidget(self.table, 1)

        footer = QHBoxLayout()
        footer.addWidget(make_button("←  Preferences — Return to Admin Screen", "secondary", self.go_back))
        footer.addStretch()
        footer.addWidget(make_button("Exit", "danger", self.close))
        root.addLayout(footer)

    # --------------------------------------------------
    # Load events from Google Calendar
    # --------------------------------------------------
    def load_events(self):
        set_status(self.info, "⏳  Fetching events from Google Calendar...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()
        try:
            self.events = fetch_events()
        except Exception as e:
            self.events = []
            populate(self.table, HEADERS, [])
            set_status(self.info, f"⚠  Failed to load events: {e}", True)
            return
        finally:
            QApplication.restoreOverrideCursor()

        rows = [{
            "Event ID": ev["id"], "Title": ev["title"],
            "Date": ev["date"], "Time": ev["time"],
            "Participants": ", ".join(ev["participants"]),
        } for ev in self.events]
        populate(self.table, HEADERS, rows)
        set_status(self.info, f"✅  Loaded {len(self.events)} event(s). "
                              "Select one to e-mail its participants.")

    # --------------------------------------------------
    # Row selection
    # --------------------------------------------------
    def on_row_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.events):
            return
        ev = self.events[row]
        set_status(self.info,
                   f"📍  {ev['title']} — {ev['date']} {ev['time']} — "
                   f"{len(ev['participants'])} participant(s)")

    # --------------------------------------------------
    # Send emails
    # --------------------------------------------------
    def send_emails(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No event", "Select an event first.")
            return

        ev = self.events[row]
        if not ev["participants"]:
            QMessageBox.information(self, "No recipients",
                                    "This event has no participants.")
            return

        confirm = QMessageBox.question(
            self,
            "Send Emails",
            f"Send emails to {len(ev['participants'])} participant(s) "
            f"of '{ev['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            results = send_event_emails(ev, dry_run=False)  # True = print only
        finally:
            QApplication.restoreOverrideCursor()
        report = "\n".join(
            f"{'✅' if ok else '❌'} {email}" for email, ok in results
        )
        QMessageBox.information(
            self, "Email Report", f"Emails for '{ev['title']}':\n\n{report}"
        )

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------
    def go_back(self):
        from preferences_admin import PreferencesAdmin
        self.next_window = PreferencesAdmin()
        self.next_window.show()
        self.close()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = AdminMenu()
    w.show()
    sys.exit(app.exec())