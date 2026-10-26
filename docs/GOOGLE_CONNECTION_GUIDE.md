# Connecting the CRM to Google Drive, Google Calendar and Email

This guide explains every step used to connect the application to Google.
Follow it in order. Total time: about 20 minutes.

| Feature | How it connects | Secret file |
|---|---|---|
| Users, Applications, Mentor, Interviews, VIT1, VIT2 (Google Sheets) | `gspread` + **service account** | `credentials/service_account.json` |
| Admin menu - calendar events | Google Calendar API + **service account** | `credentials/service_account.json` |
| Admin menu - sending e-mails | Gmail **SMTP** with an App Password | `.env` (`CRM_EMAIL`, `CRM_PASSWORD`) |

> The OAuth file `client_secret_*.json` is **not required** with this setup.
> Keep it only as a backup, and never upload it to GitHub.

---

## Part 1 - Google Cloud project and service account

1. Open <https://console.cloud.google.com> and sign in with the main Gmail account that owns the Drive files.
2. Create a project: **Select a project -> New project** -> name it `crm-capstone` -> **Create**.
3. Enable the APIs: **APIs & Services -> Library**. Search for and **Enable**:
   - Google Sheets API
   - Google Drive API
   - Google Calendar API
4. Create the service account: **APIs & Services -> Credentials -> Create credentials -> Service account**.
   Name it `crm-reader` -> **Create and continue** -> skip the optional steps -> **Done**.
5. Create the key: open the service account -> **Keys -> Add key -> Create new key -> JSON**. A file is downloaded.
6. Rename it to `service_account.json` and put it in the project's `credentials/` folder.
7. Open the file and copy the value of `client_email`
   (it looks like `crm-reader@crm-capstone.iam.gserviceaccount.com`). You need it in Parts 2 and 3.

## Part 2 - Google Drive (Sheets)

1. In Google Drive, open each file the app uses: **Users, Applications, Mentor, Interviews, VIT1, VIT2**.
2. Click **Share**, paste the `client_email`, set the role to **Viewer**, untick "Notify", and **Share**.
   (Sharing the whole dataset folder once also works.)
3. If a file is an uploaded Excel file (`.xlsx`) rather than a Google Sheet, open it and use
   **File -> Save as Google Sheets**. gspread cannot read raw Excel files.
4. Get each spreadsheet's **ID** from its URL: `https://docs.google.com/spreadsheets/d/<ID>/edit`
   and paste it into `SPREADSHEET_IDS` in `services/google_drive_service.py`
   (keys: `Users`, `Applications`, `Mentor`, `Interviews`, `VIT1`, `VIT2`).
   VIT1 and VIT2 are needed for *Previous VIT Check* and *Different Record*.
   Opening by ID means renaming a file in Drive never breaks the app.
5. Users file columns: `Username | Password | Authority` (Authority = `Admin` or `User`).
6. Test:
   ```
   pip install -r requirements.txt
   python check_drive.py
   ```
   Expected result: every CRM file shows `OK` with its row count and columns.

How the app reads data (`services/sheets_service.py`):
- it opens the file by name and reads the first worksheet;
- the header row is detected automatically;
- columns are found by name, so `Candidate Name`, `Full Name` or `First Name + Last Name` all work;
- results are kept in memory for 60 seconds (`CACHE_TTL_SECONDS`); **All Applications** and
  **All Conversations** force a fresh read from Drive. Login always reads live from Drive.

## Part 3 - Google Calendar

1. Create 2-3 test events in Google Calendar. For each event set the date, time and add
   **guests** (their e-mail addresses are the participants the Admin menu will mail).
2. Share the calendar: Google Calendar (web) -> hover the calendar -> **Settings and sharing ->
   Share with specific people -> Add people** -> paste the `client_email` ->
   permission **See all event details** -> **Send**.
3. Put the calendar ID in `CALENDAR_ID` (`services/google_calendar_service.py` and `debug_calendar.py`).
   For the main calendar it is the Gmail address. Other calendars: Settings -> *Integrate calendar* -> *Calendar ID*.
4. Test:
   ```
   python debug_calendar.py
   ```
   Step 2 must list the calendar and step 3 must show your events.
   If it shows `0 event(s)`, the calendar was not shared with the service account, or the ID is wrong.

Note: a service account cannot add guests or send invitations itself. It only **reads** events,
which is all this project needs.

## Part 4 - Sending e-mails (Gmail SMTP)

1. Sign in to the Gmail account that will send the messages and turn on **2-Step Verification**
   (Google Account -> Security).
2. Create an **App Password**: Google Account -> Security -> 2-Step Verification -> **App passwords** ->
   name it `CRM` -> copy the 16-character password.
3. Copy `.env.example` to `.env` and fill it in:
   ```
   CRM_EMAIL=your.sender@gmail.com
   CRM_PASSWORD=abcdefghijklmnop
   ```
4. `.env` is listed in `.gitignore`. Never commit it.
5. Test from the Admin menu: select an event and press **Send Emails to Participants**.
   `send_event_emails(ev, dry_run=False)` in `admin_menu.py` sends real e-mails; use `dry_run=True` to
   only print them. If `.env` is missing, the report shows a failure (nothing is sent).

## Part 5 - Files that must NEVER be uploaded to GitHub

`credentials/`, `.env`, `client_secret*.json`, `token.json`. They are already covered by `.gitignore`.
If one was uploaded by mistake: delete the key in Google Cloud (Credentials -> Keys -> Delete) and
create a new one, and change the Gmail App Password.

## Part 6 - Running as .exe

```
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name CRM main.py
```
Copy the `credentials/` folder and the `.env` file **next to `dist/CRM.exe`**. The app looks for them
in the exe's folder.

## Troubleshooting

| Message | Cause and fix |
|---|---|
| `service_account.json not found` | The key is not in `credentials/`, or has another name. |
| `SpreadsheetNotFound` / "file was not found" | Wrong ID in `SPREADSHEET_IDS`, or the file is not shared with `client_email`. |
| `No spreadsheet ID set for 'VIT1'` | Paste the VIT1 / VIT2 IDs in `services/google_drive_service.py`. |
| `ModuleNotFoundError: dotenv` | `pip install -r requirements.txt` (python-dotenv is needed by the e-mail service). |
| `APIError 403 ... API has not been used` | Enable the Sheets / Drive / Calendar API (Part 1, step 3). |
| `APIError 404` on calendar | Wrong `CALENDAR_ID`, or calendar not shared. |
| Calendar returns 0 events | No upcoming events, or calendar not shared with "See all event details". |
| `SMTPAuthenticationError` | Use the 16-character App Password, not the normal Gmail password; 2-Step Verification must be on. |
| Empty table, no error | Column names differ a lot - run `check_drive.py` and compare the columns it prints. |
