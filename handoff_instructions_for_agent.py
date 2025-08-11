handoff_instructions = '''
Task: Fix, verify, and push the Flask admission system.

Requirements:
- Use SQLite with a single global DATABASE = 'users.db' in app.py and auth_handler.py.
- Replace all sqlite3.connect('users.db') with sqlite3.connect(DATABASE) everywhere used by app.py.
- Ensure directories exist on startup: uploads, uploads/admission_photos.
- Initialize/migrate DB on startup (create if missing):
  admissions(id AUTOINCREMENT, student_name, dob, student_phone, student_email, class, school_name, maths_marks, maths_rating, last_percentage, parent_name, parent_phone, passport_photo, status default 'pending', submitted_at, user_id, submit_ip, approved_at, approved_by, disapproved_at, disapproved_by, disapproval_reason)
  admission_access(id AUTOINCREMENT, admission_id UNIQUE, access_username UNIQUE, access_password, created_at)
  admission_access_plain(id AUTOINCREMENT, admission_id UNIQUE, access_username UNIQUE, access_password_plain, created_at)
  If submit_ip missing on admissions, ALTER TABLE to add it.
- Add password hashing fallback (werkzeug.security if available; else sha256 with constant salt 'admission_salt_2024').
- Add secure_filename fallback if werkzeug.utils missing.
- /admission:
  - GET: render form (multipart).
  - POST: save passport_photo, insert admissions row incl. submit_ip=request.remote_addr; generate access_username=f"ADM{admission_id:06d}" and random password (secrets.token_urlsafe(8)); hash+store in admission_access, store plaintext in admission_access_plain, show once to user, also store in session for one-time display.
- /check_admission:
  - Verify username+password (hash check) against admission_access; on success show admission status/details.
- Admin actions:
  - Approve: set status='approved', approved_at, approved_by.
  - Disapprove: set status='disapproved', disapproved_at, disapproved_by, disapproval_reason.
  - Restrict to roles admin/teacher.
- Ensure SocketIO init is correct and all init functions are called at startup.
- Templates:
  - templates/admission.html: POST + enctype multipart, field names match parsing.
  - templates/check_admission.html: POST with username/password.
- Verify by submitting one admission and checking credentials flow end-to-end.
- Git:
  - git add .
  - git commit -m "Fix admission system: standardize DB path; implement credentials flow; secure uploads; diagnostics"
  - git push (or PR and merge)
Acceptance:
- All DB connects use sqlite3.connect(DATABASE)
- New admissions insert; ADM###### + password generated and saved (hash + plaintext table)
- /check_admission validates and shows status
- Approve/disapprove works
- Directories auto-created
- App starts without errors and changes are pushed
'''

if __name__ == "__main__":
    print(handoff_instructions)