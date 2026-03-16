import os


class ProductionConfig:
    DEBUG = False

    SECRET_KEY = os.getenv("SECRET_KEY")          # must be set in prod
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # must be set in prod

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    WTF_CSRF_ENABLED = True