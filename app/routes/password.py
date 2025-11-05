import os, base64
from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    render_template,
)
from app.utils.security import login_required
from app.models import PasswordHistory, User
from app import db, bcrypt

password_bp = Blueprint("password", __name__)

@password_bp.route("/save-password", methods=["POST"])
@login_required
def save_password():
    data = request.get_json(force=True)
    password = data.get("password")
    strength = data.get("strength", "Non précisé")

    if not password:
        return jsonify({"error": "Mot de passe manquant."}), 400

    entry = PasswordHistory(
        password=password,
        strength=strength,
        user_id=session["user_id"],
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({"success": True})


@password_bp.route("/password")
@login_required
def password_page():
    # page avec le générateur (ton template existe déjà)
    return render_template("password.html")


@password_bp.route("/check-auth")
def check_auth():
    # utilisé par ton JS pour savoir s'il doit POST le mdp
    return jsonify({"authenticated": "user_id" in session})


@password_bp.route("/me-kdf")
@login_required
def me_kdf():
    # sert au chiffrement côté front
    user = User.query.get(session["user_id"])

    if not user.kdf_salt_b64:
        salt = os.urandom(16)
        user.kdf_salt_b64 = base64.b64encode(salt).decode()
        if not user.kdf_iter:
            user.kdf_iter = 200_000
        db.session.commit()

    return jsonify({
        "kdf_salt_b64": user.kdf_salt_b64,
        "kdf_iter": user.kdf_iter,
    })


@password_bp.route("/re-auth", methods=["POST"])
@login_required
def re_auth():
    data = request.get_json(force=True)
    pwd = (data.get("password") or "").strip()

    user = User.query.get(session["user_id"])
    if user and bcrypt.check_password_hash(user.password, pwd):
        return jsonify({"valid": True})

    return jsonify({"valid": False}), 401