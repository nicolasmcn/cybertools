import os
import base64
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from sqlalchemy import text
import pymysql
import os

from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()

def get_db():
    return pymysql.connect(
        host="localhost",
        user="flaskuser",
        password="flask123",
        database="users",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)

    from app import models

    with app.app_context():
        try:
            db.create_all()
            with db.engine.begin() as conn:
                try:
                    conn.execute(text("ALTER TABLE user ADD COLUMN kdf_salt_b64 VARCHAR(64)"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE user ADD COLUMN kdf_iter INTEGER DEFAULT 200000"))
                except Exception:
                    pass

                try:
                    conn.execute(text("ALTER TABLE password_history ADD COLUMN ciphertext_b64 TEXT"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE password_history ADD COLUMN iv_b64 VARCHAR(64)"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE password_history ADD COLUMN alg VARCHAR(64) DEFAULT 'AES-GCM-256/PBKDF2-SHA256'"))
                except Exception:
                    pass

            print("Base de données connectée et prête.")
        except Exception as e:
            print(f"Erreur de base de données : {e}")

    # ====== BLUEPRINTS ======
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.analysis import analysis_bp
    from app.routes.password import password_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(password_bp)

    @app.before_request
    def log_session():
        from flask import session
        print("SESSION:", dict(session))

    @app.get("/healthz")
    def healthz():
        return "ok", 200

    return app