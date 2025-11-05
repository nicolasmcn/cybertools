from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app.utils.security import login_required
from app.models import Analysis
from app import db
from app.services.analyze_domain import analyze
from datetime import datetime, timezone

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/analyze-page")
@login_required
def analyze_page():
    return render_template("analyze_domain.html")

@analysis_bp.route("/analyze", methods=["GET"])
def analyze_domain():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    domain = request.args.get("domain")
    if not domain:
        return jsonify({"error": "Domain not provided"}), 400

    result = analyze(domain)

    new_analysis = Analysis(
        domain=domain,
        result=str(result),
        date=datetime.now(timezone.utc),
        user_id=session["user_id"],
    )
    db.session.add(new_analysis)
    db.session.commit()

    return jsonify(result)