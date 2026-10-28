from psycopg2.extras import RealDictCursor

from services.database_connection import DatabaseConnection

import re



class PostgreSQLDataService:

    def __init__(self):
        self.db = DatabaseConnection()

    def get_applications(self):
        connection = self.db.connect()

        if connection is None:
            raise ConnectionError("Could not connect to PostgreSQL.")

        try:
            with connection.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                cursor.execute("""
                    SELECT
                        a.applicationid,
                        a.timestamp,
                        t.fullname,
                        t.emailaddress,
                        t.phonenumber,
                        t.postalcode,
                        t.stateofresidence,
                        a.currentstatus,
                        a.applicationterm
                    FROM applications AS a
                    JOIN trainees AS t
                        ON a.traineeid = t.traineeid
                    ORDER BY a.applicationid
                """)

                records = cursor.fetchall()

                headers = [
                    "Application ID",
                    "Timestamp",
                    "Full Name",
                    "Email",
                    "Phone",
                    "Postal Code",
                    "Province",
                    "Current Status",
                    "Application Period"
                ]

                rows = []

                for record in records:
                    rows.append({
                        "Application ID": record["applicationid"],
                        "Timestamp": record["timestamp"],
                        "Full Name": record["fullname"],
                        "Email": record["emailaddress"],
                        "Phone": record["phonenumber"],
                        "Postal Code": record["postalcode"],
                        "Province": record["stateofresidence"],
                        "Current Status": record["currentstatus"],
                        "Application Period": record["applicationterm"]
                    })

                return headers, rows

        finally:
            connection.close()

    def search_applications(self, query):
        headers, rows = self.get_applications()

        query = query.strip().casefold()

        if not query:
            return headers, rows

        filtered_rows = [
            row
            for row in rows
            if any(
                query in str(value).casefold()
                for value in row.values()
                if value is not None
            )
        ]

        return headers, filtered_rows

    def get_mentor_defined(self):
        headers, rows = self.get_applications()

        connection = self.db.connect()

        if connection is None:
            raise ConnectionError("Could not connect to PostgreSQL.")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT t.emailaddress
                    FROM mentors AS m
                    JOIN trainees AS t
                        ON m.traineeid = t.traineeid
                """)

                mentor_emails = {
                    email.lower()
                    for (email,) in cursor.fetchall()
                    if email
                }

            filtered_rows = [
                row for row in rows
                if row.get("Email")
                and row["Email"].lower() in mentor_emails
            ]

            return headers, filtered_rows

        finally:
            connection.close()


    def get_mentor_not_defined(self):
        headers, rows = self.get_applications()

        connection = self.db.connect()

        if connection is None:
            raise ConnectionError("Could not connect to PostgreSQL.")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT t.emailaddress
                    FROM mentors AS m
                    JOIN trainees AS t
                        ON m.traineeid = t.traineeid
                """)

                mentor_emails = {
                    email.lower()
                    for (email,) in cursor.fetchall()
                    if email
                }

            filtered_rows = [
                row for row in rows
                if not row.get("Email")
                or row["Email"].lower() not in mentor_emails
            ]

            return headers, filtered_rows

        finally:
            connection.close()

    def get_duplicate_applications(self):
        headers, rows = self.get_applications()

        connection = self.db.connect()

        if connection is None:
            raise ConnectionError("Could not connect to PostgreSQL.")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT traineeid
                    FROM applications
                    GROUP BY traineeid
                    HAVING COUNT(*) > 1
                """)

                duplicate_ids = {
                    trainee_id
                    for (trainee_id,) in cursor.fetchall()
                }

            if not duplicate_ids:
                return headers, []

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT applicationid
                    FROM applications
                    WHERE traineeid = ANY(%s)
                """, (list(duplicate_ids),))

                duplicate_application_ids = {
                    application_id
                    for (application_id,) in cursor.fetchall()
                }

            filtered_rows = [
                row for row in rows
                if row["Application ID"] in duplicate_application_ids
            ]

            return headers, filtered_rows

        finally:
            connection.close()
            
    def get_different_records(self):
        """
        Return applications belonging to people who appear
        in VIT1 or VIT2, but not both.
        """

        headers, rows = self.get_applications()

        def normalize(value):
            return " ".join(str(value or "").split()).casefold()

        vit1_names = {
            normalize(row.get("Full Name"))
            for row in rows
            if normalize(row.get("Application Period")) == "vit1"
        }

        vit2_names = {
            normalize(row.get("Full Name"))
            for row in rows
            if normalize(row.get("Application Period")) == "vit2"
        }

        common_names = vit1_names & vit2_names

        different_rows = [
            row
            for row in rows
            if normalize(row.get("Application Period")) in ("vit1", "vit2")
            and normalize(row.get("Full Name")) not in common_names
        ]

        return headers, different_rows

    def get_previous_vit(self):
        """
        Return VIT3 applications whose applicants
        also appeared in VIT1 or VIT2.
        """
        headers, rows = self.get_applications()

        def normalize(value):
            return " ".join(str(value or "").split()).casefold()

        previous_names = {
            normalize(row.get("Full Name"))
            for row in rows
            if normalize(row.get("Application Period")) in ("vit1", "vit2")
        }

        previous_rows = [
            row
            for row in rows
            if normalize(row.get("Application Period")) == "vit3"
            and normalize(row.get("Full Name")) in previous_names
        ]

        return headers, previous_rows

    
    def get_unique_applications(self):
        """
        Return applications without duplicate people.
        Each person (name + email) appears only once.
        """

        headers, rows = self.get_applications()

        def normalize(value):
            return str(value or "").strip().casefold()

        seen = set()
        unique_rows = []

        for row in rows:
            name = normalize(row.get("Full Name"))
            email = normalize(row.get("Email"))

            key = (name, email)

            if name and key in seen:
                continue

            seen.add(key)
            unique_rows.append(row)

        return headers, unique_rows

    def get_all_interviews(self):
        """
        Get all interviews from PostgreSQL.
        """

        connection = DatabaseConnection().connect()

        if connection is None:
            raise ConnectionError("Could not connect to PostgreSQL")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        t.fullname,
                        p.projectsubmissiondate,
                        p.projectreviewdate
                    FROM projecttracking p
                    JOIN trainees t
                        ON p.traineeid = t.traineeid
                    ORDER BY p.projecttrackingid
                """)

                records = cursor.fetchall()

                rows = []

                for name, sent_date, received_date in records:
                    rows.append({
                        "Full Name": name,
                        "Project Sent Date": (
                            str(sent_date) if sent_date else ""
                        ),
                        "Project Received Date": (
                            str(received_date) if received_date else ""
                        )
                    })

                return rows

        finally:
            connection.close()

    def get_projects_sent(self):
        """
        Return interviews where the project was sent.
        """
        rows = self.get_all_interviews()

        return [
            row for row in rows
            if row.get("Project Sent Date")
        ]

    def get_projects_received(self):
        """
        Return interviews where the project was received.
        """
        rows = self.get_all_interviews()

        return [
            row for row in rows
            if row.get("Project Received Date")
        ]

    def get_all_conversations(self):
        """Get mentor interviews from PostgreSQL."""

        connection = DatabaseConnection().connect()

        if connection is None:
            raise ConnectionError("Could not connect to PostgreSQL")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        m.meetingdate,
                        t.fullname,
                        m.mentorfullname,
                        (
                            SELECT STRING_AGG(
                                DISTINCT a.applicationterm, ', '
                            )
                            FROM applications a
                            WHERE a.traineeid = m.traineeid
                        ) AS vit_group,
                        m.thoughts,
                        m.comments
                    FROM mentors m
                    LEFT JOIN trainees t
                        ON m.traineeid = t.traineeid
                    ORDER BY m.mentorid
                """)

                records = cursor.fetchall()
                rows = []

                for date, candidate, mentor, vit, thoughts, comments in records:

                    thoughts = thoughts or ""

                    def extract(field):
                        match = re.search(
                            rf"^{re.escape(field)}:\s*(.*)$",
                            thoughts,
                            re.MULTILINE | re.IGNORECASE
                        )
                        return match.group(1).strip() if match else ""

                    rows.append({
                        "Date": str(date.date()) if date else "",
                        "VIT Group": vit or "",
                        "Candidate Name": candidate or "",
                        "Mentor Name": mentor or "",
                        "Score": extract("Score"),
                        "Recommendation": extract("Recommendation"),
                        "Secondary Score": extract("Secondary Score"),
                        "Notes": comments or ""
                    })

                return rows

        finally:
            connection.close()

    def get_conversations_by_recommendation(self, value):
        """
        Filter mentor interviews by recommendation.
        """

        rows = self.get_all_conversations()

        wanted = str(value).strip().casefold()

        return [
            row for row in rows
            if str(row.get("Recommendation", "")).strip().casefold() == wanted
        ]