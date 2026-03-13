from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/patient")
@login_required
def patient_dashboard():
    return render_template("dashboard/patient_dashboard.html")


@dashboard_bp.route("/doctor")
@login_required
def doctor_dashboard():
    return render_template("dashboard/doctor_dashboard.html")