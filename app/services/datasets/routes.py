from flask import Blueprint
from app.services.datasets.controllers import *

bp = Blueprint("datasets", __name__)

# User route for getting requested data
@bp.get("/query")
def query_route():
    return query()

# User route for getting more infos about a data query
@bp.get("/query/info")
def query_info_route():
    return query_info()

# User route for getting limits of data
@bp.get("/limits")
def limits_route():
    return limits()