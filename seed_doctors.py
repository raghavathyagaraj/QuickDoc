"""
Seed 1000 realistic doctors across all specialties and US cities.
Run: docker cp seed_1000_doctors.py quickdoc-web-1:/app/seed_1000_doctors.py
     docker exec quickdoc-web-1 python seed_1000_doctors.py
"""
import sys
import random
sys.path.insert(0, '/app')

from src.backend import create_app, db
from src.backend.models.user import User, Doctor, DoctorSpecialty

app = create_app()

# ── US Cities ────────────────────────────────────────────────────────────────
US_CITIES = [
    ("New York", "NY", "100"), ("Los Angeles", "CA", "900"),
    ("Chicago", "IL", "606"), ("Houston", "TX", "770"),
    ("Phoenix", "AZ", "850"), ("Philadelphia", "PA", "191"),
    ("San Antonio", "TX", "782"), ("San Diego", "CA", "921"),
    ("Dallas", "TX", "752"), ("San Jose", "CA", "951"),
    ("Austin", "TX", "787"), ("Jacksonville", "FL", "322"),
    ("Fort Worth", "TX", "761"), ("Columbus", "OH", "432"),
    ("Charlotte", "NC", "282"), ("Indianapolis", "IN", "462"),
    ("San Francisco", "CA", "941"), ("Seattle", "WA", "981"),
    ("Denver", "CO", "802"), ("Nashville", "TN", "372"),
    ("Oklahoma City", "OK", "731"), ("El Paso", "TX", "799"),
    ("Washington", "DC", "200"), ("Las Vegas", "NV", "891"),
    ("Louisville", "KY", "402"), ("Memphis", "TN", "381"),
    ("Portland", "OR", "972"), ("Baltimore", "MD", "212"),
    ("Milwaukee", "WI", "532"), ("Albuquerque", "NM", "871"),
    ("Tucson", "AZ", "857"), ("Fresno", "CA", "937"),
    ("Sacramento", "CA", "958"), ("Mesa", "AZ", "852"),
    ("Kansas City", "MO", "641"), ("Atlanta", "GA", "303"),
    ("Omaha", "NE", "681"), ("Colorado Springs", "CO", "809"),
    ("Raleigh", "NC", "276"), ("Long Beach", "CA", "908"),
    ("Virginia Beach", "VA", "234"), ("Minneapolis", "MN", "554"),
    ("Tampa", "FL", "336"), ("New Orleans", "LA", "701"),
    ("Arlington", "TX", "760"), ("Bakersfield", "CA", "933"),
    ("Honolulu", "HI", "968"), ("Anaheim", "CA", "928"),
    ("Aurora", "CO", "800"), ("Santa Ana", "CA", "927"),
    ("Boston", "MA", "021"), ("Miami", "FL", "331"),
    ("Cleveland", "OH", "441"), ("Pittsburgh", "PA", "152"),
    ("Detroit", "MI", "482"), ("Salt Lake City", "UT", "841"),
    ("Richmond", "VA", "232"), ("Hartford", "CT", "061"),
    ("Birmingham", "AL", "352"), ("Buffalo", "NY", "142"),
    ("Rochester", "NY", "146"), ("St. Louis", "MO", "631"),
    ("Cincinnati", "OH", "452"), ("Boise", "ID", "837"),
]

# ── First Names ───────────────────────────────────────────────────────────────
FIRST_NAMES_M = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
    "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
    "Kenneth", "Kevin", "Brian", "George", "Timothy", "Ronald", "Edward",
    "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric",
    "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
    "Raj", "Amit", "Priya", "Wei", "Lin", "Ali", "Omar", "Amir",
    "Carlos", "Miguel", "Juan", "Pedro", "Luis", "Hiroshi", "Kenji",
]

FIRST_NAMES_F = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth",
    "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty",
    "Margaret", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily",
    "Donna", "Michelle", "Carol", "Amanda", "Melissa", "Deborah",
    "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen",
    "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma",
    "Priya", "Ananya", "Mei", "Yuki", "Fatima", "Layla", "Sofia",
    "Isabella", "Mia", "Charlotte", "Amara", "Zoe", "Chloe", "Ava",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Patel", "Shah", "Kumar", "Singh", "Chen",
    "Wang", "Liu", "Zhang", "Kim", "Park", "Choi", "Yamamoto", "Tanaka",
    "Okafor", "Mensah", "Abebe", "Hassan", "Ahmed", "Khan", "Ali",
    "Murphy", "O'Brien", "Sullivan", "Walsh", "Kelly", "Ryan", "Burke",
]

# ── Clinic Name Templates ─────────────────────────────────────────────────────
CLINIC_TEMPLATES = [
    "{city} {specialty} Center", "{last_name} Medical Group",
    "{specialty} Associates of {city}", "Advanced {specialty} Care",
    "{city} Health & {specialty}", "Premier {specialty} Clinic",
    "{last_name} & Associates", "{city} Medical Center",
    "Integrated {specialty} Care", "{specialty} Institute of {city}",
    "Metropolitan {specialty} Group", "{last_name} Healthcare",
    "Center for {specialty}", "{city} Specialty Clinic",
    "Regional {specialty} Associates",
]

# ── Bio Templates ─────────────────────────────────────────────────────────────
BIO_TEMPLATES = [
    "Board-certified {specialty} specialist with {years} years of experience serving patients in {city}. Committed to delivering compassionate, evidence-based care.",
    "Dr. {last_name} is a highly experienced {specialty} physician with {years} years of practice. Specializes in the latest minimally invasive techniques.",
    "Dedicated to excellence in {specialty} care, Dr. {last_name} brings {years} years of clinical expertise to patients throughout {city} and surrounding areas.",
    "Fellowship-trained {specialty} specialist with extensive research background. Dr. {last_name} has served {city} patients for over {years} years.",
    "Award-winning {specialty} physician recognized for patient-centered care. {years} years of experience treating complex cases in {city}.",
    "Dr. {last_name} completed training at top academic medical centers and has dedicated {years} years to advancing {specialty} care in {city}.",
    "Compassionate {specialty} specialist committed to improving patient outcomes. Dr. {last_name} brings {years} years of expertise to the {city} community.",
]

# ── Specialty Config ──────────────────────────────────────────────────────────
SPECIALTY_CONFIG = {
    "General Medicine":    {"fee_min": 80,  "fee_max": 180, "duration": 30},
    "Cardiology":          {"fee_min": 150, "fee_max": 350, "duration": 45},
    "Neurology":           {"fee_min": 150, "fee_max": 320, "duration": 45},
    "Orthopedics":         {"fee_min": 160, "fee_max": 380, "duration": 45},
    "Pediatrics":          {"fee_min": 90,  "fee_max": 220, "duration": 30},
    "Dermatology":         {"fee_min": 120, "fee_max": 280, "duration": 30},
    "Gynecology":          {"fee_min": 120, "fee_max": 280, "duration": 30},
    "Ophthalmology":       {"fee_min": 130, "fee_max": 300, "duration": 30},
    "ENT (Ear, Nose, Throat)": {"fee_min": 130, "fee_max": 290, "duration": 30},
    "Psychiatry":          {"fee_min": 150, "fee_max": 350, "duration": 60},
}


def generate_doctor(index, specialty_name, specialty_config):
    """Generate one realistic doctor record."""
    city, state, zip_prefix = random.choice(US_CITIES)
    is_male = random.random() > 0.45
    first_name = random.choice(FIRST_NAMES_M if is_male else FIRST_NAMES_F)
    last_name = random.choice(LAST_NAMES)
    years = random.randint(2, 30)
    fee = round(random.uniform(
        specialty_config["fee_min"],
        specialty_config["fee_max"]
    ), 0)
    zip_code = zip_prefix + str(random.randint(10, 99))

    # Clinic name
    clinic_template = random.choice(CLINIC_TEMPLATES)
    clinic_name = clinic_template.format(
        city=city,
        specialty=specialty_name.split("(")[0].strip(),
        last_name=last_name
    )

    # Bio
    bio_template = random.choice(BIO_TEMPLATES)
    bio = bio_template.format(
        specialty=specialty_name,
        last_name=last_name,
        years=years,
        city=city
    )

    # Street addresses
    street_num = random.randint(100, 9999)
    street_names = [
        "Main St", "Oak Ave", "Maple Dr", "Park Blvd", "Medical Center Dr",
        "Healthcare Pkwy", "University Blvd", "Central Ave", "Commerce St",
        "Broadway", "Washington Blvd", "Lincoln Ave", "Jefferson St",
    ]
    address = f"{street_num} {random.choice(street_names)}"

    return {
        "email": f"dr.{first_name.lower()}.{last_name.lower()}.{index}@quickdoc-med.com",
        "password": "Doctor1234",
        "first_name": first_name,
        "last_name": last_name,
        "specialty": specialty_name,
        "license": f"LIC{index:05d}",
        "experience": years,
        "fee": fee,
        "phone": f"{random.randint(200,999)}{random.randint(200,999)}{random.randint(1000,9999)}",
        "bio": bio,
        "clinic_name": clinic_name,
        "clinic_address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "is_verified": random.random() > 0.15,  # 85% verified
        "duration": specialty_config["duration"],
    }


def seed():
    with app.app_context():
        specialties = {s.name: s for s in DoctorSpecialty.query.all()}

        if not specialties:
            print("❌ No specialties found! Run the app first to seed specialties.")
            return

        # Check existing count
        existing = Doctor.query.count()
        print(f"📊 Existing doctors: {existing}")

        TARGET = 1000
        per_specialty = TARGET // len(specialties)
        remainder = TARGET % len(specialties)

        print(f"🎯 Target: {TARGET} doctors across {len(specialties)} specialties")
        print(f"📋 ~{per_specialty} doctors per specialty\n")

        seeded = 0
        skipped = 0
        index = existing + 1000  # offset to avoid license conflicts

        for spec_name, spec_obj in specialties.items():
            config = SPECIALTY_CONFIG.get(spec_name, {"fee_min": 100, "fee_max": 250, "duration": 30})
            count = per_specialty + (1 if remainder > 0 else 0)
            remainder = max(0, remainder - 1)

            for _ in range(count):
                data = generate_doctor(index, spec_name, config)
                index += 1

                # Skip if email exists
                if User.query.filter_by(email=data["email"]).first():
                    skipped += 1
                    continue

                # Skip if license exists
                if Doctor.query.filter_by(license_number=data["license"]).first():
                    skipped += 1
                    continue

                try:
                    user = User(
                        email=data["email"],
                        role="doctor",
                        is_active=True,
                        is_verified=True
                    )
                    user.set_password(data["password"])
                    db.session.add(user)
                    db.session.flush()

                    doctor = Doctor(
                        user_id=user.id,
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                        specialty_id=spec_obj.id,
                        license_number=data["license"],
                        years_experience=data["experience"],
                        consultation_fee=data["fee"],
                        phone=data["phone"],
                        bio=data["bio"],
                        clinic_name=data["clinic_name"],
                        clinic_address=data["clinic_address"],
                        city=data["city"],
                        state=data["state"],
                        zip_code=data["zip_code"],
                        avg_appointment_duration=data["duration"],
                        is_verified=data["is_verified"]
                    )
                    db.session.add(doctor)
                    seeded += 1

                    # Commit in batches of 50
                    if seeded % 50 == 0:
                        db.session.commit()
                        print(f"  ✅ Seeded {seeded} doctors so far...")

                except Exception as e:
                    db.session.rollback()
                    skipped += 1

        db.session.commit()
        total = Doctor.query.count()
        print(f"\n🎉 Done!")
        print(f"   Seeded this run : {seeded}")
        print(f"   Skipped         : {skipped}")
        print(f"   Total in DB     : {total}")


if __name__ == "__main__":
    seed()