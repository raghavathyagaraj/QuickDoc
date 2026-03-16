from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, DateField,
    TextAreaField, DecimalField, IntegerField, BooleanField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp,
    NumberRange, Optional, ValidationError
)
from datetime import date
from src.backend.models.user import User


# ── shared password validator ────────────────────────────────
def strong_password(form, field):
    """FV crosscut: password strength validation."""
    p = field.data
    if len(p) < 8:
        raise ValidationError("Password must be at least 8 characters.")
    if not any(c.isupper() for c in p):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in p):
        raise ValidationError("Password must contain at least one number.")


def no_future_dob(form, field):
    """FV crosscut: date of birth cannot be in the future."""
    if field.data and field.data >= date.today():
        raise ValidationError("Date of birth cannot be today or in the future.")


def min_age(min_years):
    """FV crosscut: minimum age check."""
    def validator(form, field):
        if field.data:
            today = date.today()
            age = today.year - field.data.year - (
                (today.month, today.day) < (field.data.month, field.data.day)
            )
            if age < min_years:
                raise ValidationError(f"You must be at least {min_years} years old.")
    return validator


def unique_email(form, field):
    """FV crosscut: email must not already be registered."""
    user = User.query.filter_by(email=field.data.lower()).first()
    if user:
        raise ValidationError("This email is already registered. Please log in.")


# ── 01.03 Login ──────────────────────────────────────────────
class LoginForm(FlaskForm):
    # FV crosscut: email format + required
    email = StringField("Email", validators=[
        DataRequired(message="Email is required."),
        Email(message="Enter a valid email address."),
        Length(max=255)
    ])
    # FV crosscut: password required
    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required.")
    ])
    # DDD crosscut: remember me checkbox (default off)
    remember_me = BooleanField("Remember Me", default=False)


# ── 01.01 Register Patient ───────────────────────────────────
class RegisterPatientForm(FlaskForm):
    # Account credentials
    email    = StringField("Email", validators=[
        DataRequired(), Email(message="Enter a valid email address."),
        Length(max=255), unique_email
    ])
    password = PasswordField("Password", validators=[
        DataRequired(), strong_password
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match.")
    ])

    # Personal info (CS crosscut - patient profile)
    first_name = StringField("First Name", validators=[
        DataRequired(), Length(min=2, max=100),
        Regexp(r'^[A-Za-z\s\-]+$', message="Name can only contain letters, spaces, or hyphens.")
    ])
    last_name = StringField("Last Name", validators=[
        DataRequired(), Length(min=2, max=100),
        Regexp(r'^[A-Za-z\s\-]+$', message="Name can only contain letters, spaces, or hyphens.")
    ])
    date_of_birth = DateField("Date of Birth", validators=[
        DataRequired(), no_future_dob, min_age(18)
    ])
    gender = SelectField("Gender", choices=[
        ("", "-- Select --"),
        ("male", "Male"),
        ("female", "Female"),
        ("non_binary", "Non-Binary"),
        ("prefer_not_to_say", "Prefer Not to Say")
    ], validators=[Optional()])

    # Contact info (FV crosscut)
    phone = StringField("Phone Number", validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{10,15}$', message="Enter a valid phone number (10-15 digits).")
    ])
    address_line1 = StringField("Address Line 1", validators=[Optional(), Length(max=255)])
    address_line2 = StringField("Address Line 2", validators=[Optional(), Length(max=255)])
    city          = StringField("City",  validators=[Optional(), Length(max=100)])
    state         = StringField("State", validators=[Optional(), Length(max=100)])
    zip_code      = StringField("ZIP Code", validators=[
        Optional(),
        Regexp(r'^\d{5}(-\d{4})?$', message="Enter a valid US ZIP code (e.g. 10001 or 10001-1234).")
    ])

    # Insurance (CS crosscut)
    insurance_provider = StringField("Insurance Provider", validators=[Optional(), Length(max=255)])
    insurance_id       = StringField("Insurance ID / Member #", validators=[Optional(), Length(max=100)])

    # DDD crosscut: default payment (pre-populated as 'card')
    preferred_payment = SelectField("Preferred Payment Method", choices=[
        ("card",         "Credit / Debit Card"),
        ("insurance",    "Insurance"),
        ("cash",         "Cash"),
    ], default="card", validators=[Optional()])


# ── 01.02 Register Doctor ────────────────────────────────────
class RegisterDoctorForm(FlaskForm):
    # Account credentials
    email    = StringField("Email", validators=[
        DataRequired(), Email(message="Enter a valid email address."),
        Length(max=255), unique_email
    ])
    password = PasswordField("Password", validators=[
        DataRequired(), strong_password
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match.")
    ])

    # Personal info (CS crosscut - doctor profile)
    first_name = StringField("First Name", validators=[
        DataRequired(), Length(min=2, max=100),
        Regexp(r'^[A-Za-z\s\-]+$', message="Name can only contain letters, spaces, or hyphens.")
    ])
    last_name = StringField("Last Name", validators=[
        DataRequired(), Length(min=2, max=100),
        Regexp(r'^[A-Za-z\s\-]+$', message="Name can only contain letters, spaces, or hyphens.")
    ])

    # DS crosscut: Doctor Specialty — choices populated dynamically in route
    specialty_id = SelectField("Medical Specialty", coerce=int, validators=[DataRequired()])

    # Professional credentials
    license_number = StringField("Medical License Number", validators=[
        DataRequired(), Length(min=5, max=100)
    ])
    years_experience = IntegerField("Years of Experience", validators=[
        DataRequired(), NumberRange(min=0, max=60, message="Years of experience must be between 0 and 60.")
    ])
    consultation_fee = DecimalField("Consultation Fee ($)", places=2, validators=[
        DataRequired(), NumberRange(min=0, max=10000, message="Fee must be between $0 and $10,000.")
    ])
    bio = TextAreaField("Professional Bio", validators=[Optional(), Length(max=1000)])

    # Contact (FV crosscut)
    phone = StringField("Phone Number", validators=[
        DataRequired(),
        Regexp(r'^\+?1?\d{10,15}$', message="Enter a valid phone number (10-15 digits).")
    ])

    # Clinic info (CS crosscut - clinic profile)
    clinic_name    = StringField("Clinic / Hospital Name", validators=[Optional(), Length(max=255)])
    clinic_address = StringField("Clinic Address",         validators=[Optional(), Length(max=255)])
    city           = StringField("City",  validators=[Optional(), Length(max=100)])
    state          = StringField("State", validators=[Optional(), Length(max=100)])
    zip_code       = StringField("ZIP Code", validators=[
        Optional(),
        Regexp(r'^\d{5}(-\d{4})?$', message="Enter a valid US ZIP code.")
    ])

    def validate_license_number(self, field):
        """FV: License number must be unique."""
        from src.backend.models.user import Doctor
        existing = Doctor.query.filter_by(license_number=field.data).first()
        if existing:
            raise ValidationError("This license number is already registered.")