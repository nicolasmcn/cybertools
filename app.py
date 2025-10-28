import ast
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
from config import Config  
import base64, os
import re

from analyze_domain import analyze
from functools import wraps
from dotenv import load_dotenv
load_dotenv()

def is_strong_password(password):
    return (
        len(password) >= 8 and
        len(re.findall(r'\d', password)) >= 2 and
        re.search(r'[^A-Za-z0-9]', password)
    )

def login_required(f):
    @wraps(f)
    def wrapped_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Connectez-vous pour accéder à cette page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped_function

# === CONFIGURATION ===
app = Flask(__name__)
CORS(app)

app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# === MODELES ===
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

# === INITIALISATION DE LA BASE ===

with app.app_context():
    try:
        db.create_all()
        with db.engine.begin() as conn:
            # --- user ---
            try:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN kdf_salt_b64 VARCHAR(64)'))
            except Exception:
                pass
            try:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN kdf_iter INTEGER DEFAULT 200000'))
            except Exception:
                pass

            # --- password_history (ajoute si manquant) ---
            cols = {row[1] for row in conn.execute(text('PRAGMA table_info(password_history)'))}
            if "ciphertext_b64" not in cols:
                conn.execute(text('ALTER TABLE password_history ADD COLUMN ciphertext_b64 TEXT'))
            if "iv_b64" not in cols:
                conn.execute(text('ALTER TABLE password_history ADD COLUMN iv_b64 VARCHAR(64)'))
            if "alg" not in cols:
                conn.execute(text("ALTER TABLE password_history ADD COLUMN alg VARCHAR(64) DEFAULT 'AES-GCM-256/PBKDF2-SHA256'"))

        print("Base de données connectée et prête.")
    except Exception as e:
        print(f"Erreur de base de données : {e}")

# === ROUTES ===

@app.route('/analyze', methods=['GET'])
def analyze_domain():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Domain not provided"}), 400

    result = analyze(domain)

    new_analysis = Analysis(
        domain=domain,
        result=str(result),
        user_id=session['user_id']
    )
    db.session.add(new_analysis)
    db.session.commit()

    return jsonify(result)

@app.route('/save-password', methods=['POST'])
def save_password():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    password = data.get('password')
    strength = data.get('strength', 'Non précisé')

    if not password:
        return jsonify({"error": "Mot de passe manquant."}), 400

    entry = PasswordHistory(password=password, strength=strength, user_id=session['user_id'])
    db.session.add(entry)
    db.session.commit()

    return jsonify({"success": True})

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    next_page = request.args.get('next')

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.permanent = True
            session['user_id'] = user.id

            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
            return redirect(url_for('login', next=next_page))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not is_strong_password(password):
            flash("Le mot de passe doit contenir au moins 8 caractères, \
             2 chiffres et un caractère spécial.", "error")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_pw)

        salt = os.urandom(16)
        new_user.kdf_salt_b64 = base64.b64encode(salt).decode()


        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Compte créé avec succès. Connectez-vous maintenant.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la création du compte.', 'error')
            print(f"Erreur SQL: {e}")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/index')
def index():
    return render_template('index.html')

import ast

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Pagination parameters
    analysis_page = int(request.args.get('apage', 1))
    password_page = int(request.args.get('ppage', 1))
    
    analysis_limit = int(request.args.get('alimit', 5))
    password_limit = int(request.args.get('plimit', 5))

    # Paginated queries
    analysis_query = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.date.desc())
    password_query = PasswordHistory.query.filter_by(user_id=user_id).order_by(PasswordHistory.date.desc())

    analyses = analysis_query.paginate(page=analysis_page, per_page=analysis_limit, error_out=False)
    passwords = password_query.paginate(page=password_page, per_page=password_limit, error_out=False)

    for a in analyses.items:
        try:
            a.result_dict = ast.literal_eval(a.result)
        except:
            a.result_dict = {"score": "?", "score_max": "?", "risk_level": "Inconnu"}

    return render_template(
        'dashboard.html',
        analyses=analyses,
        passwords=passwords,
        analysis_limit=analysis_limit,
        password_limit=password_limit
    )

@app.route('/delete-password/<int:password_id>', methods=['DELETE'])
def delete_password(password_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    pw = PasswordHistory.query.filter_by(id=password_id, user_id=session['user_id']).first()
    if not pw:
        return jsonify({"error": "Mot de passe introuvable."}), 404

    db.session.delete(pw)
    db.session.commit()
    print(f"[DEBUG] Suppression du mot de passe ID={password_id} pour l'utilisateur ID={session['user_id']}")
    return jsonify({"success": True}), 200

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('login'))

@app.route('/analyze-page')
def analyze_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('analyze_domain.html')

@app.route('/password')
def password():
    return render_template('password.html')

@app.before_request
def log_session():
    print("SESSION:", dict(session))

@app.route('/check-auth')
def check_auth():
    return jsonify({'authenticated': 'user_id' in session})

@app.route('/delete-account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        flash("Vous devez être connecté pour supprimer votre compte.")
        return redirect(url_for('login'))

    user_id = session['user_id']

    PasswordHistory.query.filter_by(user_id=user_id).delete()
    Analysis.query.filter_by(user_id=user_id).delete()
    User.query.filter_by(id=user_id).delete()

    db.session.commit()
    session.clear()
    flash("Votre compte et vos données ont été supprimés conformément au RGPD.")
    return redirect(url_for('home'))

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.get("/me-kdf")
def me_kdf():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    import base64, os
    user = User.query.get(session['user_id'])

    if not user.kdf_salt_b64:
        salt = os.urandom(16)
        user.kdf_salt_b64 = base64.b64encode(salt).decode()
        if not user.kdf_iter:
            user.kdf_iter = 200_000
        db.session.commit()

    return jsonify({
        "kdf_salt_b64": user.kdf_salt_b64,
        "kdf_iter": user.kdf_iter
    })

@app.post("/re-auth")
def re_auth():
    if 'user_id' not in session:
        return jsonify({"valid": False}), 401

    data = request.get_json(force=True)
    pwd = (data.get("password") or "").strip()

    user = User.query.get(session['user_id'])
    if user and bcrypt.check_password_hash(user.password, pwd):
        return jsonify({"valid": True})

    return jsonify({"valid": False})
if __name__ == '__main__':
    app.run(debug=True, port=5000)
