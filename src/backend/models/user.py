from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.backend import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(50), nullable=False)
    is_active     = db.Column(db.Boolean, default=True)
    is_verified   = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient_profile = db.relationship("Patient", backref="user", uselist=False, lazy=True)
    doctor_profile  = db.relationship("Doctor",  backref="user", uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_patient(self): return self.role == "patient"
    def is_doctor(self):  return self.role == "doctor"

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


class DoctorSpecialty(db.Model):
    __tablename__ = "doctor_specialties"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    doctors = db.relationship("Doctor", backref="specialty", lazy=True)

    def __repr__(self):
        return f"<Specialty {self.name}>"


class Patient(db.Model):
    __tablename__ = "patients"

    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    first_name          = db.Column(db.String(100), nullable=False)
    last_name           = db.Column(db.String(100), nullable=False)
    date_of_birth       = db.Column(db.Date, nullable=False)
    gender              = db.Column(db.String(20))
    phone               = db.Column(db.String(20), nullable=False)
    address_line1       = db.Column(db.String(255))
    address_line2       = db.Column(db.String(255))
    city                = db.Column(db.String(100))
    state               = db.Column(db.String(100))
    zip_code            = db.Column(db.String(20))
    country             = db.Column(db.String(100), default="USA")
    insurance_provider  = db.Column(db.String(255))
    insurance_id        = db.Column(db.String(100))
    preferred_payment   = db.Column(db.String(50), default="card")
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    favorites = db.relationship("Favorite", backref="patient", lazy=True,
                                foreign_keys="Favorite.patient_id")
    reviews   = db.relationship("Review", backref="patient", lazy=True,
                                foreign_keys="Review.patient_id")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Patient {self.full_name}>"


class Doctor(db.Model):
    __tablename__ = "doctors"

    id                       = db.Column(db.Integer, primary_key=True)
    user_id                  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    first_name               = db.Column(db.String(100), nullable=False)
    last_name                = db.Column(db.String(100), nullable=False)
    specialty_id             = db.Column(db.Integer, db.ForeignKey("doctor_specialties.id"))
    license_number           = db.Column(db.String(100), nullable=False, unique=True)
    years_experience         = db.Column(db.Integer, default=0)
    consultation_fee         = db.Column(db.Numeric(10, 2))
    bio                      = db.Column(db.Text)
    phone                    = db.Column(db.String(20), nullable=False)
    clinic_name              = db.Column(db.String(255))
    clinic_address           = db.Column(db.String(255))
    city                     = db.Column(db.String(100))
    state                    = db.Column(db.String(100))
    zip_code                 = db.Column(db.String(20))
    avg_appointment_duration = db.Column(db.Integer, default=30)
    is_verified              = db.Column(db.Boolean, default=False)
    created_at               = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at               = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    favorites = db.relationship("Favorite", backref="doctor", lazy=True,
                                foreign_keys="Favorite.doctor_id")
    reviews   = db.relationship("Review", backref="doctor", lazy=True,
                                foreign_keys="Review.doctor_id")

    @property
    def full_name(self):
        return f"Dr. {self.first_name} {self.last_name}"

    @property
    def avg_rating(self):
        if not self.reviews:
            return None
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    def __repr__(self):
        return f"<Doctor {self.full_name}>"


class Favorite(db.Model):
    """02.04 Add to Favorites — CA, ADT, CS crosscuts"""
    __tablename__ = "favorites"

    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id  = db.Column(db.Integer, db.ForeignKey("doctors.id"),  nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint — patient can only favorite a doctor once
    __table_args__ = (
        db.UniqueConstraint("patient_id", "doctor_id", name="uq_patient_doctor_favorite"),
    )

    def __repr__(self):
        return f"<Favorite patient={self.patient_id} doctor={self.doctor_id}>"


class Review(db.Model):
    """05.01 Submit Review — ER, ADT, ET-In crosscuts"""
    __tablename__ = "reviews"

    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id  = db.Column(db.Integer, db.ForeignKey("doctors.id"),  nullable=False)
    rating     = db.Column(db.Integer, nullable=False)   # 1-5 stars
    title      = db.Column(db.String(100))
    body       = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One review per patient per doctor
    __table_args__ = (
        db.UniqueConstraint("patient_id", "doctor_id", name="uq_patient_doctor_review"),
    )

    def __repr__(self):
        return f"<Review patient={self.patient_id} doctor={self.doctor_id} rating={self.rating}>"


class AuditLog(db.Model):
    """ADT crosscut — tracks all user actions."""
    __tablename__ = "audit_log"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action      = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id   = db.Column(db.Integer)
    ip_address  = db.Column(db.String(45))
    details     = db.Column(db.JSON)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} by user_id={self.user_id}>"
