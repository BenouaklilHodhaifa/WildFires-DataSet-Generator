from flask import Blueprint, render_template, jsonify
import app.services.datasets.controllers as datasets_controllers
import json

bp = Blueprint("main", __name__)

# Main route for web page home
@bp.get("/")
def home_route():
    limits, status = datasets_controllers.limits()
    limits = json.loads(limits.data)
    if status == 200:
        return render_template('base.html', limits=limits)
    else:
        return jsonify({
            "message": "Server Error",
            "error": "Couldn't get map limits"
        }), 500