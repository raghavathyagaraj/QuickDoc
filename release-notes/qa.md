<!-- QA Release Notes - Sprint 1

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
- Connectivity (CN): No external email dependency - token displayed on screen -->

<!-- QA Release Notes - Sprint 2

1. Search by Specialty (02.01)
Scope Completed:
- Core Functionality + GUI (ET-In): Specialty filter in sidebar redirects to filtered search results
- Doctor Specialty (DS): All 10 specialties seeded and filterable from sidebar
- Enrichment (ER): Verified badge, specialty badge, experience displayed on each result card
- Cache (CA): Single optimized joined query for performance across 1000+ doctors
- Connectivity (CN): Search results page loads correctly with DB connection
- Exception Handling (ExHL): Empty results handled gracefully with empty state message
- Performance (PF): Single joined query across Doctor, User, DoctorSpecialty tables
- Data Flow Out (DF-Out): Search results feed into doctor public profile view
- Audit Trail (ADT): Every search logged with query, specialty, result count and IP
QA Summary:
- Specialty filter in sidebar correctly returns only doctors of selected specialty
- All 10 specialties visible and clickable in sidebar
- Specialty cards on homepage correctly redirect to filtered search results
- Verified badge displays correctly for verified doctors
- Empty state message shown when no results found
- Search audit log entry created for every search action

2. Search by Location (02.02)
Scope Completed:
- Core Functionality + GUI (ET-In): Location input searches city, state and zip code fields
- Field Validation (FV): Empty location gracefully returns all results
- Enrichment (ER): Location displayed as badge on each doctor card
- Cache (CA): Location filter applied on same optimized query as specialty filter
- Connectivity (CN): Location search queries DB correctly across 60 US cities
- Exception Handling (ExHL): Invalid or unknown location returns empty state with message
- Performance (PF): OR query across city, state, zip_code, clinic_address fields
- Audit Trail (ADT): Location search parameter logged in audit trail
QA Summary:
- Searching by city name returns correct doctors in that city
- Searching by state abbreviation returns all doctors in that state
- Searching by ZIP code returns correct results
- Location badge correctly displayed on doctor cards
- Combined specialty + location filter works correctly
- Search bar on homepage location field submits to search page correctly

3. Search by Name (02.03)
Scope Completed:
- Core Functionality + GUI (ET-In): Name search queries first name, last name, clinic name and specialty
- Field Validation (FV): Partial name search supported using ILIKE pattern matching
- Enrichment (ER): Doctor name prominently displayed on result cards
- Cache (CA): Name filter applied on same optimized base query
- Connectivity (CN): Name search queries DB correctly
- Exception Handling (ExHL): No results returns empty state message
- Performance (PF): ILIKE search on indexed name fields
- Audit Trail (ADT): Search query logged with name parameter
QA Summary:
- Partial first name search returns correct matching doctors
- Partial last name search returns correct matching doctors
- Clinic name search returns matching doctors
- Case-insensitive search works correctly
- Combined name + specialty + location filters work together
- Autocomplete dropdown on homepage redirects to search with specialty parameter
- Find Doctors navbar link correctly routes to search page

4. View Doctor Public Profile (02.06)
Scope Completed:
- Core Functionality + GUI (ET-In): Public doctor profile accessible to logged-in patients only
- Doctor Specialty (DS): Specialty name displayed prominently in hero section
- Enrichment (ER): Verified badge, consultation fee, years experience, avg duration displayed
- Cache (CA): Profile loaded via direct doctor ID lookup
- Connectivity (CN): Profile page fetches doctor, user and specialty data correctly
- Exception Handling (ExHL): Invalid doctor ID returns 404, non-patient role redirects
- Performance (PF): Single query to load full doctor profile
- Data Flow In (DF-In): Receives doctor_id from search results page
- Audit Trail (ADT): Every profile view logged with doctor_id and patient user_id
QA Summary:
- Doctor profile page loads correctly from search results View Profile button
- All professional information displayed correctly including license, fee, experience
- Clinic information section visible when clinic data is available
- Verified badge shown for verified doctors
- Pending verification message shown for unverified doctors
- Back to Search link correctly returns to search results
- Book Appointment CTA visible on profile page
- Non-patient users correctly blocked and redirected
- Audit log records every doctor profile view with correct doctor and patient IDs

5. Doctor Data Seeding
Scope Completed:
- 1000 realistic doctor profiles seeded across all 10 specialties
- 60 US cities across all major states represented
- Realistic names, clinic names, bios, fees and addresses generated
- 85% of doctors marked as verified, 15% as pending
- Specialty-specific consultation fees and appointment durations configured
QA Summary:
- All 10 specialties have approximately 100 doctors each
- Search results show realistic diversity across cities and states
- Fee ranges are realistic per specialty
- Doctor bios are professional and specialty-appropriate -->



QA Release Notes - Sprint 2 (Full)
Team 4 : QuickDoc
Date: April 2026

==========================================================
1. Search by Specialty (02.01)
==========================================================
Scope Completed:
- Core Functionality + GUI (ET-In): Specialty filter in sidebar redirects to filtered search results
- Doctor Specialty (DS): All 10 specialties seeded and filterable from sidebar
- Enrichment (ER): Verified badge, specialty badge, experience displayed on each result card
- Cache (CA): Single optimized joined query for performance across 1000+ doctors
- Connectivity (CN): Search results page loads correctly with DB connection
- Exception Handling (ExHL): Empty results handled gracefully with empty state message
- Data Flow Out (DF-Out): Search results feed into doctor public profile view
- Audit Trail (ADT): Every search logged with query, specialty, result count and IP

QA Summary:
- Specialty filter in sidebar correctly returns only doctors of selected specialty
- All 10 specialties visible and clickable in sidebar
- Specialty cards on homepage correctly redirect to filtered search results
- Verified badge displays correctly for verified doctors
- Empty state message shown when no results found
- Search audit log entry created for every search action

==========================================================
2. Search by Location (02.02)
==========================================================
Scope Completed:
- Core Functionality + GUI (ET-In): Location input searches city, state and zip code fields
- Field Validation (FV): Empty location gracefully returns all results
- Enrichment (ER): Location badge displayed on each doctor card
- Cache (CA): Location filter applied on same optimized query as specialty filter
- Connectivity (CN): Location search queries DB correctly across 60 US cities
- Exception Handling (ExHL): Invalid or unknown location returns empty state with message
- Audit Trail (ADT): Location search parameter logged in audit trail

QA Summary:
- Searching by city name returns correct doctors in that city
- Searching by state abbreviation returns all doctors in that state
- Searching by ZIP code returns correct results
- Location badge correctly displayed on doctor cards
- Combined specialty + location filter works correctly
- Search bar on homepage location field submits to search page correctly

==========================================================
3. Search by Name (02.03)
==========================================================
Scope Completed:
- Core Functionality + GUI (ET-In): Name search queries first name, last name, clinic name and specialty
- Field Validation (FV): Partial name search supported using ILIKE pattern matching
- Enrichment (ER): Doctor name prominently displayed on result cards
- Cache (CA): Name filter applied on same optimized base query
- Connectivity (CN): Name search queries DB correctly
- Exception Handling (ExHL): No results returns empty state message
- Audit Trail (ADT): Search query logged with name parameter

QA Summary:
- Partial first name search returns correct matching doctors
- Partial last name search returns correct matching doctors
- Clinic name search returns matching doctors
- Case-insensitive search works correctly
- Combined name + specialty + location filters work together
- Autocomplete dropdown on homepage redirects to search with specialty parameter

==========================================================
4. Add to Favorites (02.04)
==========================================================
Scope Completed:
- Core Functionality + GUI (ET-In): Heart button on doctor profile toggles favorite status
- Client Setup (CS): Favorites tied to patient profile, each patient has independent favorites list
- Connectivity (CN): Favorites saved to favorites table with patient_id and doctor_id
- Data Flow In (DF-In): Receives doctor_id from search results and doctor profile page
- Data Flow Out (DF-Out): Favorites list displayed on patient dashboard with count
- Audit Trail (ADT): Every add/remove favorite logged with action, patient_id, doctor_id, IP
- Cache (CA): Patient favorites loaded once per request for O(1) lookup on search results
- Exception Handling (ExHL): Duplicate favorite handled gracefully, DB errors caught and logged

QA Summary:
- Heart button on doctor profile correctly toggles between favorited and unfavorited
- Toast notification shown on add and remove
- Favorites count updates correctly on patient dashboard stat card
- My Favorite Doctors section on patient dashboard shows saved doctors with View link
- Audit log records ADD_FAVORITE and REMOVE_FAVORITE actions correctly
- Duplicate favorite handled with friendly message
- Non-patient users blocked from adding favorites

==========================================================
5. View Doctor Profile - Enhanced (02.06)
==========================================================
Scope Completed:
- Core Functionality + GUI (ET-In): Public doctor profile accessible to logged-in patients only
- Doctor Specialty (DS): Specialty name displayed prominently in hero section
- Enrichment (ER): Average star rating, review count, verified badge, fee, experience displayed
- Cache (CA): Profile loaded via direct doctor ID lookup, favorites status checked
- Connectivity (CN): Profile page fetches doctor, user, specialty, reviews data correctly
- Data Flow In (DF-In): Receives doctor_id from search results page
- Exception Handling (ExHL): Invalid doctor ID returns 404, non-patient role redirects
- Audit Trail (ADT): Every profile view logged with doctor_id and patient user_id

QA Summary:
- Doctor profile page loads correctly from search results View Profile button
- Average star rating and review count displayed in hero section
- Favorites heart button visible and functional on profile page
- All professional information displayed correctly
- Clinic information section visible when available
- Reviews section shows all patient reviews with star ratings
- Write a Review form visible for patients who have not yet reviewed
- Already reviewed message shown for patients who have submitted a review
- Non-patient users correctly blocked and redirected
- Audit log records every doctor profile view

==========================================================
6. Submit Review (05.01)
==========================================================
Scope Completed:
- Core Functionality + GUI (ET-In): Star rating form on doctor profile for logged-in patients only
- Connectivity (CN): Review saved to reviews table with patient_id, doctor_id, rating, body
- Enrichment (ER): Doctor average rating and review count updated after submission
- Audit Trail (ADT): Every review submission logged with patient_id, doctor_id, rating, IP
- Exception Handling (ExHL): Duplicate review check prevents patient from reviewing same doctor twice

QA Summary:
- Star rating selector works correctly (1-5 stars)
- Review title field optional, body field required (min 10 characters)
- Successful submission shows flash success message
- Review immediately visible in reviews list after submission
- Average rating in doctor hero section updates after new review
- Duplicate review blocked with warning message
- Reviews visible on homepage testimonials section (latest 3 real reviews)
- Review count badge updates on doctor search result cards
- Audit log records SUBMIT_REVIEW action correctly

==========================================================
7. Homepage Dynamic Reviews
==========================================================
Scope Completed:
- Homepage testimonials section now shows real patient reviews from DB
- Latest 3 reviews displayed with star rating, patient name, specialty context
- Verified Review badge shown on each testimonial card
- Falls back to static testimonials if no reviews exist in DB
- Nginx updated to serve homepage through Flask instead of static file

QA Summary:
- Homepage loads correctly through Flask
- Real reviews show with correct patient name, rating and specialty
- Fallback static reviews shown when DB has fewer than 3 reviews
- Page loads without errors

==========================================================
8. Patient Dashboard Enhancements
==========================================================
Scope Completed:
- My Favorite Doctors section added to patient dashboard
- Saved Doctors count shown in stats row
- Find Doctor quick action now links to /search page
- Activity log shows ADD_FAVORITE, REMOVE_FAVORITE, SUBMIT_REVIEW, DOCTOR_SEARCH actions

QA Summary:
- My Favorite Doctors section lists up to 5 saved doctors with specialty and location
- View link on each favorite doctor goes to their public profile
- Saved Doctors count in stats row updates correctly
- Find Doctor button routes to search page correctly
- Activity log shows all correct action types with timestamps