"""
Preferences Admin Menu
Author: Waseem

Loads admin_preferences.ui and wires up all navigation buttons.
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt

from admin_preferences import Ui_AdminPreferences


class PreferencesAdmin(QWidget):
    """Admin Preference Menu — modern UI."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_AdminPreferences()
        self.ui.setupUi(self)

        # ---------- Connect signals ----------
        self.ui.btnApplications.clicked.connect(self.open_applications)
        self.ui.btnMentorInterview.clicked.connect(self.open_mentor)
        self.ui.btnInterviews.clicked.connect(self.open_interviews)
        self.ui.btnAdmin.clicked.connect(self.open_admin_menu)
        self.ui.btnMainMenu.clicked.connect(self.back_to_login)
        self.ui.btnExit.clicked.connect(self.close)

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------
    def open_applications(self):
        from applications_page import ApplicationsPage
        self.next_window = ApplicationsPage(is_admin=True)
        self.next_window.show()
        self.close()

    def open_mentor(self):
        from mentor_interview_page import MentorInterviewPage
        self.next_window = MentorInterviewPage(is_admin=True)
        self.next_window.show()
        self.close()

    def open_interviews(self):
        from interviews_page import InterviewsPage
        self.next_window = InterviewsPage(is_admin=True)
        self.next_window.show()
        self.close()

    def open_admin_menu(self):
        from admin_menu import AdminMenu
        self.next_window = AdminMenu()
        self.next_window.show()
        self.close()

    def back_to_login(self):
        from login_window import LoginWindow
        self.next_window = LoginWindow()
        self.next_window.show()
        self.close()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = PreferencesAdmin()
    w.show()
    sys.exit(app.exec())