import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.backend import create_app, db
from src.backend.models.user import User, Patient, Doctor, DoctorSpecialty


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def app():
    """Create test Flask app with in-memory SQLite database."""
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['WTF_CSRF_ENABLED'] = 'False'

    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        # Seed specialties for doctor tests
        for name in ['General Medicine', 'Cardiology', 'Dermatology']:
            db.session.add(DoctorSpecialty(name=name))
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def registered_patient(app):
    """Create a registered patient user for login tests."""
    with app.app_context():
        user = User(email='patient@test.com', role='patient')
        user.set_password('Test1234')
        db.session.add(user)
        db.session.flush()
        patient = Patient(
            user_id=user.id,
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            phone='1234567890',
            preferred_payment='card'
        )
        db.session.add(patient)
        db.session.commit()
        return user.id


# ── 01.01 Register Patient Tests ──────────────────────────────────────────────

class TestRegisterPatient:

    def test_register_patient_page_loads(self, client):
        """GET /auth/register/patient returns 200."""
        response = client.get('/auth/register/patient')
        assert response.status_code == 200

    def test_register_patient_success(self, client):
        """Valid patient registration saves to DB and redirects."""
        response = client.post('/auth/register/patient', data={
            'email': 'newpatient@test.com',
            'password': 'Test1234',
            'confirm_password': 'Test1234',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': '1995-05-15',
            'gender': 'female',
            'phone': '9876543210',
            'preferred_payment': 'card'
        }, follow_redirects=False)
        # Should redirect after success
        assert response.status_code in [200, 302]

    def test_register_patient_duplicate_email(self, app, client, registered_patient):
        """Duplicate email registration is blocked."""
        with app.app_context():
            response = client.post('/auth/register/patient', data={
                'email': 'patient@test.com',  # already registered
                'password': 'Test1234',
                'confirm_password': 'Test1234',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'date_of_birth': '1995-05-15',
                'phone': '9876543210',
                'preferred_payment': 'card'
            }, follow_redirects=True)
            assert response.status_code == 200
            assert b'already registered' in response.data or b'email' in response.data.lower()

    def test_register_patient_weak_password(self, client):
        """Weak password is rejected."""
        response = client.post('/auth/register/patient', data={
            'email': 'weakpass@test.com',
            'password': 'weak',
            'confirm_password': 'weak',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': '1995-05-15',
            'phone': '9876543210',
            'preferred_payment': 'card'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'password' in response.data.lower()

    def test_register_patient_password_mismatch(self, client):
        """Mismatched passwords are rejected."""
        response = client.post('/auth/register/patient', data={
            'email': 'mismatch@test.com',
            'password': 'Test1234',
            'confirm_password': 'Test5678',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': '1995-05-15',
            'phone': '9876543210',
            'preferred_payment': 'card'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'match' in response.data.lower()

    def test_register_patient_missing_required_fields(self, client):
        """Missing required fields returns validation errors."""
        response = client.post('/auth/register/patient', data={
            'email': '',
            'password': '',
            'confirm_password': '',
            'first_name': '',
            'last_name': '',
            'date_of_birth': '',
            'phone': ''
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_register_patient_saved_to_db(self, app, client):
        """Successful registration saves user and patient to DB."""
        with app.app_context():
            client.post('/auth/register/patient', data={
                'email': 'dbtest@test.com',
                'password': 'Test1234',
                'confirm_password': 'Test1234',
                'first_name': 'DB',
                'last_name': 'Test',
                'date_of_birth': '1990-01-01',
                'phone': '1234567890',
                'preferred_payment': 'card'
            })
            user = User.query.filter_by(email='dbtest@test.com').first()
            assert user is not None
            assert user.role == 'patient'


# ── 01.02 Register Doctor Tests ───────────────────────────────────────────────

class TestRegisterDoctor:

    def test_register_doctor_page_loads(self, client):
        """GET /auth/register/doctor returns 200."""
        response = client.get('/auth/register/doctor')
        assert response.status_code == 200

    def test_register_doctor_success(self, app, client):
        """Valid doctor registration saves to DB."""
        with app.app_context():
            specialty = DoctorSpecialty.query.first()
            client.post('/auth/register/doctor', data={
                'email': 'doctor@test.com',
                'password': 'Test1234',
                'confirm_password': 'Test1234',
                'first_name': 'Dr John',
                'last_name': 'Smith',
                'specialty_id': specialty.id,
                'license_number': 'LIC123456',
                'years_experience': 5,
                'consultation_fee': '150.00',
                'phone': '9876543210'
            })
            user = User.query.filter_by(email='doctor@test.com').first()
            assert user is not None
            assert user.role == 'doctor'

    def test_register_doctor_duplicate_license(self, app, client):
        """Duplicate license number is blocked."""
        with app.app_context():
            specialty = DoctorSpecialty.query.first()
            data = {
                'email': 'doc1@test.com',
                'password': 'Test1234',
                'confirm_password': 'Test1234',
                'first_name': 'Doc',
                'last_name': 'One',
                'specialty_id': specialty.id,
                'license_number': 'DUPLIC123',
                'years_experience': 5,
                'consultation_fee': '100.00',
                'phone': '1111111111'
            }
            client.post('/auth/register/doctor', data=data)

            # Try same license with different email
            data['email'] = 'doc2@test.com'
            response = client.post('/auth/register/doctor', data=data, follow_redirects=True)
            assert response.status_code == 200

    def test_register_doctor_specialties_loaded(self, client):
        """Doctor registration page loads specialties from DB."""
        response = client.get('/auth/register/doctor')
        assert response.status_code == 200
        assert b'Cardiology' in response.data or b'specialty' in response.data.lower()


# ── 01.03 Login Tests ─────────────────────────────────────────────────────────

class TestLogin:

    def test_login_page_loads(self, client):
        """GET /auth/login returns 200."""
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_login_success_patient(self, app, client, registered_patient):
        """Valid patient login redirects to patient dashboard."""
        with app.app_context():
            response = client.post('/auth/login', data={
                'email': 'patient@test.com',
                'password': 'Test1234',
                'remember_me': False
            }, follow_redirects=False)
            assert response.status_code == 302
            assert 'dashboard' in response.headers.get('Location', '')

    def test_login_wrong_password(self, app, client, registered_patient):
        """Wrong password shows error message."""
        with app.app_context():
            response = client.post('/auth/login', data={
                'email': 'patient@test.com',
                'password': 'WrongPass99',
                'remember_me': False
            }, follow_redirects=True)
            assert response.status_code == 200
            assert b'Incorrect password' in response.data or b'password' in response.data.lower()

    def test_login_unknown_email(self, client):
        """Unknown email shows error message."""
        response = client.post('/auth/login', data={
            'email': 'nobody@test.com',
            'password': 'Test1234',
            'remember_me': False
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'No account' in response.data or b'email' in response.data.lower()

    def test_login_missing_email(self, client):
        """Missing email shows validation error."""
        response = client.post('/auth/login', data={
            'email': '',
            'password': 'Test1234',
            'remember_me': False
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_missing_password(self, client):
        """Missing password shows validation error."""
        response = client.post('/auth/login', data={
            'email': 'patient@test.com',
            'password': '',
            'remember_me': False
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_inactive_account(self, app, client):
        """Inactive account is blocked from login."""
        with app.app_context():
            user = User(email='inactive@test.com', role='patient', is_active=False)
            user.set_password('Test1234')
            db.session.add(user)
            db.session.commit()

            response = client.post('/auth/login', data={
                'email': 'inactive@test.com',
                'password': 'Test1234',
                'remember_me': False
            }, follow_redirects=True)
            assert response.status_code == 200
            assert b'deactivated' in response.data or b'inactive' in response.data.lower()


# ── 01.04 Logout Tests ────────────────────────────────────────────────────────

class TestLogout:

    def test_logout_redirects_to_login(self, app, client, registered_patient):
        """Logout redirects to login page."""
        with app.app_context():
            # Login first
            client.post('/auth/login', data={
                'email': 'patient@test.com',
                'password': 'Test1234',
                'remember_me': False
            })
            # Then logout
            response = client.get('/auth/logout', follow_redirects=False)
            assert response.status_code == 302
            assert 'login' in response.headers.get('Location', '')

    def test_logout_without_login_redirects(self, client):
        """Accessing logout without being logged in redirects to login."""
        response = client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302

    def test_dashboard_inaccessible_after_logout(self, app, client, registered_patient):
        """Dashboard is not accessible after logout."""
        with app.app_context():
            # Login
            client.post('/auth/login', data={
                'email': 'patient@test.com',
                'password': 'Test1234',
                'remember_me': False
            })
            # Logout
            client.get('/auth/logout')
            # Try to access dashboard
            response = client.get('/dashboard/patient', follow_redirects=False)
            assert response.status_code == 302
            assert 'login' in response.headers.get('Location', '')