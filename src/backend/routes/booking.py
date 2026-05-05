import logging
from datetime import datetime, timedelta, date, time
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.backend import db
from src.backend.models.user import (
    Doctor, Patient, Schedule, AppointmentSlot, Appointment,
    DoctorSpecialty, Notification
)
from src.backend.utils.audit import log_audit

logger = logging.getLogger(__name__)
booking_bp = Blueprint("booking", __name__)

SLOT_DURATION_MINUTES = 30
BOOKING_WINDOW_DAYS = 180


def generate_slots_for_doctor(doctor_id):
    schedules = Schedule.query.filter_by(doctor_id=doctor_id, is_active=True).all()
    if not schedules:
        return 0

    today = date.today()
    end_date = today + timedelta(days=BOOKING_WINDOW_DAYS)

    day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
               "Friday": 4, "Saturday": 5, "Sunday": 6}

    existing = set()
    existing_slots = AppointmentSlot.query.filter(
        AppointmentSlot.doctor_id == doctor_id,
        AppointmentSlot.slot_date >= today
    ).all()
    for s in existing_slots:
        existing.add((s.slot_date, s.start_time))

    new_slots = []
    current = today + timedelta(days=1)

    while current <= end_date:
        weekday = current.weekday()
        for sched in schedules:
            if day_map.get(sched.day_of_week) != weekday:
                continue

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


def send_notification(user_id, title, message, notif_type="info", link=None):
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        link=link,
        is_read=False
    )
    db.session.add(notif)
    db.session.commit()
    return notif


# ── 03.01 View Available Slots ────────────────────────────────────────────

@booking_bp.route("/book/<int:doctor_id>", methods=["GET"])
@login_required
def view_available_slots(doctor_id):
    if current_user.role != "patient":
        flash("Only patients can book appointments.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    if not patient:
        flash("Patient profile not found.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    schedules = Schedule.query.filter_by(doctor_id=doctor_id, is_active=True).all()
    if not schedules:
        flash("This doctor has not set their availability yet.", "warning")
        return redirect(url_for("search.doctor_public_profile", doctor_id=doctor_id))

    try:
        new_count = generate_slots_for_doctor(doctor_id)
        if new_count > 0:
            logger.info("Generated %d new slots for doctor %d", new_count, doctor_id)
    except Exception as exc:
        logger.error("Slot generation failed: %s", exc, exc_info=True)

    selected_date_str = request.args.get("date", "")
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today() + timedelta(days=1)
    else:
        selected_date = date.today() + timedelta(days=1)

    available_slots = AppointmentSlot.query.filter_by(
        doctor_id=doctor_id, slot_date=selected_date, is_booked=False
    ).order_by(AppointmentSlot.start_time).all()

    today = date.today()
    available_dates = db.session.query(AppointmentSlot.slot_date).filter(
        AppointmentSlot.doctor_id == doctor_id,
        AppointmentSlot.is_booked == False,
        AppointmentSlot.slot_date > today,
        AppointmentSlot.slot_date <= today + timedelta(days=BOOKING_WINDOW_DAYS)
    ).distinct().order_by(AppointmentSlot.slot_date).all()
    available_dates = [d[0] for d in available_dates]

    existing_appts = Appointment.query.filter_by(
        patient_id=patient.id, doctor_id=doctor_id
    ).filter(Appointment.status.in_(["confirmed", "pending"])).all()

    log_audit(
        action="VIEW_AVAILABLE_SLOTS",
        entity_type="doctor", entity_id=doctor_id,
        user_id=current_user.id,
        details={"date": str(selected_date), "slots_count": len(available_slots),
                 "ip": request.remote_addr}
    )

    return render_template("booking/view_slots.html",
                           doctor=doctor, patient=patient,
                           selected_date=selected_date,
                           available_slots=available_slots,
                           available_dates=available_dates,
                           existing_appts=existing_appts)


# ── 03.02 Book Appointment ────────────────────────────────────────────────

@booking_bp.route("/book/<int:doctor_id>/confirm/<int:slot_id>", methods=["GET"])
@login_required
def confirm_booking(doctor_id, slot_id):
    if current_user.role != "patient":
        flash("Only patients can book appointments.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    slot = AppointmentSlot.query.get_or_404(slot_id)

    if slot.doctor_id != doctor_id:
        flash("Invalid slot selected.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id))

    if slot.is_booked:
        flash("This slot has already been booked by another patient.", "warning")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id,
                                date=str(slot.slot_date)))

    slot_datetime = datetime.combine(slot.slot_date, slot.start_time)
    if slot_datetime <= datetime.now():
        flash("Cannot book a slot in the past.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id))

    return render_template("booking/confirm_booking.html",
                           doctor=doctor, patient=patient, slot=slot)


@booking_bp.route("/book/<int:doctor_id>/submit/<int:slot_id>", methods=["POST"])
@login_required
def submit_booking(doctor_id, slot_id):
    if current_user.role != "patient":
        flash("Only patients can book appointments.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    slot = AppointmentSlot.query.get_or_404(slot_id)

    if slot.doctor_id != doctor_id:
        flash("Invalid slot selected.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id))

    if slot.is_booked:
        flash("This slot was just booked by another patient. Please select a different time.", "warning")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id,
                                date=str(slot.slot_date)))

    slot_datetime = datetime.combine(slot.slot_date, slot.start_time)
    if slot_datetime <= datetime.now():
        flash("Cannot book a slot in the past.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id))

    conflicting = Appointment.query.filter_by(patient_id=patient.id).filter(
        Appointment.appt_datetime == slot_datetime
    ).filter(Appointment.status.in_(["confirmed", "pending"])).first()

    if conflicting:
        flash("You already have an appointment at this time.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id,
                                date=str(slot.slot_date)))

    notes = request.form.get("notes", "").strip()

    try:
        appointment = Appointment(
            patient_id=patient.id, doctor_id=doctor_id, slot_id=slot_id,
            appt_datetime=slot_datetime, status="confirmed",
            notes=notes if notes else None
        )
        db.session.add(appointment)
        slot.is_booked = True
        db.session.commit()

        # 03.06 Send booking confirmation notification
        send_notification(
            user_id=current_user.id,
            title="Appointment Confirmed",
            message="Your appointment with %s on %s at %s has been confirmed." % (
                doctor.full_name,
                slot.slot_date.strftime('%B %d, %Y'),
                slot.start_time.strftime('%I:%M %p')
            ),
            notif_type="booking",
            link="/booking/history"
        )

        # Also notify the doctor
        send_notification(
            user_id=doctor.user_id,
            title="New Appointment Booked",
            message="Patient %s booked an appointment on %s at %s." % (
                patient.full_name,
                slot.slot_date.strftime('%B %d, %Y'),
                slot.start_time.strftime('%I:%M %p')
            ),
            notif_type="booking",
            link="/dashboard/doctor"
        )

        log_audit(
            action="BOOK_APPOINTMENT",
            entity_type="appointment", entity_id=appointment.id,
            user_id=current_user.id,
            details={"doctor_id": doctor_id, "slot_date": str(slot.slot_date),
                     "start_time": str(slot.start_time), "ip": request.remote_addr}
        )

        flash("Appointment confirmed with %s on %s at %s!" % (
            doctor.full_name,
            slot.slot_date.strftime('%B %d, %Y'),
            slot.start_time.strftime('%I:%M %p')
        ), "success")

        return redirect(url_for("booking.booking_success",
                                doctor_id=doctor_id, appointment_id=appointment.id))

    except Exception as exc:
        db.session.rollback()
        logger.error("Booking failed: %s", exc, exc_info=True)
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for("booking.view_available_slots", doctor_id=doctor_id,
                                date=str(slot.slot_date)))


@booking_bp.route("/book/<int:doctor_id>/success/<int:appointment_id>", methods=["GET"])
@login_required
def booking_success(doctor_id, appointment_id):
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    if appointment.patient_id != patient.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    slot = AppointmentSlot.query.get(appointment.slot_id)

    return render_template("booking/booking_success.html",
                           doctor=doctor, appointment=appointment,
                           slot=slot, patient=patient)


# ── 03.03 Reschedule Booking ──────────────────────────────────────────────

@booking_bp.route("/reschedule/<int:appointment_id>", methods=["GET"])
@login_required
def reschedule_select(appointment_id):
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    if appointment.status not in ["confirmed", "pending"]:
        flash("Only confirmed or pending appointments can be rescheduled.", "warning")
        return redirect(url_for("booking.booking_history"))

    appt_dt = appointment.appt_datetime
    if appt_dt <= datetime.now() + timedelta(hours=24):
        flash("Cannot reschedule within 24 hours of appointment time.", "danger")
        return redirect(url_for("booking.booking_history"))

    old_slot = AppointmentSlot.query.get(appointment.slot_id)
    doctor = Doctor.query.get(appointment.doctor_id)

    return render_template("booking/reschedule_select.html",
                           appointment=appointment, doctor=doctor,
                           old_slot=old_slot, patient=patient)


@booking_bp.route("/reschedule/<int:appointment_id>/doctor/<int:doctor_id>", methods=["GET"])
@login_required
def reschedule_pick_slot(appointment_id, doctor_id):
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.get_or_404(doctor_id)

    try:
        generate_slots_for_doctor(doctor_id)
    except Exception as exc:
        logger.error("Slot generation failed: %s", exc, exc_info=True)

    selected_date_str = request.args.get("date", "")
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today() + timedelta(days=1)
    else:
        selected_date = date.today() + timedelta(days=1)

    available_slots = AppointmentSlot.query.filter_by(
        doctor_id=doctor_id, slot_date=selected_date, is_booked=False
    ).order_by(AppointmentSlot.start_time).all()

    today = date.today()
    available_dates = db.session.query(AppointmentSlot.slot_date).filter(
        AppointmentSlot.doctor_id == doctor_id,
        AppointmentSlot.is_booked == False,
        AppointmentSlot.slot_date > today,
        AppointmentSlot.slot_date <= today + timedelta(days=BOOKING_WINDOW_DAYS)
    ).distinct().order_by(AppointmentSlot.slot_date).all()
    available_dates = [d[0] for d in available_dates]

    return render_template("booking/reschedule_slots.html",
                           doctor=doctor, patient=patient,
                           appointment=appointment,
                           selected_date=selected_date,
                           available_slots=available_slots,
                           available_dates=available_dates)


@booking_bp.route("/reschedule/<int:appointment_id>/confirm/<int:new_slot_id>", methods=["POST"])
@login_required
def reschedule_confirm(appointment_id, new_slot_id):
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    if appointment.status not in ["confirmed", "pending"]:
        flash("Only confirmed or pending appointments can be rescheduled.", "warning")
        return redirect(url_for("booking.booking_history"))

    new_slot = AppointmentSlot.query.get_or_404(new_slot_id)

    if new_slot.is_booked:
        flash("This slot was just booked by someone else. Please pick another.", "warning")
        return redirect(url_for("booking.reschedule_pick_slot",
                                appointment_id=appointment_id, doctor_id=new_slot.doctor_id))

    new_datetime = datetime.combine(new_slot.slot_date, new_slot.start_time)
    if new_datetime <= datetime.now():
        flash("Cannot reschedule to a past slot.", "danger")
        return redirect(url_for("booking.reschedule_pick_slot",
                                appointment_id=appointment_id, doctor_id=new_slot.doctor_id))

    try:
        # Free old slot
        old_slot = AppointmentSlot.query.get(appointment.slot_id)
        if old_slot:
            old_slot.is_booked = False

        old_doctor_id = appointment.doctor_id
        old_date = str(appointment.appt_datetime)

        # Update appointment
        appointment.doctor_id = new_slot.doctor_id
        appointment.slot_id = new_slot.id
        appointment.appt_datetime = new_datetime
        appointment.status = "confirmed"

        # Book new slot
        new_slot.is_booked = True
        db.session.commit()

        new_doctor = Doctor.query.get(new_slot.doctor_id)

        # Notification to patient
        send_notification(
            user_id=current_user.id,
            title="Appointment Rescheduled",
            message="Your appointment has been rescheduled to %s on %s at %s." % (
                new_doctor.full_name,
                new_slot.slot_date.strftime('%B %d, %Y'),
                new_slot.start_time.strftime('%I:%M %p')
            ),
            notif_type="reschedule",
            link="/booking/history"
        )

        # Notification to new doctor
        send_notification(
            user_id=new_doctor.user_id,
            title="Appointment Rescheduled",
            message="Patient %s rescheduled to %s at %s." % (
                patient.full_name,
                new_slot.slot_date.strftime('%B %d, %Y'),
                new_slot.start_time.strftime('%I:%M %p')
            ),
            notif_type="reschedule"
        )

        log_audit(
            action="RESCHEDULE_APPOINTMENT",
            entity_type="appointment", entity_id=appointment.id,
            user_id=current_user.id,
            details={"old_date": old_date, "new_date": str(new_datetime),
                     "old_doctor_id": old_doctor_id,
                     "new_doctor_id": new_slot.doctor_id,
                     "ip": request.remote_addr}
        )

        flash("Appointment rescheduled to %s on %s at %s!" % (
            new_doctor.full_name,
            new_slot.slot_date.strftime('%B %d, %Y'),
            new_slot.start_time.strftime('%I:%M %p')
        ), "success")

    except Exception as exc:
        db.session.rollback()
        logger.error("Reschedule failed: %s", exc, exc_info=True)
        flash("Something went wrong. Please try again.", "danger")

    return redirect(url_for("booking.booking_history"))


# ── 03.04 Cancel Booking ──────────────────────────────────────────────────

@booking_bp.route("/cancel/<int:appointment_id>", methods=["GET"])
@login_required
def cancel_confirm(appointment_id):
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    if appointment.status not in ["confirmed", "pending"]:
        flash("Only confirmed or pending appointments can be cancelled.", "warning")
        return redirect(url_for("booking.booking_history"))

    appt_dt = appointment.appt_datetime
    if appt_dt <= datetime.now() + timedelta(hours=24):
        flash("Cannot cancel within 24 hours of appointment time.", "danger")
        return redirect(url_for("booking.booking_history"))

    doctor = Doctor.query.get(appointment.doctor_id)
    slot = AppointmentSlot.query.get(appointment.slot_id)

    return render_template("booking/cancel_confirm.html",
                           appointment=appointment, doctor=doctor,
                           slot=slot, patient=patient)


@booking_bp.route("/cancel/<int:appointment_id>/submit", methods=["POST"])
@login_required
def cancel_submit(appointment_id):
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != patient.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    if appointment.status not in ["confirmed", "pending"]:
        flash("Only confirmed or pending appointments can be cancelled.", "warning")
        return redirect(url_for("booking.booking_history"))

    appt_dt = appointment.appt_datetime
    if appt_dt <= datetime.now() + timedelta(hours=24):
        flash("Cannot cancel within 24 hours of appointment time.", "danger")
        return redirect(url_for("booking.booking_history"))

    reason = request.form.get("reason", "").strip()

    try:
        # Free the slot
        slot = AppointmentSlot.query.get(appointment.slot_id)
        if slot:
            slot.is_booked = False

        doctor = Doctor.query.get(appointment.doctor_id)

        appointment.status = "cancelled"
        db.session.commit()

        # Notification to patient
        send_notification(
            user_id=current_user.id,
            title="Appointment Cancelled",
            message="Your appointment with %s on %s has been cancelled." % (
                doctor.full_name,
                appointment.appt_datetime.strftime('%B %d, %Y at %I:%M %p')
            ),
            notif_type="cancellation",
            link="/booking/history"
        )

        # Notification to doctor
        send_notification(
            user_id=doctor.user_id,
            title="Appointment Cancelled",
            message="Patient %s cancelled their appointment on %s." % (
                patient.full_name,
                appointment.appt_datetime.strftime('%B %d, %Y at %I:%M %p')
            ),
            notif_type="cancellation"
        )

        log_audit(
            action="CANCEL_APPOINTMENT",
            entity_type="appointment", entity_id=appointment.id,
            user_id=current_user.id,
            details={"doctor_id": appointment.doctor_id,
                     "date": str(appointment.appt_datetime),
                     "reason": reason, "ip": request.remote_addr}
        )

        flash("Appointment cancelled successfully.", "success")

    except Exception as exc:
        db.session.rollback()
        logger.error("Cancel failed: %s", exc, exc_info=True)
        flash("Something went wrong. Please try again.", "danger")

    return redirect(url_for("booking.booking_history"))


# ── 03.05 View Booking History ────────────────────────────────────────────

@booking_bp.route("/history", methods=["GET"])
@login_required
def booking_history():
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash("Patient profile not found.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    status_filter = request.args.get("status", "all")

    query = db.session.query(Appointment, Doctor, DoctorSpecialty, AppointmentSlot).join(
        Doctor, Doctor.id == Appointment.doctor_id
    ).outerjoin(
        DoctorSpecialty, DoctorSpecialty.id == Doctor.specialty_id
    ).join(
        AppointmentSlot, AppointmentSlot.id == Appointment.slot_id
    ).filter(
        Appointment.patient_id == patient.id
    )

    if status_filter == "upcoming":
        query = query.filter(
            Appointment.appt_datetime >= datetime.utcnow(),
            Appointment.status.in_(["confirmed", "pending"])
        )
    elif status_filter == "past":
        query = query.filter(
            Appointment.appt_datetime < datetime.utcnow(),
            Appointment.status.in_(["confirmed", "completed"])
        )
    elif status_filter == "cancelled":
        query = query.filter(Appointment.status == "cancelled")

    appointments = query.order_by(Appointment.appt_datetime.desc()).all()

    # Counts for tabs
    total_count = Appointment.query.filter_by(patient_id=patient.id).count()
    upcoming_count = Appointment.query.filter_by(patient_id=patient.id).filter(
        Appointment.appt_datetime >= datetime.utcnow(),
        Appointment.status.in_(["confirmed", "pending"])
    ).count()
    past_count = Appointment.query.filter_by(patient_id=patient.id).filter(
        Appointment.appt_datetime < datetime.utcnow(),
        Appointment.status.in_(["confirmed", "completed"])
    ).count()
    cancelled_count = Appointment.query.filter_by(
        patient_id=patient.id, status="cancelled"
    ).count()

    log_audit(
        action="VIEW_BOOKING_HISTORY",
        entity_type="patient", entity_id=patient.id,
        user_id=current_user.id,
        details={"filter": status_filter, "ip": request.remote_addr}
    )

    return render_template("booking/booking_history.html",
                           appointments=appointments,
                           patient=patient,
                           status_filter=status_filter,
                           total_count=total_count,
                           upcoming_count=upcoming_count,
                           past_count=past_count,
                           cancelled_count=cancelled_count,
                           now=datetime.utcnow())


# ── 03.06 Send Booking Reminder — Notifications ──────────────────────────

@booking_bp.route("/notifications", methods=["GET"])
@login_required
def view_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(20).all()

    unread_count = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()

    return render_template("booking/notifications.html",
                           notifications=notifications,
                           unread_count=unread_count)


@booking_bp.route("/notifications/read/<int:notif_id>", methods=["POST"])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("booking.view_notifications"))

    notif.is_read = True
    db.session.commit()

    if notif.link:
        return redirect(notif.link)
    return redirect(url_for("booking.view_notifications"))


@booking_bp.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({"is_read": True})
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for("booking.view_notifications"))


def generate_reminders():
    """Called by a scheduled job or manually. Sends reminders 24h before appointment."""
    tomorrow = datetime.utcnow() + timedelta(hours=24)
    today = datetime.utcnow()

    upcoming = Appointment.query.filter(
        Appointment.appt_datetime >= today,
        Appointment.appt_datetime <= tomorrow,
        Appointment.status.in_(["confirmed", "pending"])
    ).all()

    count = 0
    for appt in upcoming:
        existing = Notification.query.filter_by(
            user_id=Patient.query.get(appt.patient_id).user_id if Patient.query.get(appt.patient_id) else 0,
            type="reminder"
        ).filter(
            Notification.message.contains(str(appt.id))
        ).first()

        if not existing:
            patient = Patient.query.get(appt.patient_id)
            doctor = Doctor.query.get(appt.doctor_id)
            if patient and doctor:
                send_notification(
                    user_id=patient.user_id,
                    title="Appointment Reminder",
                    message="Reminder: You have an appointment with %s tomorrow on %s at %s. Appointment ID: %d" % (
                        doctor.full_name,
                        appt.appt_datetime.strftime('%B %d, %Y'),
                        appt.appt_datetime.strftime('%I:%M %p'),
                        appt.id
                    ),
                    notif_type="reminder",
                    link="/booking/history"
                )
                count += 1

    return count