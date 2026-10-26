"""
Login Window - Uses login.ui (Qt Designer)
Author: Waseem

Flow:
    - Username + Password entered
    - Show password toggle works
    - Login validates against Google Drive Users file
    - Admin  -> Preferences Admin
    - User   -> Preferences Menu
    - Close  -> Exit application
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt

from login import Ui_LoginWindow

from services.google_drive_service import authenticate
from theme import LOGIN_QSS, center


class LoginWindow(QWidget):
    """Modern login window loaded from login.ui."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        # Qt keeps the sheet that setupUi() installed; clear it first so the
        # shared design system fully replaces it.
        self.setStyleSheet("")
        self.setStyleSheet(LOGIN_QSS)
        self.ui.lblForgot.setText("Forgot your password? Contact your administrator.")
        self.ui.lblForgot.setCursor(Qt.CursorShape.ArrowCursor)
        self.resize(440, 640)
        center(self)

        # ---------- Ensure error label is visible ----------
        self.ui.lblError.setVisible(True)
        self.ui.lblError.setMinimumHeight(28)
        self.ui.lblError.setText("")
        self.ui.lblError.setWordWrap(True)
        self.ui.lblError.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------- Connect signals ----------
        self.ui.btnLogin.clicked.connect(self.handle_login)
        self.ui.btnExit.clicked.connect(self.close)
        self.ui.chkShow.toggled.connect(self.toggle_password)

        # Enter key submits
        self.ui.txtUsername.returnPressed.connect(
            lambda: self.ui.txtPassword.setFocus()
        )
        self.ui.txtPassword.returnPressed.connect(self.handle_login)

        # Clear old errors when typing
        self.ui.txtUsername.textChanged.connect(self.clear_error)
        self.ui.txtPassword.textChanged.connect(self.clear_error)

    # --------------------------------------------------
    # Show / Hide password
    # --------------------------------------------------
    def toggle_password(self, checked: bool):
        mode = (
            self.ui.txtPassword.EchoMode.Normal
            if checked
            else self.ui.txtPassword.EchoMode.Password
        )
        self.ui.txtPassword.setEchoMode(mode)
        self.ui.txtPassword.setFocus()

    # --------------------------------------------------
    # Helpers — visible error / success messages
    # --------------------------------------------------
    def clear_error(self):
        """Clear the message when the user types."""
        self.ui.lblError.setText("")
        self.ui.lblError.setStyleSheet("")   # reset style

    def show_error(self, msg: str):
        """Display a red error message — ALWAYS visible."""
        self.ui.lblError.setStyleSheet(
            "color: #f87171;"
            "background-color: rgba(248, 113, 113, 0.14);"
            "font-size: 13px;"
            "font-weight: bold;"
            "border-radius: 6px;"
            "padding: 6px;"
        )
        self.ui.lblError.setText(f"❌ {msg}")
        self.ui.lblError.setVisible(True)
        self.ui.lblError.adjustSize()
        QApplication.processEvents()

    def show_success(self, msg: str):
        """Display a green success message."""
        self.ui.lblError.setStyleSheet(
            "color: #34d399;"
            "background-color: rgba(52, 211, 153, 0.14);"
            "font-size: 13px;"
            "font-weight: bold;"
            "border-radius: 6px;"
            "padding: 6px;"
        )
        self.ui.lblError.setText(f"✅ {msg}")
        self.ui.lblError.setVisible(True)
        self.ui.lblError.adjustSize()
        QApplication.processEvents()

    def set_loading(self, loading: bool):
        """Disable/enable inputs while checking."""
        self.ui.btnLogin.setEnabled(not loading)
        self.ui.txtUsername.setEnabled(not loading)
        self.ui.txtPassword.setEnabled(not loading)
        self.ui.btnLogin.setText("⏳ Checking..." if loading else "LOGIN")
        QApplication.processEvents()

    # --------------------------------------------------
    # Login handler
    # --------------------------------------------------
    def handle_login(self):
        username = self.ui.txtUsername.text().strip()
        password = self.ui.txtPassword.text().strip()

        # ---------- 1. Empty fields ----------
        if not username and not password:
            self.show_error("Please enter your username and password.")
            self.ui.txtUsername.setFocus()
            return

        if not username:
            self.show_error("Please enter your username.")
            self.ui.txtUsername.setFocus()
            return

        if not password:
            self.show_error("Please enter your password.")
            self.ui.txtPassword.setFocus()
            return

        # ---------- 2. Loading ----------
        self.set_loading(True)

        # ---------- 3. Authenticate ----------
        try:
            success, role, message = authenticate(username, password)
        except Exception as e:
            self.set_loading(False)
            self.show_error(f"Connection error: {e}")
            return

        self.set_loading(False)

        # ---------- 4. Wrong credentials ----------
        if not success:
            self.show_error( "Your username or password is incorrect.")
           
            return

        # ---------- 5. Success ----------
        self.show_success(message or "Login successful!")

        # Route to correct menu
        if role == "admin":
            from preferences_admin import PreferencesAdmin
            self.next_window = PreferencesAdmin()
        else:
            from preferences_menu import PreferencesMenu
            self.next_window = PreferencesMenu()

        self.next_window.show()
        self.close()