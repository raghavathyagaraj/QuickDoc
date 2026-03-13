import os


class TestingConfig:
    TESTING = True
    DEBUG = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/quickdoc_test"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False   # disable CSRF in tests
    MAIL_SUPPRESS_SEND = True