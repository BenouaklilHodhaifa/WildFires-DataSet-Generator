from flask import Blueprint
from app.services.datasets.controllers import *

bp = Blueprint("announcements", __name__)

@bp.get("/")
def index_route():
    return index()