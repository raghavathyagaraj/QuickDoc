import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from src.backend import db
from src.backend.models.user import Doctor, DoctorSpecialty, Patient, User
from src.backend.utils.audit import log_audit

logger = logging.getLogger(__name__)
search_bp = Blueprint("search", __name__)


# ── 02.01 / 02.02 / 02.03 — Unified Doctor Search ─────────────────────────

@search_bp.route("/")
@login_required
def search():
    """
    Unified search handling specialty, location and name.
    ET-In: login required, patient only.
    CA: results are query-driven (no heavy caching needed at this scale).
    PF: single joined query for performance.
    """
    # ET-In: only patients can search for doctors
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    # FV: sanitize inputs
    query_text  = request.args.get("q", "").strip()
    specialty   = request.args.get("specialty", "").strip()
    location    = request.args.get("location", "").strip()
    sort_by     = request.args.get("sort", "name")  # name | fee | experience

    try:
        # Base query — join Doctor → User → Specialty
        base = (
            db.session.query(Doctor, DoctorSpecialty, User)
            .join(User, User.id == Doctor.user_id)
            .outerjoin(DoctorSpecialty, DoctorSpecialty.id == Doctor.specialty_id)
            .filter(User.is_active == True)
        )

        # 02.01 — Search by Specialty (DS crosscut)
        if specialty:
            base = base.filter(
                DoctorSpecialty.name.ilike(f"%{specialty}%")
            )

        # 02.02 — Search by Location
        if location:
            base = base.filter(
                or_(
                    Doctor.city.ilike(f"%{location}%"),
                    Doctor.state.ilike(f"%{location}%"),
                    Doctor.zip_code.ilike(f"%{location}%"),
                    Doctor.clinic_address.ilike(f"%{location}%")
                )
            )

        # 02.03 — Search by Name
        if query_text:
            base = base.filter(
                or_(
                    Doctor.first_name.ilike(f"%{query_text}%"),
                    Doctor.last_name.ilike(f"%{query_text}%"),
                    DoctorSpecialty.name.ilike(f"%{query_text}%"),
                    Doctor.clinic_name.ilike(f"%{query_text}%")
                )
            )

        # Sorting — PF crosscut
        if sort_by == "fee":
            base = base.order_by(Doctor.consultation_fee.asc())
        elif sort_by == "experience":
            base = base.order_by(Doctor.years_experience.desc())
        else:
            base = base.order_by(Doctor.last_name.asc(), Doctor.first_name.asc())

        results = base.all()

        # ADT crosscut — log search
        log_audit(
            action="DOCTOR_SEARCH",
            entity_type="search",
            entity_id=None,
            user_id=current_user.id,
            details={
                "q": query_text,
                "specialty": specialty,
                "location": location,
                "results_count": len(results),
                "ip": request.remote_addr
            }
        )

        # DS crosscut — all specialties for filter sidebar
        specialties = DoctorSpecialty.query.order_by(DoctorSpecialty.name).all()

        # ER crosscut — enrich results with computed fields
        enriched = []
        for doctor, spec, user in results:
            enriched.append({
                "doctor": doctor,
                "specialty": spec,
                "user": user,
                "is_verified": doctor.is_verified,
                "has_bio": bool(doctor.bio),
                "location_display": _format_location(doctor),
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
            patient=Patient.query.filter_by(user_id=current_user.id).first()
        )

    except Exception as exc:
        # ExHL crosscut
        logger.error("Search failed: %s", exc, exc_info=True)
        return render_template(
            "search/search_results.html",
            results=[],
            specialties=DoctorSpecialty.query.order_by(DoctorSpecialty.name).all(),
            query_text=query_text,
            selected_specialty=specialty,
            selected_location=location,
            sort_by=sort_by,
            result_count=0,
            error="Search is temporarily unavailable. Please try again.",
            patient=Patient.query.filter_by(user_id=current_user.id).first()
        )


# ── 02.06 — View Doctor Public Profile ─────────────────────────────────────

@search_bp.route("/doctor/<int:doctor_id>")
@login_required
def doctor_public_profile(doctor_id):
    """
    Public-facing doctor profile for patients.
    ET-In: login required.
    ER: enrichment — verified badge, specialty details.
    DF-In: receives doctor_id from search results.
    """
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        user   = User.query.get(doctor.user_id)
        specialty = DoctorSpecialty.query.get(doctor.specialty_id)

        log_audit(
            action="VIEW_DOCTOR_PUBLIC_PROFILE",
            entity_type="doctor",
            entity_id=doctor_id,
            user_id=current_user.id,
            details={"ip": request.remote_addr}
        )

        patient = Patient.query.filter_by(user_id=current_user.id).first()

        return render_template(
            "search/doctor_public_profile.html",
            doctor=doctor,
            user=user,
            specialty=specialty,
            patient=patient
        )

    except Exception as exc:
        logger.error("Doctor profile view failed: %s", exc, exc_info=True)
        return redirect(url_for("search.search"))


# ── Helper ──────────────────────────────────────────────────────────────────

def _format_location(doctor):
    parts = [p for p in [doctor.city, doctor.state] if p]
    return ", ".join(parts) if parts else "Location not specified"