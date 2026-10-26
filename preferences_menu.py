"""
Preferences Menu - Regular user menu.
Author: Waseem
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout
)
from PyQt6.QtCore import Qt


class PreferencesMenu(QWidget):
    """Menu for regular users."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRM - Preferences")
        self.setGeometry(400, 200, 420, 380)
        self.init_ui()
        self.apply_style()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("⚙️ Preferences")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("title")
        layout.addWidget(title)

        # Navigation buttons
        self.apps_btn = QPushButton("📄 Applications")
        self.apps_btn.clicked.connect(self.open_applications)

        self.mentor_btn = QPushButton("🎓 Mentor Interview")
        self.mentor_btn.clicked.connect(self.open_mentor)

        self.interviews_btn = QPushButton("📋 Interviews")
        self.interviews_btn.clicked.connect(self.open_interviews)

        layout.addWidget(self.apps_btn)
        layout.addWidget(self.mentor_btn)
        layout.addWidget(self.interviews_btn)

        # Close
        self.close_btn = QPushButton("❌ Close")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a3e;
                color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel#title {
                font-size: 22px;
                font-weight: bold;
                color: #2196F3;
                padding-bottom: 10px;
            }
            QPushButton {
                padding: 12px;
                border-radius: 8px;
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #1565C0; }
            QPushButton#closeBtn { background-color: #555; }
            QPushButton#closeBtn:hover { background-color: #666; }
        """)

    def open_applications(self):
        from applications_page import ApplicationsPage
        self.next_window = ApplicationsPage(is_admin=False)
        self.next_window.show()
        self.close()

    def open_mentor(self):
        from mentor_interview_page import MentorInterviewPage
        self.next_window = MentorInterviewPage(is_admin=False)
        self.next_window.show()
        self.close()

    def open_interviews(self):
        from interviews_page import InterviewsPage
        self.next_window = InterviewsPage(is_admin=False)
        self.next_window.show()
        self.close()