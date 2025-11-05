import re
from functools import wraps
from flask import session, redirect, url_for, flash


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
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapped_function