from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from src.backend import db
from src.backend.models.user import Patient, Doctor, DoctorSpecialty, AuditLog, Favorite, Appointment, AppointmentSlot

dashboard_bp = Blueprint("dashboard", __name__)


def _calc_patient_completion(patient):
    fields = [
        patient.first_name, patient.last_name, patient.phone,
        patient.date_of_birth, patient.gender,
        patient.address_line1, patient.insurance_provider
    ]
    filled = sum(1 for f in fields if f)
    return int((filled / len(fields)) * 100)


def _calc_doctor_completion(doctor):
    fields = [
        doctor.first_name, doctor.last_name, doctor.phone,
        doctor.license_number, doctor.bio,
        doctor.clinic_name, doctor.clinic_address
    ]
    filled = sum(1 for f in fields if f)
    return int((filled / len(fields)) * 100)


@dashboard_bp.route("/patient")
@login_required
def patient_dashboard():
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return redirect(url_for("auth.register_patient"))

    completion = _calc_patient_completion(patient)

    activity_logs = AuditLog.query.filter_by(
        user_id=current_user.id
    ).order_by(AuditLog.created_at.desc()).limit(5).all()

    # Load favorites with doctor and specialty info
    favorites = db.session.query(Favorite, Doctor, DoctorSpecialty)\
        .join(Doctor, Doctor.id == Favorite.doctor_id)\
        .outerjoin(DoctorSpecialty, DoctorSpecialty.id == Doctor.specialty_id)\
        .filter(Favorite.patient_id == patient.id)\
        .order_by(Favorite.created_at.desc())\
        .limit(5).all()

    # Total favorites count (not limited to 5)
    favorites_count = Favorite.query.filter_by(patient_id=patient.id).count()

    # Load upcoming appointments
    upcoming_appointments = db.session.query(Appointment, Doctor, DoctorSpecialty, AppointmentSlot)\
        .join(Doctor, Doctor.id == Appointment.doctor_id)\
        .outerjoin(DoctorSpecialty, DoctorSpecialty.id == Doctor.specialty_id)\
        .join(AppointmentSlot, AppointmentSlot.id == Appointment.slot_id)\
        .filter(Appointment.patient_id == patient.id)\
        .filter(Appointment.appt_datetime >= datetime.utcnow())\
        .filter(Appointment.status.in_(["confirmed", "pending"]))\
        .order_by(Appointment.appt_datetime.asc())\
        .limit(5).all()

    appointments_count = Appointment.query.filter_by(patient_id=patient.id)\
        .filter(Appointment.appt_datetime >= datetime.utcnow())\
        .filter(Appointment.status.in_(["confirmed", "pending"])).count()

    return render_template(
        "dashboard/patient_dashboard.html",
        patient=patient,
        user=current_user,
        completion=completion,
        activity_logs=activity_logs,
        favorites=favorites,
        favorites_count=favorites_count,
        upcoming_appointments=upcoming_appointments,
        appointments_count=appointments_count
    )


@dashboard_bp.route("/doctor")
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        return redirect(url_for("dashboard.patient_dashboard"))

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return redirect(url_for("auth.register_doctor"))

    specialty = DoctorSpecialty.query.get(doctor.specialty_id)
    completion = _calc_doctor_completion(doctor)

    activity_logs = AuditLog.query.filter_by(
        user_id=current_user.id
    ).order_by(AuditLog.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard/doctor_dashboard.html",
        doctor=doctor,
        specialty=specialty,
        user=current_user,
        completion=completion,
        activity_logs=activity_logs
    )