from flask import Blueprint, render_template
from src.backend.models.user import Review, Patient, Doctor, DoctorSpecialty

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    """Homepage with real reviews from DB."""
    try:
        # Get latest 3 reviews with patient and doctor info
        from src.backend import db
        reviews = db.session.query(Review, Patient, Doctor, DoctorSpecialty)\
            .join(Patient, Patient.id == Review.patient_id)\
            .join(Doctor, Doctor.id == Review.doctor_id)\
            .outerjoin(DoctorSpecialty, DoctorSpecialty.id == Doctor.specialty_id)\
            .order_by(Review.created_at.desc())\
            .limit(3).all()
    except Exception:
        reviews = []

    return render_template("index.html", reviews=reviews)