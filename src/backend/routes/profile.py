import logging
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.backend import db
from src.backend.models.user import User, Patient, Doctor, DoctorSpecialty
from src.backend.utils.audit import log_audit

logger = logging.getLogger(__name__)
profile_bp = Blueprint("profile", __name__)

# In-memory token store (for demo — no email needed)
reset_tokens = {}


# ── 01.07 Show Patient Profile ─────────────────────────────────────────────

@profile_bp.route("/patient")
@login_required
def patient_profile():
    if current_user.role != "patient":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()

    log_audit(
        action="VIEW_PROFILE",
        entity_type="patient",
        entity_id=patient.id,
        user_id=current_user.id,
        details={"ip": request.remote_addr}
    )

    return render_template("profile/patient_profile.html",
                           patient=patient,
                           user=current_user)


# ── 01.07 Show Doctor Profile ──────────────────────────────────────────────

@profile_bp.route("/doctor")
@login_required
def doctor_profile():
    if current_user.role != "doctor":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    specialty = DoctorSpecialty.query.get(doctor.specialty_id)

    log_audit(
        action="VIEW_PROFILE",
        entity_type="doctor",
        entity_id=doctor.id,
        user_id=current_user.id,
        details={"ip": request.remote_addr}
    )

    return render_template("profile/doctor_profile.html",
                           doctor=doctor,
                           specialty=specialty,
                           user=current_user)


# ── 01.05 Edit Patient Profile ─────────────────────────────────────────────

@profile_bp.route("/patient/edit", methods=["GET", "POST"])
@login_required
def patient_edit():
    if current_user.role != "patient":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == "POST":
        try:
            patient.first_name = request.form.get("first_name", "").strip()
            patient.last_name = request.form.get("last_name", "").strip()
            patient.phone = request.form.get("phone", "").strip()
            patient.address_line1 = request.form.get("address_line1") or None
            patient.address_line2 = request.form.get("address_line2") or None
            patient.city = request.form.get("city") or None
            patient.state = request.form.get("state") or None
            patient.zip_code = request.form.get("zip_code") or None
            patient.insurance_provider = request.form.get("insurance_provider") or None
            patient.insurance_id = request.form.get("insurance_id") or None
            patient.preferred_payment = request.form.get("preferred_payment", "card")

            db.session.commit()

            log_audit(
                action="UPDATE_PROFILE",
                entity_type="patient",
                entity_id=patient.id,
                user_id=current_user.id,
                details={"ip": request.remote_addr}
            )

            flash("Your profile has been updated successfully!", "success")
            return redirect(url_for("profile.patient_profile"))

        except Exception as exc:
            db.session.rollback()
            logger.error("Patient profile update failed: %s", exc, exc_info=True)
            flash("Something went wrong. Please try again.", "danger")

    return render_template("profile/patient_edit.html",
                           patient=patient,
                           user=current_user)


# ── 01.05 Edit Doctor Profile ──────────────────────────────────────────────

@profile_bp.route("/doctor/edit", methods=["GET", "POST"])
@login_required
def doctor_edit():
    if current_user.role != "doctor":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
    specialties = DoctorSpecialty.query.order_by(DoctorSpecialty.name).all()

    if request.method == "POST":
        try:
            doctor.first_name = request.form.get("first_name", "").strip()
            doctor.last_name = request.form.get("last_name", "").strip()
            doctor.phone = request.form.get("phone", "").strip()
            doctor.bio = request.form.get("bio") or None
            doctor.clinic_name = request.form.get("clinic_name") or None
            doctor.clinic_address = request.form.get("clinic_address") or None
            doctor.city = request.form.get("city") or None
            doctor.state = request.form.get("state") or None
            doctor.zip_code = request.form.get("zip_code") or None
            doctor.consultation_fee = float(request.form.get("consultation_fee", 0))

            db.session.commit()

            log_audit(
                action="UPDATE_PROFILE",
                entity_type="doctor",
                entity_id=doctor.id,
                user_id=current_user.id,
                details={"ip": request.remote_addr}
            )

            flash("Your profile has been updated successfully!", "success")
            return redirect(url_for("profile.doctor_profile"))

        except Exception as exc:
            db.session.rollback()
            logger.error("Doctor profile update failed: %s", exc, exc_info=True)
            flash("Something went wrong. Please try again.", "danger")

    return render_template("profile/doctor_edit.html",
                           doctor=doctor,
                           specialties=specialties,
                           user=current_user)


# ── 01.08 Reset Password (Token on Screen) ─────────────────────────────────

@profile_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password_request():
    """Step 1 — User enters email, gets token shown on screen."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with that email.", "danger")
            return render_template("profile/reset_password_request.html")

        # Generate token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        reset_tokens[token] = {"user_id": user.id, "expires_at": expires_at}

        log_audit(
            action="PASSWORD_RESET_REQUESTED",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            details={"email": email, "ip": request.remote_addr}
        )

        # Show token on screen (no email needed)
        flash(f"Your password reset token is: {token} (valid for 30 minutes)", "info")
        return render_template("profile/reset_password_request.html", token=token)

    return render_template("profile/reset_password_request.html")


@profile_bp.route("/reset-password/confirm", methods=["GET", "POST"])
def reset_password_confirm():
    """Step 2 — User enters token + new password."""
    if request.method == "POST":
        token = request.form.get("token", "").strip()
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # FV crosscut
        if not token:
            flash("Reset token is required.", "danger")
            return render_template("profile/reset_password_confirm.html")

        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("profile/reset_password_confirm.html")

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("profile/reset_password_confirm.html")

        # ExHL crosscut - validate token
        token_data = reset_tokens.get(token)
        if not token_data:
            flash("Invalid or expired token. Please request a new one.", "danger")
            return render_template("profile/reset_password_confirm.html")

        if datetime.utcnow() > token_data["expires_at"]:
            del reset_tokens[token]
            flash("Token has expired. Please request a new one.", "danger")
            return render_template("profile/reset_password_confirm.html")

        # Update password
        user = User.query.get(token_data["user_id"])
        user.set_password(new_password)
        db.session.commit()
        del reset_tokens[token]

        log_audit(
            action="PASSWORD_RESET_SUCCESS",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            details={"ip": request.remote_addr}
        )

        flash("Password reset successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("profile/reset_password_confirm.html")