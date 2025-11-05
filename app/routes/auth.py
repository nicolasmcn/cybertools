from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db, bcrypt
from app.models import User
from app.utils.security import is_strong_password
import os, base64
from flask_bcrypt import Bcrypt
from app.db import get_db   

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    next_page = request.args.get('next')

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.permanent = True
            session['user_id'] = user.id
            return redirect(next_page or url_for('dashboard.dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
            return redirect(url_for('auth.login', next=next_page))

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not is_strong_password(password):
            flash("Le mot de passe doit contenir au moins 8 caractères, 2 chiffres et un caractère spécial.", "error")
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('auth.register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_pw)

        salt = os.urandom(16)
        new_user.kdf_salt_b64 = base64.b64encode(salt).decode()

        db.session.add(new_user)
        db.session.commit()
        flash('Compte créé avec succès. Connectez-vous maintenant.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('auth.login'))