import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.backend import db
from src.backend.models.user import Patient, Doctor, DoctorSpecialty, Favorite, Review, User
from src.backend.utils.audit import log_audit

logger = logging.getLogger(__name__)
social_bp = Blueprint("social", __name__)


# ── 02.04 Add / Remove Favorite ────────────────────────────────────────────

@social_bp.route("/favorite/<int:doctor_id>", methods=["POST"])
@login_required
def toggle_favorite(doctor_id):
    """ET-In: patient only. ADT: logged. CA: returns current state."""
    if current_user.role != "patient":
        return jsonify({"error": "Only patients can add favorites"}), 403

    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()
    doctor  = Doctor.query.get_or_404(doctor_id)

    existing = Favorite.query.filter_by(
        patient_id=patient.id,
        doctor_id=doctor_id
    ).first()

    try:
        if existing:
            # Remove favorite
            db.session.delete(existing)
            db.session.commit()
            log_audit(
                action="REMOVE_FAVORITE",
                entity_type="doctor",
                entity_id=doctor_id,
                user_id=current_user.id,
                details={"doctor_name": doctor.full_name, "ip": request.remote_addr}
            )
            return jsonify({"favorited": False, "message": f"Removed Dr. {doctor.last_name} from favorites"})
        else:
            # Add favorite
            fav = Favorite(patient_id=patient.id, doctor_id=doctor_id)
            db.session.add(fav)
            db.session.commit()
            log_audit(
                action="ADD_FAVORITE",
                entity_type="doctor",
                entity_id=doctor_id,
                user_id=current_user.id,
                details={"doctor_name": doctor.full_name, "ip": request.remote_addr}
            )
            return jsonify({"favorited": True, "message": f"Added Dr. {doctor.last_name} to favorites"})

    except Exception as exc:
        db.session.rollback()
        logger.error("Favorite toggle failed: %s", exc, exc_info=True)
        return jsonify({"error": "Something went wrong"}), 500


# ── 05.01 Submit Review ─────────────────────────────────────────────────────

@social_bp.route("/review/<int:doctor_id>", methods=["POST"])
@login_required
def submit_review(doctor_id):
    """ET-In: patient only. ER: enriches doctor rating. ADT: logged."""
    if current_user.role != "patient":
        flash("Only patients can submit reviews.", "danger")
        return redirect(url_for("search.doctor_public_profile", doctor_id=doctor_id))

    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()
    doctor  = Doctor.query.get_or_404(doctor_id)

    # FV crosscut
    rating = request.form.get("rating", type=int)
    title  = request.form.get("title", "").strip()
    body   = request.form.get("body", "").strip()

    if not rating or rating < 1 or rating > 5:
        flash("Please select a rating between 1 and 5 stars.", "danger")
        return redirect(url_for("search.doctor_public_profile", doctor_id=doctor_id))

    if not body or len(body) < 10:
        flash("Review must be at least 10 characters.", "danger")
        return redirect(url_for("search.doctor_public_profile", doctor_id=doctor_id))

    if len(body) > 1000:
        flash("Review must be under 1000 characters.", "danger")
        return redirect(url_for("search.doctor_public_profile", doctor_id=doctor_id))

    # ExHL — check duplicate review
    existing = Review.query.filter_by(
        patient_id=patient.id,
        doctor_id=doctor_id
    ).first()

    if existing:
        flash("You have already reviewed this doctor. You can only submit one review per doctor.", "warning")
        return redirect(url_for("search.doctor_public_profile", doctor_id=doctor_id))

    try:
        review = Review(
            patient_id=patient.id,
            doctor_id=doctor_id,
            rating=rating,
            title=title if title else None,
            body=body
        )
        db.session.add(review)
        db.session.commit()

        log_audit(
            action="SUBMIT_REVIEW",
            entity_type="doctor",
            entity_id=doctor_id,
            user_id=current_user.id,
            details={
                "doctor_name": doctor.full_name,
                "rating": rating,
                "ip": request.remote_addr
            }
        )

        flash(f"Your review for Dr. {doctor.last_name} has been submitted!", "success")

    except Exception as exc:
        db.session.rollback()
        logger.error("Review submit failed: %s", exc, exc_info=True)
        flash("Something went wrong. Please try again.", "danger")

    return redirect(url_for("search.doctor_public_profile", doctor_id=doctor_id))


# ── Patient Favorites Page (for dashboard) ─────────────────────────────────

@social_bp.route("/favorites")
@login_required
def my_favorites():
    """CA: load patient favorites for dashboard display."""
    if current_user.role != "patient":
        return redirect(url_for("dashboard.doctor_dashboard"))

    patient = Patient.query.filter_by(user_id=current_user.id).first_or_404()

    favorites = db.session.query(Favorite, Doctor, DoctorSpecialty, User)\
        .join(Doctor, Doctor.id == Favorite.doctor_id)\
        .join(User, User.id == Doctor.user_id)\
        .outerjoin(DoctorSpecialty, DoctorSpecialty.id == Doctor.specialty_id)\
        .filter(Favorite.patient_id == patient.id)\
        .order_by(Favorite.created_at.desc())\
        .all()

    return render_template(
        "social/favorites.html",
        favorites=favorites,
        patient=patient
    )
