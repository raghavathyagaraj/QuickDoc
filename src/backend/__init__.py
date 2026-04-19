from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import logging
import os

db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
mail = Mail()
csrf = CSRFProtect()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "../frontend/templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "../frontend/static")
    )
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Load config directly from environment — no config package needed
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/quickdoc"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@quickdoc.com")
    app.config["DEBUG"] = os.getenv("FLASK_ENV") == "development"

    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    from src.backend.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from src.backend.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    from src.backend.routes.profile import profile_bp
    app.register_blueprint(profile_bp, url_prefix="/profile")
    from src.backend.routes.search import search_bp
    app.register_blueprint(search_bp, url_prefix="/search")
    from src.backend.routes.social import social_bp
    app.register_blueprint(social_bp, url_prefix="/social")
    from src.backend.routes.home import home_bp
    app.register_blueprint(home_bp)
    
    from src.backend.routes.provider import provider_bp
    app.register_blueprint(provider_bp, url_prefix="/provider")
    
    return app