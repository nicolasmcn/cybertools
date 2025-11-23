from flask import Blueprint, render_template, session, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/check-auth")
def check_auth():
    return jsonify({"authenticated": "user_id" in session})
