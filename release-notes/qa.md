QA Release Notes - Sprint 2 (Complete)
Team 4 : QuickDoc
Date: April 2026

==========================================================
1. Search by Specialty (02.01)
   Crosscuts: Core+GUI, ET-In, DS, FV, ER, CN, CA, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Specialty filter sidebar with 10 clickable specialties, doctor result cards with badges
- ET-In: Route /search requires @login_required, patient role only, doctors redirected
- DS: All 10 specialties loaded from doctor_specialties table via SQLAlchemy join
- FV: Empty specialty returns all results, invalid specialty shows empty state, input sanitized
- ER: Verified badge, specialty badge, location badge, experience years on each card
- CN: Single joined query across Doctor + User + DoctorSpecialty tables via PostgreSQL
- CA: Base query reused for all filter combinations, avoids N+1 problem
- ExHL: Try/except wraps search query, DB errors logged, user-friendly error shown

QA Test Cases:
- Click each specialty in sidebar — correct filtered results returned
- Empty specialty — shows all doctors
- Verified badge shows for verified doctors only
- Empty state message when no doctors match
- Non-patient users blocked from accessing search

==========================================================
2. Search by Location (02.02)
   Crosscuts: Core+GUI, ET-In, FV, ER, CN, CA, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Location input field in search bar, location badge on doctor cards
- ET-In: Same @login_required on /search, patient role validated
- FV: Empty location returns all, partial city via ILIKE, state abbreviation supported, ZIP code search
- ER: Location badge on each card formatted as City, State
- CN: OR query across city, state, zip_code, clinic_address columns
- CA: Location filter applied on same base query as specialty filter
- ExHL: Unknown location returns empty state message, DB errors caught

QA Test Cases:
- Search "New York" — returns correct doctors
- Search "NY" — returns all New York state doctors
- Search invalid city — empty state shown
- Combined specialty + location filter works
- Location badge displays correctly on cards

==========================================================
3. Search by Name (02.03)
   Crosscuts: Core+GUI, ET-In, FV, ER, CN, CA, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Name search input queries first_name, last_name, clinic_name, specialty_name
- ET-In: Patient role required, session validated
- FV: ILIKE pattern matching for case-insensitive partial search, input stripped
- ER: Doctor full name displayed prominently, specialty and verified badges
- CN: ILIKE OR query across 4 name fields via PostgreSQL
- CA: Name filter combined with specialty + location on same base query
- ExHL: No results shows friendly message, gibberish input handled

QA Test Cases:
- Search "Smith" — returns matching doctors
- Search "smi" — partial match works
- Case-insensitive — "SMITH" and "smith" return same results
- Combined name + specialty + location filters work
- No results shows empty state message

==========================================================
4. Add to Favorites (02.04)
   Crosscuts: Core+GUI, ET-In, CS, CN, DF-In, DF-Out, ADT, CA, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Heart icon button on doctor profile page, toggles filled/outline state
- ET-In: POST /social/favorite/<doctor_id> requires @login_required, patient role checked
- CS: Favorites tied to patient profile via patient_id FK, each patient has independent list
- CN: Favorite records saved to favorites table, unique constraint on patient+doctor
- DF-In: Receives doctor_id from doctor profile page via POST request
- DF-Out: Favorites list displayed on patient dashboard, count shown in stats card
- ADT: Every add/remove logged with action=ADD_FAVORITE or REMOVE_FAVORITE, patient_id, doctor_id, IP
- CA: Patient favorites loaded once per search request as set for O(1) lookup
- ExHL: Duplicate favorite returns friendly message, DB errors caught with rollback

QA Test Cases:
- Click heart on doctor profile — toast shows "Added to favorites"
- Click again — toast shows "Removed from favorites"
- Check patient dashboard — favorites count updates correctly
- My Favorite Doctors section shows saved doctors with View link
- Non-patient users get 403 error
- Audit log shows ADD_FAVORITE and REMOVE_FAVORITE entries

==========================================================
5. View Doctor Profile - Enhanced (02.06)
   Crosscuts: Core+GUI, ET-In, DS, ER, CN, DF-In, CA, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Full doctor profile page with hero section, bio, professional info, clinic info, reviews
- ET-In: Route /search/doctor/<id> requires @login_required, patient role only
- DS: Specialty name displayed in hero section and badges
- ER: Average star rating computed from reviews, review count badge, verified badge, fee, experience
- CN: Doctor + User + Specialty + Reviews loaded from PostgreSQL via joins
- DF-In: Receives doctor_id from search results View Profile link
- CA: Favorite status checked with single query, reviews loaded with patient join
- ExHL: Invalid doctor_id returns 404, non-patient role redirected

QA Test Cases:
- Click View Profile from search — profile page loads correctly
- Average rating and review count shown in hero section
- Heart button shows correct favorite status
- All professional info displayed (license, fee, experience, duration)
- Clinic info section shown when data available
- Reviews section shows all patient reviews with stars
- Write a Review form visible for patients who haven't reviewed yet
- "Already reviewed" message for patients who submitted review
- Invalid doctor ID shows 404 page

==========================================================
6. Submit Review (05.01)
   Crosscuts: Core+GUI, ET-In, CN, ER, ADT, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Star rating selector (1-5), optional title field, required body field on doctor profile
- ET-In: POST /social/review/<doctor_id> requires @login_required, patient role only
- CN: Review saved to reviews table with patient_id, doctor_id, rating, title, body
- ER: Doctor avg_rating and review_count properties updated dynamically after submission
- ADT: Review submission logged with action=SUBMIT_REVIEW, patient_id, doctor_id, rating, IP
- ExHL: Duplicate review blocked with warning, rating validated 1-5, body min 10 chars, max 1000 chars

QA Test Cases:
- Select 5 stars, type review body (min 10 chars) — submits successfully
- Review appears in Patient Reviews section immediately
- Average rating in hero section updates
- Try submitting second review for same doctor — "already reviewed" warning
- Empty rating — error message shown
- Body less than 10 chars — error message shown
- Reviews show on homepage testimonials section (latest 3)
- Audit log shows SUBMIT_REVIEW entry

==========================================================
7. Add Doctor Profile (04.01)
   Crosscuts: Core+GUI, ET-In, CS, DS, FV, ER, CN, DF-Out, ADT, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Full profile edit form with 3 sections — Personal Info, Professional Details, Clinic Info
- ET-In: Route /provider/profile/edit requires @login_required, doctor role only, patients redirected
- CS: Profile completion percentage bar computed from 9 key fields, shown at top of form
- DS: Specialty dropdown populated from doctor_specialties table, doctor can change specialty
- FV: First name, last name, phone required. Fee must be positive. Experience 0-60. Bio max 500 chars.
- ER: Profile completion percentage computed. License number shown as read-only. Verified status displayed.
- CN: Profile updates saved to doctors table via SQLAlchemy ORM, atomic DB transaction
- DF-Out: Updated profile data immediately reflected in search results and doctor public profile
- ADT: Profile update logged with action=UPDATE_DOCTOR_PROFILE, doctor_id, completion %, IP
- ExHL: All DB errors caught with session rollback. Validation errors shown as flash messages. Success redirects to dashboard.

QA Test Cases:
- Login as doctor — navigate to /provider/profile/edit
- Profile completion bar shows correct percentage
- Update bio — saves successfully, flash success shown
- Update consultation fee to 250 — saves correctly
- Enter negative fee (-50) — error: "cannot be negative"
- Clear first name and submit — error: "required"
- Type bio over 500 chars — error: "under 500 characters"
- Change specialty from dropdown — saves correctly
- License number field is read-only and cannot be modified
- Fill clinic name, address, city, state, zip — all save correctly
- Non-doctor users redirected to patient dashboard
- Audit log shows UPDATE_DOCTOR_PROFILE entry
- Updated data immediately visible in patient search results

==========================================================
8. Update Schedule (04.02)
   Crosscuts: Core+GUI, ET-In, CS, DS, AS, FV, DDV, DDD, CC, CN, TZ, DF-In, DF-Out, ADT, CA, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Weekly schedule grid with 7 days, add slot form, delete slot buttons, stats cards
- ET-In: Route /provider/schedule requires @login_required, doctor role only
- CS: Schedule tied to doctor profile via doctor_id FK, each doctor has independent schedule
- DS: Avg appointment duration loaded from doctor specialty config, shown in stats
- AS: Time slots define doctor availability, feeds into appointment booking in Sprint 3
- FV: Day, start time, end time required. End time must be after start time. Invalid time format rejected.
- DDV: Overlapping time slots detected by comparing start/end times of existing slots on same day
- DDD: Default appointment duration auto-loaded from doctor profile (specialty-specific)
- CC: Unique constraint uq_doctor_day_time on (doctor_id, day_of_week, start_time) at DB level
- CN: Schedule slots saved to schedules table via SQLAlchemy ORM
- TZ: Time inputs in 24-hour format, displayed as 12-hour AM/PM format
- DF-In: Receives doctor_id from current logged-in user session
- DF-Out: Schedule data available for patient appointment booking feature in Sprint 3
- ADT: Add slot logged as ADD_SCHEDULE_SLOT, delete logged as DELETE_SCHEDULE_SLOT with day, times, IP
- CA: Schedule slots loaded once per request, grouped by day_of_week for efficient rendering
- ExHL: DB errors caught with rollback. Ownership verified before delete. Flash messages for all errors.

QA Test Cases:
- Login as doctor — navigate to /provider/schedule
- Stats cards show 0 total slots, 0 active days initially
- Add Monday 09:00-17:00 — green chip shows "09:00 AM - 05:00 PM"
- Add Tuesday 10:00-16:00 — shows on Tuesday row
- Stats update to 2 total slots, 2 active days
- Try adding Monday 08:00-10:00 — error: "overlaps with existing slot"
- Try adding Monday 17:00-09:00 — error: "End time must be after start"
- Try adding without selecting day — error: "required"
- Days with slots show green background, empty days show "No slots set — Day off"
- Click ✕ on a slot — slot removed, success message shown
- Add multiple non-overlapping slots on same day — all display correctly
- Non-doctor users redirected to patient dashboard
- Audit log shows ADD_SCHEDULE_SLOT and DELETE_SCHEDULE_SLOT entries
- Doctor can only delete their own schedule slots (ownership check)

==========================================================
9. Homepage Dynamic Reviews
==========================================================

Scope:
- Homepage testimonials section shows real patient reviews from DB
- Latest 3 reviews displayed with star rating, patient name, specialty
- Verified Review badge on each card
- Falls back to static testimonials if fewer than 3 reviews

QA Test Cases:
- Homepage loads through Flask at http://18.217.96.211
- Real reviews show with correct patient name and rating
- Fallback static reviews shown when DB has fewer than 3

==========================================================
10. Patient Dashboard Enhancements
==========================================================

Scope:
- My Favorite Doctors section with View links
- Saved Doctors count in stats row
- Find Doctor quick action links to /search
- Activity log shows favorites, reviews and search actions

QA Test Cases:
- Favorites section shows saved doctors with specialty and location
- Count in stats card matches actual favorites
- Activity log shows correct action types with timestamps

==========================================================
11. Database Changes
==========================================================
- New table: schedules (id PK, doctor_id FK, day_of_week, start_time, end_time, is_active, created_at, updated_at)
- Unique constraint: uq_doctor_day_time on (doctor_id, day_of_week, start_time)
- Doctor model: added profile_completion property, schedules relationship
- 1000 doctors seeded across 10 specialties and 60 US cities