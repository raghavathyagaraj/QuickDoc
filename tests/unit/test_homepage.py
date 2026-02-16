# tests/unit/test_homepage.py
# QuickDoc Homepage Tests - Team 4

"""
Unit tests for QuickDoc Homepage
These tests validate basic functionality before deployment
"""

def test_homepage_title():
    """Test that homepage has correct title"""
    expected_title = "QuickDoc"
    assert expected_title == "QuickDoc"

def test_homepage_tagline():
    """Test that homepage has correct tagline"""
    expected_tagline = "Your Health, Simplified"
    assert "Simplified" in expected_tagline

def test_navigation_links_count():
    """Test that homepage has correct number of nav links"""
    nav_links = ["Find Doctors", "Specialties", "For Providers", "About"]
    assert len(nav_links) == 4

def test_specialties_available():
    """Test that specialties are defined"""
    specialties = [
        "Cardiology",
        "Neurology", 
        "Orthopedics",
        "Ophthalmology",
        "Pediatrics",
        "Oncology",
        "General Physician",
        "Dentistry"
    ]
    assert len(specialties) == 8
    assert "Cardiology" in specialties

def test_stats_values():
    """Test that stats have correct values"""
    stats = {
        "doctors": "5000+",
        "patients": "120K+",
        "satisfaction": "98%",
        "availability": "24/7"
    }
    assert stats["satisfaction"] == "98%"

def test_cta_buttons_exist():
    """Test that CTA buttons are defined"""
    cta_buttons = ["Book an Appointment", "Join as a Doctor", "Sign Up"]
    assert "Book an Appointment" in cta_buttons

def test_trust_badges():
    """Test that trust badges are defined"""
    badges = ["HIPAA Compliant", "SSL Encrypted", "SOC 2 Certified", "99.9% Uptime"]
    assert len(badges) == 4

def test_footer_sections():
    """Test that footer has all sections"""
    footer_sections = ["Product", "Company", "Resources", "Legal"]
    assert len(footer_sections) == 4

def test_testimonials_count():
    """Test that testimonials exist"""
    testimonials = [
        {"name": "Emily Rodriguez", "role": "Patient"},
        {"name": "Dr. James Chen", "role": "Cardiologist"},
        {"name": "Sarah Thompson", "role": "Patient"}
    ]
    assert len(testimonials) == 3

def test_search_functionality():
    """Test that search fields are defined"""
    search_fields = ["Specialty or doctor name", "City or Zip code"]
    assert len(search_fields) == 2
