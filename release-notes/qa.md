QA Release Notes - Sprint 3 Week 3
Team 4 - QuickDoc
Date - May 2026

----------------------------------------------------------
1. Manage Availability - 04.03
   Crosscuts - Core+GUI, ET-In, CS, FV, DDV, CC, CN, DF-In, DF-Out, ADT, ExHL
----------------------------------------------------------

Crosscut Implementation
- Core+GUI - Availability management page with two modes - Single Date block and Date Range block. Toggle buttons switch between modes. Form shows date picker, optional end date for range, and optional reason field. Stats cards show upcoming and past blocked dates count. Blocked dates list shows each date with formatted day name, reason and Unblock button. Red styling indicates blocked status.
- ET-In - All availability routes require login and doctor role only. Patient users redirected. Ownership verified on unblock - doctors can only unblock their own dates.
- CS - Blocked dates tied to doctor profile via doctor_id FK. Each doctor manages independently.
- FV - Date must be in the future - cannot block past dates. For date range end date must be after start date. Maximum 30 days can be blocked at once. Reason field optional with max 255 characters.
- DDV - Duplicate date check before blocking. If date already blocked it is skipped and count reflects only newly blocked dates. Warning shown if all selected dates already blocked.
- CC - Unique constraint uq_doctor_blocked_date on doctor_id plus block_date prevents duplicates at DB level.
- CN - BlockedDate records saved to blocked_dates table with doctor_id FK, block_date, reason. Bulk insert for date ranges in single transaction.
- DF-In - Accessed from doctor dashboard via Manage Availability button.
- DF-Out - Blocked dates should be checked during slot generation to prevent patients from booking on blocked days.
- ADT - Block action logged with action=BLOCK_DATE including dates_blocked count, start date, end date, reason and IP. Unblock logged with action=UNBLOCK_DATE including date and IP.
- ExHL - All DB errors caught with session rollback. Invalid date format returns error. Past date returns error. Range over 30 days returns error. Flash messages for all success and error states.

QA Test Cases
- Login as doctor - navigate to /provider/availability
- Stats cards show 0 upcoming and 0 past blocked dates initially
- Select Single Date mode - pick a future date - click Block - date appears in blocked list
- Select Date Range mode - pick start and end date - click Block - all dates in range appear
- Try blocking a past date - error Cannot block a date in the past
- Try blocking same date twice - warning Selected dates are already blocked
- Try range over 30 days - error Cannot block more than 30 days at once
- Try end date before start date - error End date must be after start date
- Add reason for blocking - reason shows under blocked date
- Click Unblock on a blocked date - date removed from list with success message
- Stats cards update correctly after blocking and unblocking
- Non doctor users redirected to patient dashboard
- Doctor can only unblock their own blocked dates
- Audit log shows BLOCK_DATE and UNBLOCK_DATE entries

----------------------------------------------------------
2. View Reviews - 05.03
   Crosscuts - Core+GUI, ET-In, CS, CN, DF-In, DF-Out, ADT, CA, ExHL
----------------------------------------------------------

Crosscut Implementation
- Core+GUI - Doctor reviews dashboard with three stats cards - Average Rating with star icons, Total Reviews count, 5-Star Reviews count. Rating breakdown bar chart showing distribution from 5 stars to 1 star with color coded bars - green for 5 and 4 stars, yellow for 3, orange for 2, red for 1. All Reviews section showing each review with patient name initial, star rating, optional title, review body and date. Clean teal design consistent with rest of application.
- ET-In - Reviews route requires login and doctor role only. Patient users redirected to patient dashboard.
- CS - Reviews filtered by doctor_id. Each doctor sees only their own reviews.
- CN - Joined query across reviews and patients tables. Reviews ordered by created_at descending showing newest first. Rating breakdown computed from query results.
- DF-In - Accessed from doctor dashboard via My Reviews button.
- DF-Out - Each review shows patient first name and last initial for privacy.
- ADT - Every reviews dashboard view logged with action=VIEW_REVIEWS_DASHBOARD including total_reviews count and IP.
- CA - Rating breakdown computed in single pass over query results. Average rating computed server-side.
- ExHL - Doctor profile not found returns flash error. Empty state shown when no reviews exist.

QA Test Cases
- Login as doctor - navigate to /provider/reviews
- Average Rating stat card shows correct rating with star icons
- Total Reviews stat card shows correct count
- 5-Star Reviews stat card shows correct count
- Rating breakdown shows correct bar widths for each star level
- Color coding correct - green for 5 stars, red for 1 star
- Each review shows patient name as First Name plus Last Initial
- Each review shows correct star rating
- Review title displayed when present
- Review body text displayed correctly
- Reviews ordered by newest first
- Empty state shown when doctor has no reviews
- Non doctor users redirected to patient dashboard
- Audit log shows VIEW_REVIEWS_DASHBOARD entry

----------------------------------------------------------
3. Database Changes
----------------------------------------------------------
- New table - blocked_dates with columns id PK, doctor_id FK, block_date, reason, created_at
- Unique constraint - uq_doctor_blocked_date on doctor_id plus block_date
- Doctor model - added blocked_dates relationship
- Removed duplicate Notification class that caused test failures

----------------------------------------------------------
4. New Routes Added
----------------------------------------------------------
- GET /provider/availability - View and manage blocked dates - 04.03
- POST /provider/availability/block - Block single date or date range - 04.03
- POST /provider/availability/unblock/block_id - Unblock a date - 04.03
- GET /provider/reviews - View reviews dashboard with stats - 05.03

----------------------------------------------------------
5. Doctor Dashboard Updates Needed
----------------------------------------------------------
- Add Manage Availability button linking to /provider/availability
- Add My Reviews button linking to /provider/reviews

----------------------------------------------------------
6. Regression - All Passing
----------------------------------------------------------
Sprint 3 Week 1 and Week 2
- 03.01 View Available Slots - working
- 03.02 Book Appointment - working
- 03.03 Reschedule Booking - working
- 03.04 Cancel Booking - working
- 03.05 View Booking History - working
- 03.06 Send Booking Reminder - working

Sprint 2
- All 8 user stories - working