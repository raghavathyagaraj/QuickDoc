import logging
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from src.backend import db
from src.backend.models.user import Doctor, DoctorSpecialty, Patient, User, Favorite, Review
from src.backend.utils.audit import log_audit

logger = logging.getLogger(__name__)
search_bp = Blueprint("search", __name__)


@search_bp.route("/")
@login_required
def search():
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    query_text = request.args.get("q", "").strip()
    specialty  = request.args.get("specialty", "").strip()
    location   = request.args.get("location", "").strip()
    sort_by    = request.args.get("sort", "name")

    try:
        base = (
            db.session.query(Doctor, DoctorSpecialty, User)
            .join(User, User.id == Doctor.user_id)
            .outerjoin(DoctorSpecialty, DoctorSpecialty.id == Doctor.specialty_id)
            .filter(User.is_active == True)
        )

        if specialty:
            base = base.filter(DoctorSpecialty.name.ilike(f"%{specialty}%"))
        if location:
            base = base.filter(or_(
                Doctor.city.ilike(f"%{location}%"),
                Doctor.state.ilike(f"%{location}%"),
                Doctor.zip_code.ilike(f"%{location}%"),
                Doctor.clinic_address.ilike(f"%{location}%")
            ))
        if query_text:
            base = base.filter(or_(
                Doctor.first_name.ilike(f"%{query_text}%"),
                Doctor.last_name.ilike(f"%{query_text}%"),
                DoctorSpecialty.name.ilike(f"%{query_text}%"),
                Doctor.clinic_name.ilike(f"%{query_text}%")
            ))

        if sort_by == "fee":
            base = base.order_by(Doctor.consultation_fee.asc())
        elif sort_by == "experience":
            base = base.order_by(Doctor.years_experience.desc())
        else:
            base = base.order_by(Doctor.last_name.asc(), Doctor.first_name.asc())

        results = base.all()

        # CA crosscut — load patient favorites once for O(1) lookup
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        fav_doctor_ids = set()
        if patient:
            favs = Favorite.query.filter_by(patient_id=patient.id).all()
            fav_doctor_ids = {f.doctor_id for f in favs}

        log_audit(
            action="DOCTOR_SEARCH",
            entity_type="search",
            entity_id=None,
            user_id=current_user.id,
            details={"q": query_text, "specialty": specialty,
                     "location": location, "results_count": len(results),
                     "ip": request.remote_addr}
        )

        specialties = DoctorSpecialty.query.order_by(DoctorSpecialty.name).all()

        enriched = []
        for doctor, spec, user in results:
            enriched.append({
                "doctor": doctor,
                "specialty": spec,
                "user": user,
                "is_verified": doctor.is_verified,
                "has_bio": bool(doctor.bio),
                "location_display": _format_location(doctor),
                "is_favorited": doctor.id in fav_doctor_ids,
                "avg_rating": doctor.avg_rating,
                "review_count": doctor.review_count,
            })

        return render_template(
            "search/search_results.html",
            results=enriched,
            specialties=specialties,
            query_text=query_text,
            selected_specialty=specialty,
            selected_location=location,
            sort_by=sort_by,
            result_count=len(results),
            patient=patient
        )

    except Exception as exc:
        logger.error("Search failed: %s", exc, exc_info=True)
        return render_template(
            "search/search_results.html",
            results=[], specialties=DoctorSpecialty.query.all(),
            query_text=query_text, selected_specialty=specialty,
            selected_location=location, sort_by=sort_by,
            result_count=0,
            error="Search is temporarily unavailable. Please try again.",
            patient=Patient.query.filter_by(user_id=current_user.id).first()
        )


@search_bp.route("/doctor/<int:doctor_id>")
@login_required
def doctor_public_profile(doctor_id):
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    doctor   = Doctor.query.get_or_404(doctor_id)
    user     = User.query.get(doctor.user_id)
    specialty = DoctorSpecialty.query.get(doctor.specialty_id)
    patient  = Patient.query.filter_by(user_id=current_user.id).first()

    # CA — check favorite status
    is_favorited = False
    if patient:
        is_favorited = Favorite.query.filter_by(
            patient_id=patient.id, doctor_id=doctor_id
        ).first() is not None

    # Check if patient already reviewed
    has_reviewed = False
    if patient:
        has_reviewed = Review.query.filter_by(
            patient_id=patient.id, doctor_id=doctor_id
        ).first() is not None

    # Load reviews with patient info
    reviews = db.session.query(Review, Patient)\
        .join(Patient, Patient.id == Review.patient_id)\
        .filter(Review.doctor_id == doctor_id)\
        .order_by(Review.created_at.desc())\
        .all()

    # Flatten for template
    review_list = []
    for review, pat in reviews:
        review.patient = pat
        review_list.append(review)

    log_audit(
        action="VIEW_DOCTOR_PUBLIC_PROFILE",
        entity_type="doctor",
        entity_id=doctor_id,
        user_id=current_user.id,
        details={"ip": request.remote_addr}
    )

    return render_template(
        "search/doctor_public_profile.html",
        doctor=doctor, user=user, specialty=specialty,
        patient=patient, is_favorited=is_favorited,
        has_reviewed=has_reviewed, reviews=review_list
    )


def _format_location(doctor):
    parts = [p for p in [doctor.city, doctor.state] if p]
    return ", ".join(parts) if parts else "Location not specified"
