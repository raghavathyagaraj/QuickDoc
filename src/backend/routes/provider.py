import logging
from datetime import time, date, timedelta, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.backend import db
from src.backend.models.user import Doctor, DoctorSpecialty, Schedule, BlockedDate, Review, Patient
from src.backend.utils.audit import log_audit

logger = logging.getLogger(__name__)
provider_bp = Blueprint("provider", __name__)

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ── 04.01 Add/Edit Doctor Profile ─────────────────────────────────────────

@provider_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """ET-In: doctor only. FV: all fields validated. ADT: logged."""
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    specialties = DoctorSpecialty.query.order_by(DoctorSpecialty.name).all()

    if request.method == "POST":
        try:
            # FV — Field Validation
            first_name = request.form.get("first_name", "").strip()
            last_name  = request.form.get("last_name", "").strip()
            phone      = request.form.get("phone", "").strip()
            bio        = request.form.get("bio", "").strip()
            clinic_name    = request.form.get("clinic_name", "").strip()
            clinic_address = request.form.get("clinic_address", "").strip()
            city       = request.form.get("city", "").strip()
            state      = request.form.get("state", "").strip()
            zip_code   = request.form.get("zip_code", "").strip()
            specialty_id   = request.form.get("specialty_id", type=int)
            consultation_fee = request.form.get("consultation_fee", "").strip()
            years_experience = request.form.get("years_experience", type=int)
            avg_duration     = request.form.get("avg_appointment_duration", type=int)

            # FV — Required fields
            if not first_name or not last_name:
                flash("First name and last name are required.", "danger")
                return render_template("provider/doctor_edit_profile.html",
                                       doctor=doctor, specialties=specialties)

            if not phone:
                flash("Phone number is required.", "danger")
                return render_template("provider/doctor_edit_profile.html",
                                       doctor=doctor, specialties=specialties)

            # FV — Consultation fee validation
            fee = None
            if consultation_fee:
                try:
                    fee = float(consultation_fee)
                    if fee < 0:
                        flash("Consultation fee cannot be negative.", "danger")
                        return render_template("provider/doctor_edit_profile.html",
                                               doctor=doctor, specialties=specialties)
                except ValueError:
                    flash("Consultation fee must be a valid number.", "danger")
                    return render_template("provider/doctor_edit_profile.html",
                                           doctor=doctor, specialties=specialties)

            # FV — Years experience
            if years_experience is not None and (years_experience < 0 or years_experience > 60):
                flash("Years of experience must be between 0 and 60.", "danger")
                return render_template("provider/doctor_edit_profile.html",
                                       doctor=doctor, specialties=specialties)

            # FV — Bio length
            if bio and len(bio) > 500:
                flash("Bio must be under 500 characters.", "danger")
                return render_template("provider/doctor_edit_profile.html",
                                       doctor=doctor, specialties=specialties)

            # Update fields
            doctor.first_name     = first_name
            doctor.last_name      = last_name
            doctor.phone          = phone
            doctor.bio            = bio if bio else None
            doctor.clinic_name    = clinic_name if clinic_name else None
            doctor.clinic_address = clinic_address if clinic_address else None
            doctor.city           = city if city else None
            doctor.state          = state if state else None
            doctor.zip_code       = zip_code if zip_code else None
            doctor.consultation_fee = fee
            doctor.specialty_id     = specialty_id if specialty_id else doctor.specialty_id
            doctor.years_experience = years_experience if years_experience is not None else doctor.years_experience
            doctor.avg_appointment_duration = avg_duration if avg_duration else doctor.avg_appointment_duration

            db.session.commit()

            # ADT — Audit Trail
            log_audit(
                action="UPDATE_DOCTOR_PROFILE",
                entity_type="doctor",
                entity_id=doctor.id,
                user_id=current_user.id,
                details={"ip": request.remote_addr, "completion": doctor.profile_completion}
            )

            flash("Profile updated successfully!", "success")
            return redirect(url_for("dashboard.doctor_dashboard"))

        except Exception as exc:
            db.session.rollback()
            logger.error("Doctor profile update failed: %s", exc, exc_info=True)
            flash("Something went wrong. Please try again.", "danger")

    return render_template("provider/doctor_edit_profile.html",
                           doctor=doctor, specialties=specialties)


# ── 04.02 Update Schedule ─────────────────────────────────────────────────

@provider_bp.route("/schedule", methods=["GET"])
@login_required
def manage_schedule():
    """ET-In: doctor only. DS: specialty affects default duration."""
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    # Load existing schedule grouped by day
    existing = Schedule.query.filter_by(doctor_id=doctor.id, is_active=True)\
        .order_by(Schedule.day_of_week, Schedule.start_time).all()

    schedule_by_day = {day: [] for day in DAYS_OF_WEEK}
    for slot in existing:
        schedule_by_day[slot.day_of_week].append(slot)

    return render_template("provider/schedule_manage.html",
                           doctor=doctor,
                           days=DAYS_OF_WEEK,
                           schedule_by_day=schedule_by_day)


@provider_bp.route("/schedule/add", methods=["POST"])
@login_required
def add_schedule_slot():
    """FV: time validation. DDV: no overlapping. CC: unique constraint. ADT: logged."""
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    day_of_week = request.form.get("day_of_week", "").strip()
    start_str   = request.form.get("start_time", "").strip()
    end_str     = request.form.get("end_time", "").strip()

    # FV — Required fields
    if not day_of_week or not start_str or not end_str:
        flash("Day, start time and end time are required.", "danger")
        return redirect(url_for("provider.manage_schedule"))

    # FV — Valid day
    if day_of_week not in DAYS_OF_WEEK:
        flash("Invalid day selected.", "danger")
        return redirect(url_for("provider.manage_schedule"))

    # FV — Parse times
    try:
        start_parts = start_str.split(":")
        end_parts   = end_str.split(":")
        start_time  = time(int(start_parts[0]), int(start_parts[1]))
        end_time    = time(int(end_parts[0]), int(end_parts[1]))
    except (ValueError, IndexError):
        flash("Invalid time format.", "danger")
        return redirect(url_for("provider.manage_schedule"))

    # FV — End must be after start
    if end_time <= start_time:
        flash("End time must be after start time.", "danger")
        return redirect(url_for("provider.manage_schedule"))

    # DDV — Check overlapping slots
    existing = Schedule.query.filter_by(
        doctor_id=doctor.id, day_of_week=day_of_week, is_active=True
    ).all()

    for slot in existing:
        if (start_time < slot.end_time and end_time > slot.start_time):
            flash(f"Time slot overlaps with existing slot {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}.", "danger")
            return redirect(url_for("provider.manage_schedule"))

    try:
        new_slot = Schedule(
            doctor_id=doctor.id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )
        db.session.add(new_slot)
        db.session.commit()

        # ADT
        log_audit(
            action="ADD_SCHEDULE_SLOT",
            entity_type="schedule",
            entity_id=new_slot.id,
            user_id=current_user.id,
            details={
                "day": day_of_week,
                "start": start_str,
                "end": end_str,
                "ip": request.remote_addr
            }
        )

        flash(f"Schedule slot added: {day_of_week} {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}", "success")

    except Exception as exc:
        db.session.rollback()
        logger.error("Add schedule slot failed: %s", exc, exc_info=True)
        flash("Something went wrong. Please try again.", "danger")

    return redirect(url_for("provider.manage_schedule"))


@provider_bp.route("/schedule/delete/<int:slot_id>", methods=["POST"])
@login_required
def delete_schedule_slot(slot_id):
    """ExHL: validates ownership. ADT: logged."""
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    slot = Schedule.query.get_or_404(slot_id)

    # ExHL — Verify ownership
    if slot.doctor_id != doctor.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("provider.manage_schedule"))

    try:
        day = slot.day_of_week
        db.session.delete(slot)
        db.session.commit()

        log_audit(
            action="DELETE_SCHEDULE_SLOT",
            entity_type="schedule",
            entity_id=slot_id,
            user_id=current_user.id,
            details={"day": day, "ip": request.remote_addr}
        )

        flash("Schedule slot removed.", "success")

    except Exception as exc:
        db.session.rollback()
        logger.error("Delete schedule slot failed: %s", exc, exc_info=True)
        flash("Something went wrong.", "danger")

    return redirect(url_for("provider.manage_schedule"))


# ── 04.03 Manage Availability — Block Dates ───────────────────────────────

@provider_bp.route("/availability", methods=["GET"])
@login_required
def manage_availability():
    """ET-In: doctor only. Shows blocked dates and allows adding new blocks."""
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    blocked = BlockedDate.query.filter_by(doctor_id=doctor.id).filter(
        BlockedDate.block_date >= date.today()
    ).order_by(BlockedDate.block_date).all()

    past_blocked = BlockedDate.query.filter_by(doctor_id=doctor.id).filter(
        BlockedDate.block_date < date.today()
    ).count()

    return render_template("provider/manage_availability.html",
                           doctor=doctor, blocked_dates=blocked,
                           past_blocked_count=past_blocked)


@provider_bp.route("/availability/block", methods=["POST"])
@login_required
def block_date():
    """FV: date validation. DDV: no duplicate. CC: unique constraint. ADT: logged."""
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    block_type = request.form.get("block_type", "single")
    start_date_str = request.form.get("block_date", "").strip()
    end_date_str = request.form.get("end_date", "").strip()
    reason = request.form.get("reason", "").strip()

    if not start_date_str:
        flash("Please select a date to block.", "danger")
        return redirect(url_for("provider.manage_availability"))

    try:
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("provider.manage_availability"))

    if start_dt <= date.today():
        flash("Cannot block a date in the past.", "danger")
        return redirect(url_for("provider.manage_availability"))

    dates_to_block = [start_dt]

    if block_type == "range" and end_date_str:
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid end date format.", "danger")
            return redirect(url_for("provider.manage_availability"))

        if end_dt <= start_dt:
            flash("End date must be after start date.", "danger")
            return redirect(url_for("provider.manage_availability"))

        if (end_dt - start_dt).days > 30:
            flash("Cannot block more than 30 days at once.", "danger")
            return redirect(url_for("provider.manage_availability"))

        current_d = start_dt
        dates_to_block = []
        while current_d <= end_dt:
            dates_to_block.append(current_d)
            current_d += timedelta(days=1)

    try:
        blocked_count = 0
        for d in dates_to_block:
            existing = BlockedDate.query.filter_by(doctor_id=doctor.id, block_date=d).first()
            if not existing:
                new_block = BlockedDate(
                    doctor_id=doctor.id,
                    block_date=d,
                    reason=reason if reason else None
                )
                db.session.add(new_block)
                blocked_count += 1

        db.session.commit()

        log_audit(
            action="BLOCK_DATE",
            entity_type="availability",
            entity_id=doctor.id,
            user_id=current_user.id,
            details={
                "dates_blocked": blocked_count,
                "start": start_date_str,
                "end": end_date_str if block_type == "range" else start_date_str,
                "reason": reason,
                "ip": request.remote_addr
            }
        )

        if blocked_count > 0:
            flash("%d date%s blocked successfully." % (blocked_count, "s" if blocked_count > 1 else ""), "success")
        else:
            flash("Selected dates are already blocked.", "warning")

    except Exception as exc:
        db.session.rollback()
        logger.error("Block date failed: %s", exc, exc_info=True)
        flash("Something went wrong. Please try again.", "danger")

    return redirect(url_for("provider.manage_availability"))


@provider_bp.route("/availability/unblock/<int:block_id>", methods=["POST"])
@login_required
def unblock_date(block_id):
    """ExHL: ownership verified. ADT: logged."""
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    blocked = BlockedDate.query.get_or_404(block_id)

    if blocked.doctor_id != doctor.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("provider.manage_availability"))

    try:
        block_date_val = str(blocked.block_date)
        db.session.delete(blocked)
        db.session.commit()

        log_audit(
            action="UNBLOCK_DATE",
            entity_type="availability",
            entity_id=block_id,
            user_id=current_user.id,
            details={"date": block_date_val, "ip": request.remote_addr}
        )

        flash("Date unblocked successfully.", "success")

    except Exception as exc:
        db.session.rollback()
        logger.error("Unblock date failed: %s", exc, exc_info=True)
        flash("Something went wrong.", "danger")

    return redirect(url_for("provider.manage_availability"))


# ── 05.03 View Reviews — Doctor Reviews Dashboard ────────────────────────

@provider_bp.route("/reviews", methods=["GET"])
@login_required
def view_reviews():
    """ET-In: doctor only. Shows all reviews with stats."""
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    reviews = db.session.query(Review, Patient).join(
        Patient, Patient.id == Review.patient_id
    ).filter(
        Review.doctor_id == doctor.id
    ).order_by(Review.created_at.desc()).all()

    total = len(reviews)
    avg_rating = round(sum(r.rating for r, p in reviews) / total, 1) if total > 0 else 0
    rating_breakdown = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r, p in reviews:
        rating_breakdown[r.rating] = rating_breakdown.get(r.rating, 0) + 1

    log_audit(
        action="VIEW_REVIEWS_DASHBOARD",
        entity_type="doctor",
        entity_id=doctor.id,
        user_id=current_user.id,
        details={"total_reviews": total, "ip": request.remote_addr}
    )

    return render_template("provider/doctor_reviews.html",
                           doctor=doctor, reviews=reviews,
                           total=total, avg_rating=avg_rating,
                           rating_breakdown=rating_breakdown)