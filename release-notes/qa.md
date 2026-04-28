QA Release Notes - Sprint 3 Week 1
Team 4 - QuickDoc
Date - April 2026


View Available Slots - 03.01
Crosscuts - Core+GUI, ET-In, DS, AS, CN, DF-In, DF-Out, CA, ADT, ExHL


What Was Built

Booking page with calendar and time slot grid
30 min slots auto-generated from doctor weekly schedule
Slots generated for next 6 months - 180 days ahead
Green highlighted dates show available days on calendar
Doctor header shows name, specialty, fee and location
Patient role only - doctors redirected
Audit trail logs every slot view

Test Cases

Click Book Appointment on doctor profile - booking page loads
Calendar shows green dates where doctor has availability
Click a green date - time slots update on right side
Time slots show in 30 min intervals
Past dates shown as grey and not clickable
Doctor with no schedule - warning message shown
Non patient users redirected



Book Appointment - 03.02
Crosscuts - Core+GUI, ET-In, CS, AS, FV, DDV, CC, CN, TZ, DF-In, DF-Out, ADT, CA, ExHL

What Was Built

Three page booking flow - Select Slot then Confirm then Success
Confirmation page shows doctor, date, time, fee, notes field
Success page shows green checkmark with appointment ID
Slot marked as booked immediately after booking
Double booking prevention - same time blocked
Unique constraint on patient plus slot
Audit trail logs every booking

Test Cases

Click time slot - confirmation page loads with correct details
Click Confirm Booking - success page shown
After booking - slot no longer appears in available list
Try booking same slot again - error shown
Try booking at same time as existing appointment - blocked
Non patient users blocked from booking



Patient Dashboard - Upcoming Appointments
Crosscuts - Core+GUI, CN, DF-Out, CA


What Was Built

New Upcoming Appointments section on patient dashboard
Shows next 5 confirmed or pending appointments
Each shows doctor name, specialty, date, time, status
Stats card shows upcoming appointment count
Activity log shows Booked an appointment action

Test Cases

Login as patient with bookings - section visible
Stats card shows correct count
Empty state shown when no upcoming appointments
View link navigates to doctor profile



Button Fixes

Search results Book Appointment button now works
Doctor profile Book Appointment button now works
Patient dashboard Book Visit button now works
Fixed route name from doctor_profile to doctor_public_profile



Database Changes

New table - appointment_slots
New table - appointments
Unique constraint on doctor plus date plus time
Unique constraint on patient plus slot