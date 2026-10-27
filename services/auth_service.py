import bcrypt
from services.database_connection import DatabaseConnection


class AuthService:

    def __init__(self):
        self.db = DatabaseConnection()

    def authenticate(self, username, password):
        connection = self.db.connect()

        if connection is None:
            return False, None, "Database connection failed."

        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT password, role
                FROM users
                WHERE LOWER(username) = LOWER(%s)
                """,
                (username,)
            )

            user = cursor.fetchone()

            if user is None:
                return False, None, "User not found."

            stored_password, role = user

            password_matches = bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8")
            )

            if password_matches:
                return True, role.strip().lower(), "Login successful"

            return False, None, "Wrong password."

        except Exception as error:
            return False, None, f"Authentication error: {error}"

        finally:
            cursor.close()
            connection.close()


def authenticate(username, password):
    auth = AuthService()
    return auth.authenticate(username, password)