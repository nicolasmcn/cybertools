import ast
from flask import (
    Blueprint, render_template, redirect,
    url_for, request, session, jsonify, flash
)
from app.utils.security import login_required
from app.models import Analysis, PasswordHistory, User
from app import db
from werkzeug.security import check_password_hash

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]

    analysis_page = int(request.args.get("apage", 1))
    password_page = int(request.args.get("ppage", 1))

    analysis_limit = int(request.args.get("alimit", 5))
    password_limit = int(request.args.get("plimit", 5))

    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.date.desc()).paginate(
        page=analysis_page, per_page=analysis_limit, error_out=False
    )
    passwords = PasswordHistory.query.filter_by(user_id=user_id).order_by(PasswordHistory.date.desc()).paginate(
        page=password_page, per_page=password_limit, error_out=False
    )

    for a in analyses.items:
        try:
            a.result_dict = ast.literal_eval(a.result)
        except Exception:
            a.result_dict = {"score": "?", "score_max": "?", "risk_level": "Inconnu"}

    return render_template(
        "dashboard.html",
        analyses=analyses,
        passwords=passwords,
        analysis_limit=analysis_limit,
        password_limit=password_limit,
    )


# ✅ ROUTE DE VALIDATION DU MOT DE PASSE (NOUVELLE)
@dashboard_bp.route("/re-auth", methods=["POST"])
@login_required
def reauth():
    data = request.get_json()
    password = data.get("password", "")

    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"valid": False}), 401

    if check_password_hash(user.password, password):
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})


@dashboard_bp.route("/delete-password/<int:password_id>", methods=["DELETE"])
@login_required
def delete_password(password_id):
    pw = PasswordHistory.query.filter_by(id=password_id, user_id=session["user_id"]).first()

    if not pw:
        return jsonify({"error": "Mot de passe introuvable."}), 404

    db.session.delete(pw)
    db.session.commit()
    return jsonify({"success": True}), 200


@dashboard_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    user_id = session["user_id"]

    PasswordHistory.query.filter_by(user_id=user_id).delete()
    Analysis.query.filter_by(user_id=user_id).delete()
    User.query.filter_by(id=user_id).delete()

    db.session.commit()
    session.clear()
    flash("Votre compte et vos données ont été supprimés.")
    return redirect(url_for("main.index"))
