import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user
from src.backend import db
from src.backend.models.user import User, Patient, Doctor, DoctorSpecialty
from src.backend.forms.auth_forms import RegisterPatientForm, RegisterDoctorForm
from src.backend.utils.audit import log_audit

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


# ── helpers ────────────────────────────────────────────────────────────────

def _get_specialty_choices():
    """DS crosscut: load specialties from DB for the doctor form."""
    specialties = DoctorSpecialty.query.order_by(DoctorSpecialty.name).all()
    return [(s.id, s.name) for s in specialties]


def _get_ddd_duration(specialty_id):
    """
    DDD crosscut: data-driven default appointment duration by specialty.
    Specialties that typically need longer slots get 45 or 60 min.
    """
    longer_specialties = {
        "Psychiatry": 60,
        "Neurology": 45,
        "Cardiology": 45,
        "Orthopedics": 45,
    }
    specialty = DoctorSpecialty.query.get(specialty_id)
    if specialty:
        return longer_specialties.get(specialty.name, 30)
    return 30


# ── 01.01 Register Patient ─────────────────────────────────────────────────

@auth_bp.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    if current_user.is_authenticated:
        return redirect(url_for("auth.register_patient"))

    form = RegisterPatientForm()

    if form.validate_on_submit():
        try:
            # Create User (ET-In: role = patient, DF-Out: feeds all modules)
            user = User(
                email=form.email.data.strip().lower(),
                role="patient"
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()  # get user.id before commit

            # Create Patient profile (CS crosscut)
            patient = Patient(
                user_id=user.id,
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                date_of_birth=form.date_of_birth.data,
                gender=form.gender.data or None,
                phone=form.phone.data.strip(),
                address_line1=form.address_line1.data or None,
                address_line2=form.address_line2.data or None,
                city=form.city.data or None,
                state=form.state.data or None,
                zip_code=form.zip_code.data or None,
                insurance_provider=form.insurance_provider.data or None,
                insurance_id=form.insurance_id.data or None,
                preferred_payment=form.preferred_payment.data,  # DDD default
            )
            db.session.add(patient)
            db.session.commit()

            # ADT crosscut: log registration
            log_audit(
                action="REGISTER_PATIENT",
                entity_type="patient",
                entity_id=patient.id,
                user_id=user.id,
                details={"email": user.email, "ip": request.remote_addr}
            )

            logger.info("Patient registered: user_id=%s email=%s", user.id, user.email)

            # Log the new user in
            login_user(user)
            flash("Welcome to QuickDoc! Your account has been created.", "success")
            return redirect(url_for("auth.register_patient"))

        except Exception as exc:
            # ExHL crosscut: catch, log, rollback, show user-friendly message
            db.session.rollback()
            logger.error("Patient registration failed: %s", exc, exc_info=True)
            flash("Something went wrong. Please try again or contact support.", "danger")

    # CN crosscut: on GET or invalid form, just render — no external calls needed
    return render_template("register_patient.html", form=form, title="Register as Patient")


# ── 01.02 Register Doctor ──────────────────────────────────────────────────

@auth_bp.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    if current_user.is_authenticated:
        return redirect(url_for("auth.register_doctor"))

    form = RegisterDoctorForm()

    # DS crosscut: populate specialty choices from DB
    try:
        form.specialty_id.choices = _get_specialty_choices()
    except Exception as exc:
        # CN crosscut: DB unavailable — show error, don't crash
        logger.error("Could not load specialties: %s", exc)
        flash("Unable to load specialties. Please try again.", "danger")
        form.specialty_id.choices = []

    if form.validate_on_submit():
        try:
            # Create User (ET-In: role = doctor, DF-Out: feeds all modules)
            user = User(
                email=form.email.data.strip().lower(),
                role="doctor"
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()

            # DDD crosscut: default appointment duration by specialty
            default_duration = _get_ddd_duration(form.specialty_id.data)

            # Create Doctor profile (CS + DS crosscuts)
            doctor = Doctor(
                user_id=user.id,
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                specialty_id=form.specialty_id.data,
                license_number=form.license_number.data.strip(),
                years_experience=form.years_experience.data,
                consultation_fee=form.consultation_fee.data,
                bio=form.bio.data or None,
                phone=form.phone.data.strip(),
                clinic_name=form.clinic_name.data or None,
                clinic_address=form.clinic_address.data or None,
                city=form.city.data or None,
                state=form.state.data or None,
                zip_code=form.zip_code.data or None,
                avg_appointment_duration=default_duration,  # DDD
            )
            db.session.add(doctor)
            db.session.commit()

            # ADT crosscut: log registration
            log_audit(
                action="REGISTER_DOCTOR",
                entity_type="doctor",
                entity_id=doctor.id,
                user_id=user.id,
                details={
                    "email": user.email,
                    "specialty_id": doctor.specialty_id,
                    "license_number": doctor.license_number,
                    "ip": request.remote_addr
                }
            )

            logger.info("Doctor registered: user_id=%s email=%s", user.id, user.email)

            login_user(user)
            flash("Welcome to QuickDoc! Your doctor profile is pending verification.", "success")
            return redirect(url_for("auth.register_doctor"))

        except Exception as exc:
            # ExHL crosscut
            db.session.rollback()
            logger.error("Doctor registration failed: %s", exc, exc_info=True)
            flash("Something went wrong. Please try again or contact support.", "danger")

    return render_template("register_doctor.html", form=form, title="Register as Doctor")