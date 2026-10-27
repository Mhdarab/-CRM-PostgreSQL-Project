import os

from PyQt6 import QtWidgets, uic

from services.postgres_data_service import PostgreSQLDataService
from theme import apply_theme, style_table


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ApplicationsPage(QtWidgets.QWidget):
    def __init__(self, is_admin=False):
        super().__init__()
        self.is_admin = is_admin
        self.postgres_service = PostgreSQLDataService()

        # 1. Load the Qt Designer UI once
        ui_path = os.path.join(
            BASE_DIR, "ui", "applications_page.ui"
        )
        uic.loadUi(ui_path, self)

        # 2. Find the table
        table = self.findChild(
            QtWidgets.QTableWidget, "applicationsTable"
        )

        if table is None:
            table = self.findChild(
                QtWidgets.QTableWidget, "applicationsTabel"
            )

        if table is None:
            raise RuntimeError(
                "The UI must contain a QTableWidget named "
                "'applicationsTable'."
            )

        self.applicationsTable = table

        # 3. Remove old Designer styles
        self.setStyleSheet("")

        for widget in self.findChildren(QtWidgets.QWidget):
            widget.setStyleSheet("")

        # 4. Set button styles
        filter_buttons = [
            self.allApplicationsButton,
            self.mentorDefinedButton,
            self.mentorNotDefinedButton,
            self.btn_previous_vit,
            self.btn_duplicates,
            self.btn_different_records,
            self.btn_filter_applications,
        ]

        for button in filter_buttons:
            button.setProperty("variant", "secondary")

        self.returnButton.setProperty("variant", "ghost")

        apply_theme(self)
        style_table(self.applicationsTable)

        self.setWindowTitle("Applications")

        # 5. Connect the existing buttons
        self.searchButton.clicked.connect(
            self.search_applications
        )
        self.allApplicationsButton.clicked.connect(
            self.show_all_applications
        )
        self.mentorDefinedButton.clicked.connect(
            self.show_mentor_defined
        )
        self.mentorNotDefinedButton.clicked.connect(
            self.show_mentor_not_defined
        )
        self.returnButton.clicked.connect(
            self.open_preferences
        )

        # 6. Connect the new buttons
        self.btn_previous_vit.clicked.connect(
            self.show_previous_vit
        )
        self.btn_duplicates.clicked.connect(
            self.show_duplicates
        )
        self.btn_different_records.clicked.connect(
            self.show_different_records
        )
        self.btn_filter_applications.clicked.connect(
            self.show_unique_applications
        )

        # Enter in the search field also runs the search
        self.searchInput.returnPressed.connect(
            self.search_applications
        )

        # 7. Load applications when the page opens
        self.show_all_applications()

    def display_results(self, result):
        """Display service results without changing source keys."""
        

        headers, rows = result
        table = self.applicationsTable

        display_names = {
            "Timestamp": "Date",
            "Full Name": "Full name",
            "Email": "Mail",
            "Phone": "Telephone",
            "Postal Code": "Post Code",
            "Province": "State",
        }

        sorting_enabled = table.isSortingEnabled()
        table.setSortingEnabled(False)
        table.setUpdatesEnabled(False)

        try:
            table.clearContents()
            table.setRowCount(0)
            table.setColumnCount(len(headers))

            table.setHorizontalHeaderLabels([
                display_names.get(header, str(header))
                for header in headers
            ])

            table.setRowCount(len(rows))

            for row_index, record in enumerate(rows):
                table.setRowHidden(row_index, False)

                for column_index, header in enumerate(headers):
                    value = record.get(header, "")
                    text = "" if value is None else str(value)

                    item = QtWidgets.QTableWidgetItem(text)
                    item.setToolTip(text)

                    table.setItem(
                        row_index, column_index, item
                    )

            table.resizeColumnsToContents()

            for column in range(table.columnCount()):
                width = table.columnWidth(column)
                table.setColumnWidth(
                    column, min(max(width, 110), 280)
                )

        finally:
            table.setSortingEnabled(sorting_enabled)
            table.setUpdatesEnabled(True)

    def search_applications(self):
        query = self.searchInput.text().strip()

        if not query:
            self.show_all_applications()
            return

        try:
            result = self.postgres_service.search_applications(query)
            self.display_results(result)

        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self,
                "Database Error",
                str(error)
            )

    def show_all_applications(self):
        try:
            result = self.postgres_service.get_applications()

            # PostgreSQL returned the data successfully
            headers, rows = result

            print("Applications loaded from PostgreSQL:", len(rows))

            self.display_results((headers, rows))

        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self,
                "Database Error",
                str(error)
            )

    def show_mentor_defined(self):
        try:
            result = self.postgres_service.get_mentor_defined()
            self.display_results(result)

        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self,
                "Database Error",
                str(error)
            )


    def show_mentor_not_defined(self):
        try:
            result = self.postgres_service.get_mentor_not_defined()
            self.display_results(result)

        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self,
                "Database Error",
                str(error)
            )

    def show_previous_vit(self):
        try:
            result = self.postgres_service.get_previous_vit()
            self.display_results(result)

            headers, rows = result
            print(f"Previous VIT: {len(rows)} records")

        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self,
                "Database Error",
                str(error)
            )

    def show_duplicates(self):
        try:
            result = self.postgres_service.get_duplicate_applications()
            self.display_results(result)

        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self,
                "Database Error",
                str(error)
            )

    def show_different_records(self):
        try:
            headers, rows = self.postgres_service.get_different_records()
            self.display_results((headers, rows))
            print(f"Different Records: {len(rows)} records")

        except Exception as error:
            print("Error loading different records:", error)

    def show_unique_applications(self):
        try:
            headers, rows = self.postgres_service.get_unique_applications()

            self.display_results((headers, rows))

            print(f"Unique Applications: {len(rows)} records")

        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self,
                "Database Error",
                str(error)
            )

    def open_preferences(self):
        if self.is_admin:
            from preferences_admin import PreferencesAdmin
            self.next_window = PreferencesAdmin()
        else:
            from preferences_menu import PreferencesMenu
            self.next_window = PreferencesMenu()

        self.next_window.show()
        self.close()