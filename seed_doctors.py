"""
Seed fake doctors for Sprint 2 testing.
Run once: docker exec quickdoc-web-1 python seed_doctors.py
"""
import sys
import os
sys.path.insert(0, '/app')

from src.backend import create_app, db
from src.backend.models.user import User, Doctor, DoctorSpecialty
from werkzeug.security import generate_password_hash

app = create_app()

FAKE_DOCTORS = [
    {
        "email": "dr.smith@quickdoc.com",
        "password": "Test1234",
        "first_name": "James",
        "last_name": "Smith",
        "specialty": "Cardiology",
        "license": "LIC001",
        "experience": 15,
        "fee": 200.00,
        "phone": "2125550001",
        "bio": "Board-certified cardiologist with 15 years of experience in interventional cardiology.",
        "clinic_name": "Heart Care Center",
        "clinic_address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "is_verified": True
    },
    {
        "email": "dr.patel@quickdoc.com",
        "password": "Test1234",
        "first_name": "Priya",
        "last_name": "Patel",
        "specialty": "Neurology",
        "license": "LIC002",
        "experience": 10,
        "fee": 175.00,
        "phone": "2125550002",
        "bio": "Specialist in neurodegenerative diseases and movement disorders.",
        "clinic_name": "NeuroHealth Clinic",
        "clinic_address": "456 Park Ave",
        "city": "New York",
        "state": "NY",
        "zip_code": "10022",
        "is_verified": True
    },
    {
        "email": "dr.johnson@quickdoc.com",
        "password": "Test1234",
        "first_name": "Emily",
        "last_name": "Johnson",
        "specialty": "Dermatology",
        "license": "LIC003",
        "experience": 8,
        "fee": 150.00,
        "phone": "2125550003",
        "bio": "Expert in medical and cosmetic dermatology with a focus on skin cancer prevention.",
        "clinic_name": "ClearSkin Dermatology",
        "clinic_address": "789 Broadway",
        "city": "Brooklyn",
        "state": "NY",
        "zip_code": "11201",
        "is_verified": True
    },
    {
        "email": "dr.lee@quickdoc.com",
        "password": "Test1234",
        "first_name": "Kevin",
        "last_name": "Lee",
        "specialty": "Orthopedics",
        "license": "LIC004",
        "experience": 12,
        "fee": 225.00,
        "phone": "2125550004",
        "bio": "Orthopedic surgeon specializing in sports medicine and joint replacement.",
        "clinic_name": "Active Orthopedics",
        "clinic_address": "321 Lexington Ave",
        "city": "New York",
        "state": "NY",
        "zip_code": "10016",
        "is_verified": True
    },
    {
        "email": "dr.garcia@quickdoc.com",
        "password": "Test1234",
        "first_name": "Maria",
        "last_name": "Garcia",
        "specialty": "Pediatrics",
        "license": "LIC005",
        "experience": 6,
        "fee": 120.00,
        "phone": "2125550005",
        "bio": "Compassionate pediatrician dedicated to children's health from birth through adolescence.",
        "clinic_name": "Little Stars Pediatrics",
        "clinic_address": "555 5th Ave",
        "city": "Queens",
        "state": "NY",
        "zip_code": "11354",
        "is_verified": True
    },
    {
        "email": "dr.chen@quickdoc.com",
        "password": "Test1234",
        "first_name": "Michael",
        "last_name": "Chen",
        "specialty": "General Medicine",
        "license": "LIC006",
        "experience": 20,
        "fee": 100.00,
        "phone": "2125550006",
        "bio": "Family medicine physician providing comprehensive primary care for all ages.",
        "clinic_name": "ChenCare Family Medicine",
        "clinic_address": "888 Queens Blvd",
        "city": "Queens",
        "state": "NY",
        "zip_code": "11373",
        "is_verified": True
    },
    {
        "email": "dr.wilson@quickdoc.com",
        "password": "Test1234",
        "first_name": "Sarah",
        "last_name": "Wilson",
        "specialty": "Gynecology",
        "license": "LIC007",
        "experience": 9,
        "fee": 160.00,
        "phone": "2125550007",
        "bio": "OB/GYN focused on women's health, prenatal care, and minimally invasive procedures.",
        "clinic_name": "Women's Wellness Center",
        "clinic_address": "222 Madison Ave",
        "city": "New York",
        "state": "NY",
        "zip_code": "10016",
        "is_verified": True
    },
    {
        "email": "dr.brown@quickdoc.com",
        "password": "Test1234",
        "first_name": "David",
        "last_name": "Brown",
        "specialty": "Ophthalmology",
        "license": "LIC008",
        "experience": 14,
        "fee": 180.00,
        "phone": "2125550008",
        "bio": "Ophthalmologist specializing in LASIK surgery and treatment of retinal diseases.",
        "clinic_name": "ClearVision Eye Center",
        "clinic_address": "444 Park Ave South",
        "city": "New York",
        "state": "NY",
        "zip_code": "10016",
        "is_verified": False
    },
    {
        "email": "dr.taylor@quickdoc.com",
        "password": "Test1234",
        "first_name": "Lisa",
        "last_name": "Taylor",
        "specialty": "ENT (Ear, Nose, Throat)",
        "license": "LIC009",
        "experience": 11,
        "fee": 165.00,
        "phone": "2125550009",
        "bio": "ENT specialist with expertise in sinus surgery, hearing loss, and sleep disorders.",
        "clinic_name": "Metro ENT Associates",
        "clinic_address": "777 7th Ave",
        "city": "New York",
        "state": "NY",
        "zip_code": "10019",
        "is_verified": True
    },
    {
        "email": "dr.anderson@quickdoc.com",
        "password": "Test1234",
        "first_name": "Robert",
        "last_name": "Anderson",
        "specialty": "Psychiatry",
        "license": "LIC010",
        "experience": 7,
        "fee": 190.00,
        "phone": "2125550010",
        "bio": "Psychiatrist specializing in anxiety, depression, and cognitive behavioral therapy.",
        "clinic_name": "MindWell Psychiatry",
        "clinic_address": "100 Central Park West",
        "city": "New York",
        "state": "NY",
        "zip_code": "10023",
        "is_verified": True
    },
]


def seed():
    with app.app_context():
        seeded = 0
        skipped = 0

        for doc_data in FAKE_DOCTORS:
            # Skip if email already exists
            if User.query.filter_by(email=doc_data["email"]).first():
                print(f"  ⏭️  Skipping {doc_data['email']} — already exists")
                skipped += 1
                continue

            # Get specialty
            specialty = DoctorSpecialty.query.filter_by(
                name=doc_data["specialty"]
            ).first()
            if not specialty:
                print(f"  ⚠️  Specialty '{doc_data['specialty']}' not found — skipping")
                skipped += 1
                continue

            # Create user
            user = User(
                email=doc_data["email"],
                role="doctor",
                is_active=True,
                is_verified=True
            )
            user.set_password(doc_data["password"])
            db.session.add(user)
            db.session.flush()

            # Create doctor profile
            doctor = Doctor(
                user_id=user.id,
                first_name=doc_data["first_name"],
                last_name=doc_data["last_name"],
                specialty_id=specialty.id,
                license_number=doc_data["license"],
                years_experience=doc_data["experience"],
                consultation_fee=doc_data["fee"],
                phone=doc_data["phone"],
                bio=doc_data["bio"],
                clinic_name=doc_data["clinic_name"],
                clinic_address=doc_data["clinic_address"],
                city=doc_data["city"],
                state=doc_data["state"],
                zip_code=doc_data["zip_code"],
                avg_appointment_duration=30,
                is_verified=doc_data["is_verified"]
            )
            db.session.add(doctor)
            seeded += 1
            print(f"  ✅ Seeded Dr. {doc_data['first_name']} {doc_data['last_name']} — {doc_data['specialty']}")

        db.session.commit()
        print(f"\n✅ Done! Seeded: {seeded}, Skipped: {skipped}")


if __name__ == "__main__":
    seed()
