from flask import Blueprint, request, jsonify, session, render_template
from app.models import Analysis
from app import db
from app.services.analyze_domain import analyze as run_analysis
from datetime import datetime, timezone

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/analyze-page")
def analyze_page():
    return render_template("analyze_domain.html")


@analysis_bp.route("/analyze")
def analyze_domain_route():
    if "user_id" not in session:
        return jsonify({"error": "Non autorisé"}), 401

    domain = request.args.get("domain")

    if not domain:
        return jsonify({"error": "Domaine non fourni"}), 400

    try:
        result = run_analysis(domain)

        new_analysis = Analysis(
            domain=domain,
            result=str(result),
            date=datetime.now(timezone.utc),
            user_id=session["user_id"]
        )

        db.session.add(new_analysis)
        db.session.commit()

        return jsonify(result)

    except Exception as e:
        print("ERREUR ANALYSE :", e)
        return jsonify({"error": "Erreur serveur lors de l'analyse"}), 500
