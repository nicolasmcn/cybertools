from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)

    from app.models import User, Analysis, PasswordHistory

    with app.app_context():
        db.create_all()

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.password import password_bp
    from app.routes.analysis import analysis_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(password_bp)
    app.register_blueprint(analysis_bp)

    return app
