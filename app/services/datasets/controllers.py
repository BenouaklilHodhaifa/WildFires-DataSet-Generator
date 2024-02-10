from flask import request
from datetime import datetime as dt
from .utils.gfed_utils import get_gfed_data_for_range
from .utils.open_meteo_utils import get_data as get_open_meteo_data
from app import db
from flask import jsonify
from sqlalchemy import text
import pandas as pd

def populate():
    """Admin route controller for populating the data from sources"""
    try:
        start_date = dt.fromisoformat(request.args.get("start_date"))
        end_date = dt.fromisoformat(request.args.get("start_date"))
        lng_min = request.args.get("lng_min")
        lng_max = request.args.get("lng_max")
        lat_min = request.args.get("lat_min")
        lat_max = request.args.get("lng_max")

        # Get GFED Data
        geo_pos_df, time_df, gfed_df = get_gfed_data_for_range(start_date, end_date, lat_min, lat_max,
                                                            lng_min, lng_max)

        # Get OpenMeteo Data
        open_meteo_df = get_open_meteo_data(lat_min, lat_max, lng_min, lng_max, start_date, end_date)

        with db.engine.connect() as connection:
            connection.execute(text(f"INSERT INTO positions VALUES {",".join([f"({",".join(map(str, r))})" for r in geo_pos_df.values])}"))
            connection.execute(text(f"INSERT INTO dates VALUES {",".join([f"({",".join(map(str, r))})" for r in time_df.values])}"))
            connection.execute(text(f"INSERT INTO gfed_data VALUES {",".join([f"({",".join(map(str, r))})" for r in gfed_df.values])}"))
            connection.execute(text(f"INSERT INTO meteo VALUES {",".join([f"({",".join(map(str, r))})" for r in open_meteo_df.values])}"))

        return jsonify({
            "message": "Database populated successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "message": "Server Error",
            "error": str(e)
        }), 500


def query():
    """User route controller for getting requested data"""
    try:
        connection = db.engine.connect()
        df = pd.read_sql("SELECT * FROM gfed_data", connection)
        pd.read_hdf()

    except Exception as e:
        return jsonify({
            "message": "Server Error",
            "error": str(e)
        }), 500

def limits():
    """User route controller for getting limits of data"""
    pass