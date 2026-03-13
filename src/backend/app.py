import sys
import os

print("[QuickDoc] Starting...", flush=True)

try:
    from src.backend import create_app, db
    from src.backend.models.user import DoctorSpecialty
    print("[QuickDoc] Imports OK", flush=True)
except Exception as e:
    print(f"[QuickDoc] IMPORT ERROR: {e}", flush=True)
    sys.exit(1)

try:
    app = create_app()
    print("[QuickDoc] App created OK", flush=True)
except Exception as e:
    print(f"[QuickDoc] APP CREATE ERROR: {e}", flush=True)
    sys.exit(1)


def seed_specialties():
    if DoctorSpecialty.query.count() == 0:
        specialties = [
            "General Medicine", "Cardiology", "Dermatology",
            "Neurology", "Orthopedics", "Pediatrics",
            "Gynecology", "Ophthalmology", "ENT (Ear, Nose, Throat)", "Psychiatry"
        ]
        for name in specialties:
            db.session.add(DoctorSpecialty(name=name))
        db.session.commit()
        print(f"[QuickDoc] Seeded specialties.", flush=True)


try:
    with app.app_context():
        db.create_all()
        seed_specialties()
        print("[QuickDoc] Database ready.", flush=True)
except Exception as e:
    print(f"[QuickDoc] DB ERROR: {e}", flush=True)
    sys.exit(1)

print("[QuickDoc] Launching Flask on port 5000...", flush=True)
app.run(host="0.0.0.0", port=5000, debug=True)