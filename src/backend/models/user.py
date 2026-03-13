from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.backend import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """
    Core user model — DF-Out crosscut: feeds all modules.
    ET-In crosscut: role controls feature access.
    """
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(50), nullable=False)  # patient | doctor | ...
    is_active     = db.Column(db.Boolean, default=True)
    is_verified   = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient_profile = db.relationship("Patient", backref="user", uselist=False, lazy=True)
    doctor_profile  = db.relationship("Doctor", backref="user", uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_patient(self):
        return self.role == "patient"

    def is_doctor(self):
        return self.role == "doctor"

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


class DoctorSpecialty(db.Model):
    """DS crosscut — specialties lookup table."""
    __tablename__ = "doctor_specialties"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    doctors = db.relationship("Doctor", backref="specialty", lazy=True)

    def __repr__(self):
        return f"<Specialty {self.name}>"


class Patient(db.Model):
    """
    01.01 Register Patient
    CS crosscut: patient profile config (contact, insurance, payment)
    """
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
    # CS: insurance config
    insurance_provider  = db.Column(db.String(255))
    insurance_id        = db.Column(db.String(100))
    # DDD: default payment from profile
    preferred_payment   = db.Column(db.String(50), default="card")
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Patient {self.full_name}>"


class Doctor(db.Model):
    """
    01.02 Register Doctor
    CS crosscut: doctor profile config (specialty, fees, credentials)
    DS crosscut: specialty_id FK
    """
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
    # DDD: default appointment duration by specialty
    avg_appointment_duration = db.Column(db.Integer, default=30)
    is_verified              = db.Column(db.Boolean, default=False)
    created_at               = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at               = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def full_name(self):
        return f"Dr. {self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Doctor {self.full_name}>"


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