import os


class DevelopmentConfig:
    DEBUG = True

    # Reads from docker-compose environment block
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")

    # docker-compose sets: postgresql://postgres:postgres@db:5432/quickdoc
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/quickdoc"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail (optional in dev)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@quickdoc.com")

    WTF_CSRF_ENABLED = True