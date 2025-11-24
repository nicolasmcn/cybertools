from flask import Blueprint, request, jsonify, session, render_template
from app.models import PasswordHistory
from app import db
from app.utils.security import login_required

password_bp = Blueprint("password", __name__)

@password_bp.route("/password-generator")
def password_page():
    return render_template("password.html")


@password_bp.route("/save-password", methods=["POST"])
@login_required
def save_password():
    try:
        data = request.get_json(force=True)

        password = data.get("password")
        strength = data.get("strength", "Auto")
        user_id = session.get("user_id")

        if not password:
            return jsonify({"success": False, "error": "Mot de passe vide"}), 400

        new_pw = PasswordHistory(
            password=password,
            strength=strength,
            user_id=user_id
        )

        db.session.add(new_pw)
        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        print("ERREUR SAVE PASSWORD:", e)
        return jsonify({"success": False, "error": "Erreur serveur"}), 500
