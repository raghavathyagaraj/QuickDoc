QA Release Notes - Sprint 3 Week 2
Team 4 - QuickDoc
Date - May 2026

----------------------------------------------------------
1. Reschedule Booking - 03.03
   Crosscuts - Core+GUI, ET-In, CS, AS, FV, DDV, CC, CN, TZ, DF-In, DF-Out, ADT, CA, ExHL
----------------------------------------------------------

Crosscut Implementation
- Core+GUI - Two page reschedule flow. First page shows current appointment details with two options - Same Doctor Different Time or Switch to Different Doctor. Second page shows calendar with available slots for the selected doctor. Patient clicks a slot to confirm reschedule instantly.
- ET-In - All reschedule routes require login and patient role only. Doctors redirected to doctor dashboard. Ownership verified - patient can only reschedule their own appointments.
- CS - Reschedule tied to patient profile via patient_id FK. Each patient manages their own appointments independently.
- AS - Old slot marked as is_booked=False when rescheduled freeing it for other patients. New slot marked as is_booked=True immediately. Appointment status remains confirmed after reschedule.
- FV - Only confirmed or pending appointments can be rescheduled. Cannot reschedule within 24 hours of appointment time. New slot must be in the future. New slot must not already be booked.
- DDV - System checks if new slot was booked by someone else between page load and confirmation. Race condition handled with is_booked check before commit.
- CC - Unique constraint uq_patient_slot prevents duplicate booking at DB level.
- CN - Appointment record updated with new doctor_id, slot_id and appt_datetime in single atomic transaction. Old slot and new slot updated in same commit.
- TZ - All times displayed in 12-hour AM/PM format. Stored as UTC in database.
- DF-In - Receives appointment_id from booking history page. Receives new slot_id from reschedule slot picker.
- DF-Out - Updated appointment visible in booking history. Notifications sent to both patient and doctor.
- ADT - Reschedule logged with action=RESCHEDULE_APPOINTMENT including old date, new date, old doctor_id, new doctor_id and IP address.
- CA - Slots generated in bulk if not already existing. Available dates loaded as distinct query for calendar.
- ExHL - All DB errors caught with session rollback. Invalid appointment_id returns 404. Unauthorized access returns flash error. Already booked slot shows warning message.

QA Test Cases
- Login as patient - go to booking history - click Reschedule on a confirmed appointment
- Reschedule page shows current appointment details correctly
- Click Same Doctor Different Time - calendar loads with available dates
- Click a green date - available 30 min slots shown
- Click a slot - appointment rescheduled immediately with success message
- Old slot now available for other patients to book
- New slot no longer appears in available slots
- Booking history shows updated date and time
- Notification received - Appointment Rescheduled
- Doctor also receives notification about reschedule
- Try rescheduling appointment less than 24 hours away - error shown
- Try rescheduling a cancelled appointment - error shown
- Click Switch to Different Doctor - redirected to search page
- Audit log shows RESCHEDULE_APPOINTMENT with old and new details
- Non patient users blocked from rescheduling

----------------------------------------------------------
2. Cancel Booking - 03.04
   Crosscuts - Core+GUI, ET-In, CS, AS, FV, CN, DF-In, DF-Out, ADT, ExHL
----------------------------------------------------------

Crosscut Implementation
- Core+GUI - Cancel confirmation page with red warning icon. Shows appointment details including doctor name, date, time and current status. Warning box states action cannot be undone. Optional reason for cancellation textarea. Two buttons - Keep Appointment and Cancel Appointment.
- ET-In - Cancel routes require login and patient role only. Ownership verified - patient can only cancel their own appointments.
- CS - Cancellation tied to patient profile. Each patient cancels independently.
- AS - Slot marked as is_booked=False when cancelled. Slot becomes available for other patients immediately. Appointment status changed to cancelled.
- FV - Only confirmed or pending appointments can be cancelled. Cannot cancel within 24 hours of appointment time. Cancellation reason optional with max 500 characters.
- CN - Appointment status updated to cancelled and slot is_booked set to False in single atomic DB transaction.
- DF-In - Receives appointment_id from booking history page Reschedule or Cancel buttons.
- DF-Out - Cancelled appointment visible in booking history under Cancelled tab. Notifications sent to both patient and doctor about cancellation.
- ADT - Cancellation logged with action=CANCEL_APPOINTMENT including doctor_id, appointment date, cancellation reason and IP address.
- ExHL - All DB errors caught with session rollback. Invalid appointment_id returns 404. Unauthorized access returns flash error. Already cancelled appointment shows warning.

QA Test Cases
- Login as patient - go to booking history - click Cancel on a confirmed appointment
- Cancel confirmation page shows correct doctor name, date, time and status
- Warning message displayed - This action cannot be undone
- Type optional cancellation reason
- Click Cancel Appointment - appointment cancelled with success message
- Booking history shows appointment with Cancelled status badge
- Cancelled tab count increases by 1
- Upcoming tab count decreases by 1
- The time slot is now available for other patients to book
- Patient receives Appointment Cancelled notification
- Doctor receives notification about cancellation
- Try cancelling appointment less than 24 hours away - error Cannot cancel within 24 hours
- Try cancelling an already cancelled appointment - error shown
- Click Keep Appointment - redirected back to booking history without cancelling
- Audit log shows CANCEL_APPOINTMENT with reason and details
- Non patient users blocked from cancelling

----------------------------------------------------------
3. View Booking History - 03.05
   Crosscuts - Core+GUI, ET-In, CS, CN, DF-In, DF-Out, ADT, CA, ExHL
----------------------------------------------------------

Crosscut Implementation
- Core+GUI - Full appointment history page with tab filters - All, Upcoming, Past, Cancelled. Each tab shows count badge. Each appointment card shows date calendar icon, doctor name, specialty, time range, clinic location and status badge color coded as green for Confirmed, yellow for Pending, red for Cancelled, blue for Completed. Upcoming appointments show Reschedule and Cancel action buttons. Empty state with link to find a doctor.
- ET-In - History route requires login and patient role only. Doctors redirected.
- CS - History filtered by patient_id. Each patient sees only their own appointments.
- CN - Joined query across appointments, doctors, doctor_specialties and appointment_slots tables. Filtered by status based on selected tab. Ordered by appointment datetime descending showing newest first.
- DF-In - Receives status filter from URL query parameter. Links from patient dashboard upcoming appointments section.
- DF-Out - Reschedule button links to reschedule flow. Cancel button links to cancel confirmation. View Doctor button links to doctor public profile.
- ADT - Every history view logged with action=VIEW_BOOKING_HISTORY including filter type and IP address.
- CA - Separate count queries for each tab to show badge counts. Main query limited to selected filter for performance.
- ExHL - Patient profile not found returns flash error. Empty results show friendly empty state message.

QA Test Cases
- Login as patient - navigate to /booking/history
- All tab shows total count of all appointments
- Upcoming tab shows only future confirmed and pending appointments
- Past tab shows only past confirmed and completed appointments
- Cancelled tab shows only cancelled appointments
- Each tab count badge shows correct number
- Appointment card shows correct doctor name and specialty
- Appointment card shows correct date with calendar icon
- Appointment card shows correct time range
- Appointment card shows clinic name and city
- Confirmed appointments show green badge
- Cancelled appointments show red badge
- Upcoming appointments show Reschedule, Cancel and View Doctor buttons
- Past and cancelled appointments do not show Reschedule or Cancel buttons
- Click Reschedule - navigates to reschedule flow
- Click Cancel - navigates to cancel confirmation
- Click View Doctor - navigates to doctor public profile
- Empty state shown when no appointments exist
- Empty state shows link to find a doctor
- Non patient users redirected to their dashboard
- Audit log shows VIEW_BOOKING_HISTORY entry

----------------------------------------------------------
4. Send Booking Reminder - 03.06
   Crosscuts - Core+GUI, ET-In, CS, CN, DF-In, DF-Out, ADT, CA, ExHL
----------------------------------------------------------

Crosscut Implementation
- Core+GUI - Full notifications page showing all in-app notifications. Each notification card shows icon color coded by type - green for booking, red for cancellation, blue for reschedule, yellow for reminder. Shows title, message, timestamp and Mark read button for unread notifications. Unread notifications highlighted with teal left border. Header shows unread count badge. Mark all read button clears all unread notifications at once.
- ET-In - Notifications route requires login. Users can only see their own notifications. Mark read verifies ownership before updating.
- CS - Notifications tied to user_id. Each user has independent notification list.
- CN - Notifications saved to notifications table with user_id FK, title, message, type, is_read flag, optional link. Queries ordered by created_at descending showing newest first. Limited to 20 most recent.
- DF-In - Notifications automatically created when patient books appointment, reschedules appointment or cancels appointment. Reminder notifications generated for appointments within next 24 hours.
- DF-Out - Booking confirmation sends notification to patient and doctor. Cancel sends notification to patient and doctor. Reschedule sends notification to patient and doctor. Click notification link navigates to booking history.
- ADT - Notification creation logged implicitly through booking, cancel and reschedule audit entries.
- CA - Unread count query separate from main list for header badge. Bulk update for mark all read operation.
- ExHL - Invalid notification_id returns 404. Unauthorized notification access returns error. All DB errors caught.

Notification Types
- booking - Sent when appointment is confirmed. Sent to both patient and doctor.
- cancellation - Sent when appointment is cancelled. Sent to both patient and doctor.
- reschedule - Sent when appointment is rescheduled. Sent to both patient and new doctor.
- reminder - Sent 24 hours before appointment. Sent to patient only.

QA Test Cases
- Book an appointment - check notifications page - booking notification appears
- Cancel an appointment - check notifications - cancellation notification appears
- Reschedule an appointment - check notifications - reschedule notification appears
- Login as doctor who received a booking - doctor sees notification
- Unread notifications show teal left border highlight
- Unread count badge shows correct number in header
- Click Mark read on a notification - notification no longer highlighted
- Click Mark all read - all notifications marked as read
- Unread count badge disappears after marking all read
- Notification shows correct icon - green calendar for booking, red X for cancel, blue arrows for reschedule, yellow bell for reminder
- Notification shows correct title, message and timestamp
- Empty state shown when no notifications exist
- Non logged in users redirected to login page
- User can only see their own notifications
- Try marking another users notification as read - error shown

----------------------------------------------------------
5. Patient Dashboard Updates
----------------------------------------------------------

Updates Made
- Upcoming Appointments section links to booking history
- Book Visit button links to search page
- Activity log shows RESCHEDULE_APPOINTMENT and CANCEL_APPOINTMENT actions
- Notifications bell icon can be added to navbar linking to /booking/notifications

----------------------------------------------------------
6. Database Changes
----------------------------------------------------------
- New table - notifications with columns notification_id PK, user_id FK, title, message, type, is_read, link, created_at
- User model - added notifications relationship
- No changes to existing tables - all Sprint 3 Week 1 tables remain unchanged

----------------------------------------------------------
7. New Routes Added
----------------------------------------------------------
- GET /booking/history - View all appointments with tab filters - 03.05
- GET /booking/reschedule/appointment_id - Choose reschedule option - 03.03
- GET /booking/reschedule/appointment_id/doctor/doctor_id - Pick new slot - 03.03
- POST /booking/reschedule/appointment_id/confirm/slot_id - Confirm reschedule - 03.03
- GET /booking/cancel/appointment_id - Cancel confirmation page - 03.04
- POST /booking/cancel/appointment_id/submit - Submit cancellation - 03.04
- GET /booking/notifications - View all notifications - 03.06
- POST /booking/notifications/read/notif_id - Mark notification as read - 03.06
- POST /booking/notifications/read-all - Mark all notifications as read - 03.06

----------------------------------------------------------
8. Sprint 3 Week 1 Regression - All Passing
----------------------------------------------------------
- 03.01 View Available Slots - working
- 03.02 Book Appointment - working
- Patient Dashboard Upcoming Appointments - working
- Book Appointment button on search results - working
- Book Appointment button on doctor profile - working

----------------------------------------------------------
9. Sprint 2 Regression - All Passing
----------------------------------------------------------
- Search by Specialty - working
- Search by Location - working
- Search by Name - working
- Add to Favorites - working
- View Doctor Profile - working
- Submit Review - working
- Doctor Profile Edit - working
- Schedule Management - working
- Homepage Dynamic Reviews - working