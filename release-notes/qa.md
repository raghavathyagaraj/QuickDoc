QA Release Notes - Sprint 1

1. Register Patient (01.01)
Scope Completed:
- Role-Based Access Control (ET-In): Patient role assigned on registration
- Field Validation (FV): Email format, password strength, DOB, phone validated
- Client Setup (CS): Full patient profile with insurance and payment info
- Data-Driven Defaults (DDD): Default payment method pre-set to card
- Audit Trail (ADT): Registration event logged with IP and timestamp
- Exception Handling (ExHL): Duplicate email and DB errors handled gracefully
QA Summary:
- Patient registration saves correctly to users and patients tables
- All required field validations trigger appropriate error messages
- Duplicate email registration correctly blocked with user-friendly message
- Audit log entry created for every successful registration
- Form rejects weak passwords and future dates of birth

2. Register Doctor (01.02)
Scope Completed:
- Doctor Specialty (DS): 10 specialties seeded and selectable from DB
- Role-Based Access (ET-In): Doctor role assigned on registration
- Field Validation (FV): License number uniqueness, fee range, experience validated
- Data-Driven Defaults (DDD): Appointment duration auto-set by specialty
- Audit Trail (ADT): Registration logged with specialty and license info
QA Summary:
- Doctor registration saves to users and doctors tables correctly
- Specialty dropdown populated from database on every page load
- Duplicate license number correctly blocked
- Default appointment duration varies correctly by specialty type

3. Login (01.03)
Scope Completed:
- Role-Based Redirect (ET-In): Patients to patient dashboard, doctors to doctor dashboard
- Field Validation (FV): Email format and password required enforced
- Remember Me (DDD): Session persists based on remember me checkbox
- Audit Trail (ADT): Successful and failed login attempts both logged
- Exception Handling (ExHL): Wrong password, unknown email, inactive account handled
QA Summary:
- Login redirects correctly based on user role
- Failed login attempts logged in audit table with reason
- Inactive accounts blocked with appropriate message
- Remember me extends session duration correctly

4. Logout (01.04)
Scope Completed:
- Session Management (ET-In): Session cleared completely on logout
- Audit Trail (ADT): Logout event logged with timestamp, IP and role
- Exception Handling (ExHL): Unauthenticated logout redirects to login
QA Summary:
- Logout clears session and redirects to login page correctly
- Accessing protected routes after logout redirects to login
- Audit log captures logout event with full user details
- Log Out button visible and accessible from dashboard and profile pages

5. Modify Profile (01.05)
Scope Completed:
- Core Functionality + GUI (ET-In): Separate edit pages for patient and doctor
- Field Validation (FV): Required fields enforced, phone format validated
- Client Setup (CS): All profile fields editable including address and insurance
- Data-Driven Defaults (DDD): Preferred payment method retained across edits
- Audit Trail (ADT): Profile update event logged with IP and timestamp
- Exception Handling (ExHL): DB errors handled with rollback and user message
- Connectivity (CN): Form pre-filled with existing data from database
QA Summary:
- Patient profile edit saves all fields correctly to DB
- Doctor profile edit saves all fields correctly to DB
- Pre-filled form shows existing data on page load
- Required fields show validation errors when empty
- Success message displayed after successful update
- Audit log records every profile update action

6. Show Profile (01.07)
Scope Completed:
- Core Functionality + GUI (ET-In): Separate profile pages for patient and doctor
- Role-Based Access (ET-In): Patients see patient profile, doctors see doctor profile
- Client Setup (CS): All profile sections displayed including address and insurance
- Audit Trail (ADT): Profile view event logged with IP and timestamp
- Exception Handling (ExHL): 404 handled if profile not found
- Performance (PF): Navbar dropdown for fast profile access from any page
QA Summary:
- Patient profile page displays all personal, address and insurance information
- Doctor profile page displays specialty, credentials and clinic information
- Profile completion percentage calculated and displayed accurately
- Navbar dropdown with profile links accessible from dashboard
- Unauthorized role access correctly blocked with redirect

7. Reset Password (01.08)
Scope Completed:
- Core Functionality + GUI: Two-step reset flow - token generation then password update
- Field Validation (FV): Password strength, match validation, token required enforced
- Exception Handling (ExHL): Invalid token, expired token, unknown email handled
- Audit Trail (ADT): Password reset request and success both logged with IP
- Data-Driven Defaults (DDD): Token valid for 30 minutes from generation
- Connectivity (CN): No external email dependency - token displayed on screen
