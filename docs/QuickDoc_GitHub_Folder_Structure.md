# QuickDoc - GitHub Repository Structure

## Team 4 | CS691 Capstone Project | Pace University

---

## 📁 Repository Folder Structure

```
QuickDoc/
│
├── 📄 README.md                     # Project overview, setup instructions
├── 📄 .gitignore                    # Files to ignore (venv, __pycache__, etc.)
├── 📄 requirements.txt              # Python dependencies
├── 📄 LICENSE                       # License file
│
├── 📁 docs/                         # Project Documentation
│   ├── 📁 business-case/
│   │   └── Business_Case_QuickDoc.docx
│   ├── 📁 requirements/
│   │   ├── List_of_Customer_Needs.docx
│   │   ├── List_of_Internal_User_Needs.docx
│   │   └── Business_Requirements.xlsx
│   ├── 📁 diagrams/
│   │   ├── BRM_SIPOC_Diagram.pptx
│   │   └── wireframes/
│   ├── 📁 meeting-notes/
│   └── 📁 presentations/
│
├── 📁 src/                          # Source Code
│   ├── 📁 backend/                  # Python Backend (Flask/Django)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 app.py                # Main application entry point
│   │   ├── 📄 config.py             # Configuration settings
│   │   ├── 📁 models/               # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── appointment.py
│   │   │   └── clinic.py
│   │   ├── 📁 routes/               # API routes/endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── appointments.py
│   │   │   ├── doctors.py
│   │   │   └── patients.py
│   │   ├── 📁 services/             # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── appointment_service.py
│   │   │   └── notification_service.py
│   │   └── 📁 utils/                # Utility functions
│   │       ├── __init__.py
│   │       └── helpers.py
│   │
│   └── 📁 frontend/                 # Frontend (HTML/CSS/JS)
│       ├── 📁 templates/            # HTML templates
│       │   ├── base.html
│       │   ├── index.html
│       │   ├── login.html
│       │   ├── register.html
│       │   ├── dashboard/
│       │   │   ├── patient_dashboard.html
│       │   │   ├── doctor_dashboard.html
│       │   │   └── admin_dashboard.html
│       │   ├── appointments/
│       │   │   ├── book_appointment.html
│       │   │   ├── appointment_list.html
│       │   │   └── appointment_details.html
│       │   └── doctors/
│       │       ├── doctor_list.html
│       │       └── doctor_profile.html
│       │
│       ├── 📁 static/               # Static files
│       │   ├── 📁 css/
│       │   │   ├── style.css
│       │   │   └── responsive.css
│       │   ├── 📁 js/
│       │   │   ├── main.js
│       │   │   ├── appointments.js
│       │   │   └── validation.js
│       │   └── 📁 images/
│       │       └── logo.png
│       │
│       └── 📁 components/           # Reusable UI components
│
├── 📁 database/                     # Database related files
│   ├── 📁 migrations/               # Database migrations
│   ├── 📁 seeds/                    # Sample/test data
│   └── 📄 schema.sql                # Database schema
│
├── 📁 tests/                        # Test files
│   ├── 📄 __init__.py
│   ├── 📁 unit/                     # Unit tests
│   │   ├── test_auth.py
│   │   ├── test_appointments.py
│   │   └── test_doctors.py
│   ├── 📁 integration/              # Integration tests
│   └── 📁 fixtures/                 # Test data
│
└── 📁 config/                       # Configuration files
    ├── 📄 development.py
    ├── 📄 production.py
    └── 📄 testing.py
```

---

## 📋 Folder Descriptions

| Folder | Purpose |
|--------|---------|
| `docs/` | All project documentation (Business Case, Requirements, Diagrams, Meeting Notes) |
| `src/backend/` | Python Flask/Django backend code |
| `src/frontend/` | HTML templates, CSS, JavaScript files |
| `database/` | Database schema, migrations, and seed data |
| `tests/` | Unit and integration tests |
| `config/` | Environment-specific configuration files |

---

## 📝 Key Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, setup instructions, team info |
| `.gitignore` | Specifies files Git should ignore |
| `requirements.txt` | Python package dependencies |
| `app.py` | Main application entry point |
| `config.py` | Application configuration |

---

## 🔀 Branch Strategy (Recommended)

```
main (production-ready code)
  │
  └── develop (integration branch)
        │
        ├── feature/homepage
        ├── feature/user-auth
        ├── feature/appointment-booking
        ├── feature/doctor-search
        └── bugfix/login-issue
```

---

## 👥 Team 4 Members

| Name | Role |
|------|------|
| | |
| | |
| | |
| | |

---

**Created:** February 2025  
**Course:** CS691 Capstone Project  
**University:** Pace University
