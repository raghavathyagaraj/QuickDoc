import logging
from datetime import datetime, timedelta, date, time
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.backend import db
from src.backend.models.user import Doctor, Patient, Schedule, AppointmentSlot, Appointment, DoctorSpecialty
from src.backend.utils.audit import log_audit

logger = logging.getLogger(__name__)
booking_bp = Blueprint("booking", __name__)

SLOT_DURATION_MINUTES = 30
BOOKING_WINDOW_DAYS = 180  # 6 months


def generate_slots_for_doctor(doctor_id):
    """Generate 30-min appointment slots from weekly schedule for next 6 months.
    Only generates slots that don't already exist in DB."""

    schedules = Schedule.query.filter_by(doctor_id=doctor_id, is_active=True).all()
    if not schedules:
        return 0

    today = date.today()
    end_date = today + timedelta(days=BOOKING_WINDOW_DAYS)

    # Map day names to weekday numbers
    day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
               "Friday": 4, "Saturday": 5, "Sunday": 6}

    # Get all existing slot dates+times for this doctor to avoid duplicates
    existing = set()
    existing_slots = AppointmentSlot.query.filter(
        AppointmentSlot.doctor_id == doctor_id,
        AppointmentSlot.slot_date >= today
    ).all()
    for s in existing_slots:
        existing.add((s.slot_date, s.start_time))

    new_slots = []
    current = today + timedelta(days=1)  # start from tomorrow

    while current <= end_date:
        weekday = current.weekday()
        for sched in schedules:
            if day_map.get(sched.day_of_week) != weekday:
                continue

            # Generate 30-min slots within this schedule window
            slot_start = datetime.combine(current, sched.start_time)
            slot_end_limit = datetime.combine(current, sched.end_time)

            while slot_start + timedelta(minutes=SLOT_DURATION_MINUTES) <= slot_end_limit:
                s_time = slot_start.time()
                e_time = (slot_start + timedelta(minutes=SLOT_DURATION_MINUTES)).time()

                if (current, s_time) not in existing:
                    new_slots.append(AppointmentSlot(
                        doctor_id=doctor_id,
                        schedule_id=sched.id,
                        slot_date=current,
                        start_time=s_time,
                        end_time=e_time,
                        is_booked=False
                    ))
                    existing.add((current, s_time))

                slot_start += timedelta(minutes=SLOT_DURATION_MINUTES)

        current += timedelta(days=1)

    if new_slots:
        db.session.bulk_save_objects(new_slots)
        db.session.commit()

    return len(new_slots)


# ── 03.01 View Available Slots ────────────────────────────────────────────

@booking_bp.route("/book/<int:doctor_id>", methods=["GET"])
@login_required
def view_available_slots(doctor_id):
    """ET-In: patient only. Generates slots from schedule, shows calendar."""
    if current_user.role != "patient":
        flash("Only patients can book appointments.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    if not patient:
        flash("Patient profile not found.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    # Check if doctor has any schedule set
    schedules = Schedule.query.filter_by(doctor_id=doctor_id, is_active=True).all()
    if not schedules:
        flash("This doctor has not set their availability yet.", "warning")
        return redirect(url_for("search.doctor_profile", doctor_id=doctor_id))

    # Generate slots if needed
    try:
        new_count = generate_slots_for_doctor(doctor_id)
        if new_count > 0:
            logger.info(f"Generated {new_count} new slots for doctor {doctor_id}")
    except Exception as exc:
        logger.error(f"Slot generation failed: {exc}", exc_info=True)

    # Get selected date from query param or default to tomorrow
    selected_date_str = request.args.get("date", "")
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today() + timedelta(days=1)
    else:
        selected_date = date.today() + timedelta(days=1)

    # Get available (unbooked) slots for selected date
    available_slots = AppointmentSlot.query.filter_by(
        doctor_id=doctor_id,
        slot_date=selected_date,
        is_booked=False
    ).order_by(AppointmentSlot.start_time).all()

    # Get dates that have available slots for next 6 months (for calendar)
    today = date.today()
    available_dates = db.session.query(AppointmentSlot.slot_date)\
        .filter(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.is_booked == False,
            AppointmentSlot.slot_date > today,
            AppointmentSlot.slot_date <= today + timedelta(days=BOOKING_WINDOW_DAYS)
        )\
        .distinct()\
        .order_by(AppointmentSlot.slot_date)\
        .all()
    available_dates = [d[0] for d in available_dates]

    # Get patient's existing appointments with this doctor
    existing_appts = Appointment.query.filter_by(
        patient_id=patient.id,
        doctor_id=doctor_id
    ).filter(Appointment.status.in_(["confirmed", "pending"])).all()

    # ADT
    log_audit(
        action="VIEW_AVAILABLE_SLOTS",
        entity_type="doctor",
        entity_id=doctor_id,
        user_id=current_user.id,
        details={"date": str(selected_date), "slots_count": len(available_slots),
                 "ip": request.remote_addr}
    )

    return render_template("booking/view_slots.html",
                           doctor=doctor,
                           patient=patient,
                           selected_date=selected_date,
                           available_slots=available_slots,
                           available_dates=available_dates,
                           existing_appts=existing_appts)


# ── 03.02 Book Appointment ────────────────────────────────────────────────

@booking_bp.route("/book/<int:doctor_id>/confirm/<int:slot_id>", methods=["GET"])
@login_required
def confirm_booking(doctor_id, slot_id):
    """Shows confirmation page before booking."""
    if current_user.role != "patient":
        flash("Only patients can book appointments.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    slot = AppointmentSlot.query.get_or_404(slot_id)

    # ExHL — Verify slot belongs to this doctor
    if slot.doctor_id != doctor_id:
        flash("Invalid slot selected.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id))

    # ExHL — Verify slot is not already booked
    if slot.is_booked:
        flash("This slot has already been booked by another patient.", "warning")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id,
                                date=str(slot.slot_date)))

    # ExHL — Verify slot is in the future
    slot_datetime = datetime.combine(slot.slot_date, slot.start_time)
    if slot_datetime <= datetime.now():
        flash("Cannot book a slot in the past.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id))

    return render_template("booking/confirm_booking.html",
                           doctor=doctor,
                           patient=patient,
                           slot=slot)


@booking_bp.route("/book/<int:doctor_id>/submit/<int:slot_id>", methods=["POST"])
@login_required
def submit_booking(doctor_id, slot_id):
    """FV: validates everything. CC: unique constraint. ADT: logged."""
    if current_user.role != "patient":
        flash("Only patients can book appointments.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    slot = AppointmentSlot.query.get_or_404(slot_id)

    # FV — Verify slot belongs to doctor
    if slot.doctor_id != doctor_id:
        flash("Invalid slot selected.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id))

    # FV — Verify not already booked
    if slot.is_booked:
        flash("This slot was just booked by another patient. Please select a different time.", "warning")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id,
                                date=str(slot.slot_date)))

    # FV — Verify slot is in future
    slot_datetime = datetime.combine(slot.slot_date, slot.start_time)
    if slot_datetime <= datetime.now():
        flash("Cannot book a slot in the past.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id))

    # DDV — Check if patient already has appointment at same time
    conflicting = Appointment.query.filter_by(patient_id=patient.id)\
        .filter(Appointment.appt_datetime == slot_datetime)\
        .filter(Appointment.status.in_(["confirmed", "pending"])).first()

    if conflicting:
        flash("You already have an appointment at this time.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id,
                                date=str(slot.slot_date)))

    notes = request.form.get("notes", "").strip()

    try:
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            slot_id=slot_id,
            appt_datetime=slot_datetime,
            status="confirmed",
            notes=notes if notes else None
        )
        db.session.add(appointment)

        # Mark slot as booked
        slot.is_booked = True
        db.session.commit()

        # ADT
        log_audit(
            action="BOOK_APPOINTMENT",
            entity_type="appointment",
            entity_id=appointment.id,
            user_id=current_user.id,
            details={
                "doctor_id": doctor_id,
                "slot_date": str(slot.slot_date),
                "start_time": str(slot.start_time),
                "end_time": str(slot.end_time),
                "ip": request.remote_addr
            }
        )

        flash(f"Appointment confirmed with {doctor.full_name} on "
              f"{slot.slot_date.strftime('%B %d, %Y')} at "
              f"{slot.start_time.strftime('%I:%M %p')}!", "success")

        return redirect(url_for("booking.booking_success",
                                doctor_id=doctor_id, appointment_id=appointment.id))

    except Exception as exc:
        db.session.rollback()
        logger.error(f"Booking failed: {exc}", exc_info=True)
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id,
                                date=str(slot.slot_date)))


@booking_bp.route("/book/<int:doctor_id>/success/<int:appointment_id>", methods=["GET"])
@login_required
def booking_success(doctor_id, appointment_id):
    """Booking confirmation page."""
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    # ExHL — Verify this appointment belongs to the patient
    if appointment.patient_id != patient.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    slot = AppointmentSlot.query.get(appointment.slot_id)

    return render_template("booking/booking_success.html",
                           doctor=doctor,
                           appointment=appointment,
                           slot=slot,
                           patient=patient)
