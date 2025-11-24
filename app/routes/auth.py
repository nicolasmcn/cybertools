from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db, bcrypt
from app.models import User
from app.utils.security import is_strong_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard.dashboard'))

    next_page = request.args.get('next')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['email'] = user.email
            flash("Connexion réussie ✅", "success")
            return redirect(next_page or url_for('dashboard.dashboard'))
        else:
            flash("Identifiants incorrects", "error")

    return render_template('login.html')


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Cet email existe déjà.", "error")
            return redirect(url_for("auth.register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id
        session["email"] = new_user.email

        flash("Compte créé avec succès ✅", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("register.html")


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("main.index"))
