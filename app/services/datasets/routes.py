from flask import Blueprint
from app.services.datasets.controllers import *

bp = Blueprint("datasets", __name__)

# Admin route for populating the data from sources
@bp.get("/populate")
def populate_route():
    return populate()

# User route for getting requested data
@bp.get("/query")
def query_route():
    return query()

# User route for getting limits of data
@bp.get("/limits")
def limits_route():
    return limits()