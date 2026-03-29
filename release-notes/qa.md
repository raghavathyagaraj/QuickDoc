
QA Release Notes - Sprint 2

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

