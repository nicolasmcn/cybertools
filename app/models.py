from datetime import datetime, timezone
from app import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    kdf_salt_b64 = db.Column(db.String(64), nullable=True)
    kdf_iter = db.Column(db.Integer, default=200_000)
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    passwords = db.relationship('PasswordHistory', backref='user', lazy=True)

    def check_password(self, password_input):
        return bcrypt.check_password_hash(self.password, password_input)


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    result = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class PasswordHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    ciphertext_b64 = db.Column(db.Text, nullable=True)
    iv_b64 = db.Column(db.String(64), nullable=True)
    alg = db.Column(db.String(64), default="AES-GCM-256/PBKDF2-SHA256")
    strength = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)