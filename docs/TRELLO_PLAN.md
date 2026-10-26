# Trello Board — CRM Capstone Project
## Board Structure

---

## List 1: 📋 BACKLOG (All tasks)

### Card: Login & Navigation
- [ ] Design login window (UI)
- [ ] Connect to Users sheet via gspread
- [ ] Implement authenticate() in google_service.py
- [ ] Route Admin → Preferences Admin, User → Preferences
- [ ] Test success + error messages
- **Assigned:** Waseem
- **Due:** 06/10/2026

### Card: Preferences Menus
- [ ] User Preferences window (3 buttons)
- [ ] Admin Preferences window (4 buttons + Exit)
- [ ] Wire navigation between pages
- [ ] Test role-based access (Admin vs User)
- **Assigned:** Waseem
- **Due:** 06/10/2026

### Card: Mentor Interview Page
- [ ] Load Mentor sheet data
- [ ] Search by name/surname (partial match)
- [ ] All Conversations button
- [ ] Filter by recommendation (QComboBox)
- [ ] Return to Preferences
- **Assigned:** Dana
- **Due:** 07/10/2026

### Card: Interviews Page
- [ ] Load Interviews sheet
- [ ] Search by name/surname
- [ ] Projects Sent filter
- [ ] Projects Received filter
- [ ] Return to Preferences
- **Assigned:** Dana
- **Due:** 07/10/2026

### Card: Admin Menu — Calendar
- [ ] Connect Google Calendar API
- [ ] Fetch events (title, date, time, participants)
- [ ] Display in QTableWidget
- [ ] Refresh Events button
- **Assigned:** Waseem
- **Due:** 08/10/2026

### Card: Admin Menu — Email
- [ ] Set up Gmail SMTP + App Password
- [ ] send_event_emails() function
- [ ] Confirm dialog before sending
- [ ] Dry-run mode for testing
- **Assigned:** Waseem
- **Due:** 08/10/2026

### Card: Applications Page
- [ ] Load Applications sheet
- [ ] Search by name (partial match)
- [ ] All Applications
- [ ] Mentor Meeting Identified / Not Identified
- [ ] Duplicate Record (name + email)
- [ ] Previous VIT Check (Applications ∩ VIT1 ∪ VIT2)
- [ ] Different Record (VIT1 only or VIT2 only)
- [ ] Application Filter (unique by name)
- **Assigned:** Mohammed
- **Due:** 09/10/2026

### Card: UML Diagrams
- [ ] Use Case Diagram
- [ ] Class Diagram
- [ ] Description documents
- **Assigned:** All
- **Due:** 06/10/2026

### Card: Testing
- [ ] Test wrong credentials
- [ ] Test Admin vs User login
- [ ] Test each page + return
- [ ] Test empty search results
- [ ] Test duplicate records
- [ ] Test Google connection failure
- [ ] Test email send (dry-run then real)
- **Assigned:** All
- **Due:** 10/10/2026

### Card: Packaging & Delivery
- [ ] requirements.txt
- [ ] README.md
- [ ] GOOGLE_CONNECTION_GUIDE.md
- [ ] Build .exe (PyInstaller)
- [ ] GitHub repo + branches
- [ ] Presentation slides
- **Assigned:** Waseem ,Mohammed, Dana
- **Due:** 10/10/2026

---

## List 2: 🎯 THIS WEEK

| Day | Task |
|-----|------|
| 06/10 | UML + Login + Navigation |
| 07/10 | Mentor + Interviews pages |
| 08/10 | Calendar + Admin + Email |
| 09/10 | Applications full functions |
| 10/10 | Testing + Packaging + GitHub |
| 11/10 | Final Presentation |

---

## List 3: 🚧 IN PROGRESS

*(Move cards here when actively working on them)*

---

## List 4: 👀 REVIEW

*(Move cards here when code is complete but needs testing)*

---

## List 5: ✅ DONE

*(Move cards here when fully tested and merged)*

---

## Daily Meeting Template

**Date:** __/10/2026
**Attendees:** Waseem, Dana, Mohammed

### ✅ Completed yesterday:
- ...

### 🚧 Working on today:
- ...

### ⚠️ Blockers:
- ...

### 📅 Plan for tomorrow:
- ...

---

## Labels

| Label | Color | Meaning |
|-------|-------|---------|
| Login | Blue | Auth + roles |
| UI | Green | Design only |
| Data | Yellow | Google Drive/Sheets |
| Calendar | Orange | Google Calendar |
| Email | Purple | SMTP |
| Critical | Red | Blocks others |
| Docs | Grey | UML, README |

---

## Member Assignment Summary

| Member | Responsibility | Files |
|--------|---------------|-------|
| **Waseem** | Login + Navigation + Admin Menu + Docs | `login_window.py`, `preferences_*.py`, `admin_menu.py`, `README.md` |
| **Dana** | Mentor + Interviews | `mentor_interview_page.py`, `interviews_page.py` |
| **Mohammed** | Applications | `applications_page.py` |
| **All** | Google Services + Testing | `services/*.py`, `tests/*.py` |