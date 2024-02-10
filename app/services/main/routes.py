from flask import Blueprint, render_template

bp = Blueprint("main", __name__)

# Main route for web page home
@bp.get("/")
def home_route():
    return render_template('base.html')