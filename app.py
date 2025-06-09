from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
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

# === MODELE UTILISATEUR ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def check_password(self, password_input):
        return bcrypt.check_password_hash(self.password, password_input)

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
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Domain not provided"}), 400
    result = analyze(domain)
    return jsonify(result)

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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

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
