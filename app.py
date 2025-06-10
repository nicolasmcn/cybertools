import ast
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import os

from analyze_domain import analyze
from functools import wraps


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

app.config['SECRET_KEY'] = '5fdd0250fe2820b9724a16995bf576e0ba9814410cb176f41a2994b5359af1fe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:flask123@localhost/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # en sec

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# === MODELES ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    passwords = db.relationship('PasswordHistory', backref='user', lazy=True)

    def check_password(self, password_input):
        return bcrypt.check_password_hash(self.password, password_input)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    result = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class PasswordHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    strength = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# === INITIALISATION DE LA BASE ===
with app.app_context():
    try:
        db.create_all()
        print("✅ Base de données connectée et prête.")
    except Exception as e:
        print(f"❌ Erreur de base de données : {e}")

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

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_pw)

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
    return jsonify({"success": True}), 200
    print(f"[DEBUG] Suppression du mot de passe ID={password_id} pour l'utilisateur ID={session['user_id']}")

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
