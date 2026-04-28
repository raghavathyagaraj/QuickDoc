QA Release Notes - Sprint 3 Week 1
Team 4 : QuickDoc
Date: April 2026

==========================================================
1. View Available Slots (03.01)
   Crosscuts: Core+GUI, ET-In, DS, AS, CN, DF-In, DF-Out, CA, ADT, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Booking page with interactive JavaScript calendar on left and time slot grid on right. Doctor header shows name, specialty, fee and location. Green highlighted dates indicate availability.
- ET-In: Route /booking/book/<doctor_id> requires @login_required, patient role only. Doctors redirected to doctor dashboard.
- DS: Doctor specialty displayed in header badge. Slot duration fixed at 30 minutes per industry standard.
- AS: 30-minute appointment slots auto-generated from doctor's weekly recurring schedule template (04.02). Slots generated for next 6 months (180 days).
- CN: Slots saved to appointment_slots table with doctor_id FK, schedule_id FK, slot_date, start_time, end_time. Unique constraint on doctor + date + time.
- DF-In: Receives doctor_id from doctor profile Book Appointment button or search results Book button.
- DF-Out: Selected slot feeds into booking confirmation page (03.02).
- CA: Slots generated in bulk using bulk_save_objects. Existing slots checked via set lookup to avoid duplicates. Available dates loaded as distinct query for calendar.
- ADT: Every slot view logged with action=VIEW_AVAILABLE_SLOTS, doctor_id, selected date, slots count, IP address.
- ExHL: Doctor with no schedule shows warning "Doctor has not set availability yet" and redirects to profile. Invalid date defaults to tomorrow. Past slots not shown. DB errors caught with try/except.

QA Test Cases:
- Login as patient — click Book Appointment on doctor profile — booking page loads
- Click Book Appointment on search results page — booking page loads
- Calendar shows green dates where doctor has availability
- Click a green date — time slots update on right side
- Time slots show in 30-minute intervals e.g. 9:00 AM, 9:30 AM, 10:00 AM
- Click Prev/Next month buttons — calendar navigates correctly
- Past dates shown as grey and not clickable
- Dates with no availability not highlighted
- Doctor with no schedule — warning message shown, redirected to profile
- Non-patient users redirected to their dashboard
- Doctor header shows correct name, specialty badge and consultation fee
- Existing appointments with this doctor shown as warning at top
- Audit log shows VIEW_AVAILABLE_SLOTS entry

==========================================================
2. Book Appointment (03.02)
   Crosscuts: Core+GUI, ET-In, CS, AS, FV, DDV, CC, CN, TZ, DF-In, DF-Out, ADT, CA, ExHL
==========================================================

Crosscut Implementation:
- Core+GUI: Three-page booking flow — Select Slot → Confirm Details → Success Page. Confirmation page shows doctor name, specialty, date, time, duration, location, consultation fee and optional notes field. Success page shows green checkmark with all appointment details and appointment ID.
- ET-In: All booking routes require @login_required, patient role only. Doctor role redirected.
- CS: Appointment tied to patient profile via patient_id FK. Each patient books independently.
- AS: Slot marked as is_booked=True immediately after booking. Booked slots no longer appear in available slots list. Appointment status set to "confirmed" on creation.
- FV: Slot ownership verified — slot must belong to the correct doctor. Slot must not be already booked. Slot must be in the future — past slots rejected. Notes field optional, max 500 characters.
- DDV: Patient cannot book two appointments at the same date and time. System checks for conflicting confirmed/pending appointments before allowing booking.
- CC: Unique constraint uq_patient_slot on (patient_id, slot_id) prevents duplicate bookings at DB level.
- CN: Appointment saved to appointments table with patient_id, doctor_id, slot_id, appt_datetime, status, notes. Slot is_booked flag updated in same transaction.
- TZ: Appointment datetime stored as UTC. Displayed in 12-hour AM/PM format on all pages.
- DF-In: Receives doctor_id and slot_id from slot selection on view slots page.
- DF-Out: Confirmed appointment visible on patient dashboard Upcoming Appointments section. Appointment data available for doctor dashboard in future sprint.
- ADT: Booking logged with action=BOOK_APPOINTMENT, appointment_id, doctor_id, slot_date, start_time, end_time, IP address.
- CA: Slot availability checked with single query. Transaction commits appointment and slot update atomically.
- ExHL: Already booked slot shows warning "This slot was just booked by another patient". Invalid slot_id returns 404. Slot not belonging to doctor returns error. Past slot returns error. DB errors caught with session rollback. All errors shown as flash messages.

QA Test Cases:
- Click a time slot on booking page — confirmation page loads
- Confirmation page shows correct doctor name, specialty, date, time, duration
- Consultation fee displayed correctly
- Patient name shown correctly
- Type optional notes — saves correctly
- Click Confirm Booking — success page shown with green checkmark
- Appointment ID displayed on success page
- Go to Dashboard button works — redirects to patient dashboard
- View Doctor button works — redirects to doctor profile
- After booking — slot no longer appears in available slots list
- Try booking same slot again — error "This slot has already been booked"
- Try booking slot at same time as existing appointment — error "You already have an appointment at this time"
- Try booking a past slot — error "Cannot book a slot in the past"
- Non-patient users blocked from booking
- Audit log shows BOOK_APPOINTMENT entry with correct details

==========================================================
3. Patient Dashboard — Upcoming Appointments Section
   Crosscuts: Core+GUI, CN, DF-Out, CA
==========================================================

Crosscut Implementation:
- Core+GUI: New Upcoming Appointments section added between My Favorite Doctors and Recent Activity. Each appointment shows doctor name, specialty, date, time and status with teal dot indicator. Stats row updated — Payment Method replaced with Upcoming Appointments count.
- CN: Appointments loaded via joined query across appointments, doctors, doctor_specialties and appointment_slots tables. Filtered for future confirmed/pending appointments only.
- DF-Out: View link on each appointment navigates to doctor public profile.
- CA: Limited to 5 upcoming appointments for performance. Count query separate for stats card.

QA Test Cases:
- Login as patient with booked appointments — Upcoming Appointments section visible
- Stats card shows correct upcoming appointment count
- Each appointment shows doctor name, specialty, date, time and status
- View link navigates to correct doctor profile
- Empty state shown when no upcoming appointments — "Book your first appointment" link works
- Activity log shows "Booked an appointment" and "Viewed available slots" actions
- Past appointments do not appear in upcoming section
- Cancelled appointments do not appear in upcoming section

==========================================================
4. Book Appointment Button Fixes
==========================================================

Fixes Applied:
- Search results page: Book Appointment button now links to /booking/book/<doctor_id> instead of #
- Doctor public profile page: Book Appointment button now links to /booking/book/<doctor_id> instead of #
- Patient dashboard: Book Visit quick action now links to /search instead of Coming soon
- All booking templates: Fixed route name from search.doctor_profile to search.doctor_public_profile

QA Test Cases:
- Search results — click Book Appointment — booking page loads correctly
- Doctor profile — click Book Appointment — booking page loads correctly
- Patient dashboard — click Book Visit — search page loads correctly

==========================================================
5. Database Changes
==========================================================
- New table: appointment_slots (slot_id PK, doctor_id FK, schedule_id FK, slot_date, start_time, end_time, is_booked, created_at)
- Unique constraint: uq_doctor_date_time on (doctor_id, slot_date, start_time)
- New table: appointments (appointment_id PK, patient_id FK, doctor_id FK, slot_id FK, appt_datetime, status, notes, created_at, updated_at)
- Unique constraint: uq_patient_slot on (patient_id, slot_id)
- Patient model: added appointments relationship
- Doctor model: added slots and appointments relationships
- Schedule model: added slots relationship
