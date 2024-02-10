from flask import request
from datetime import date
from app import db
from flask import jsonify, make_response, current_app as app
from sqlalchemy import text
import pandas as pd

def populate():
    """Admin route controller for populating the data from sources"""
    try:
        start_date = date.fromisoformat(request.args.get("start_date"))
        end_date = date.fromisoformat(request.args.get("start_date"))
        lat_min = request.args.get("lat_min")
        lat_max = request.args.get("lng_max")
        lng_min = request.args.get("lng_min")
        lng_max = request.args.get("lng_max")

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
        connection = db.engine.connect() # Connect to database
        df = pd.read_sql("SELECT * FROM wildfires_data", connection) # Query data

        # Serve data read as a csv file
        resp = make_response(df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"

        return resp
    
    except Exception as e:
        return jsonify({
            "message": "Server Error",
            "error": str(e)
        }), 500

def limits():
    """User route controller for getting limits of data"""
    try:
        # Connect to database
        connection = db.engine.connect()
        # Get limits of data
        res = connection.execute("SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude), MIN(date), MAX(date) from wildfires_data")
        return jsonify({
            "lat_min": res[0],
            "lat_max": res[1],
            "lng_min": res[2],
            "lng_max": res[3],
            "date_min": res[4],
            "date_max": res[5]
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Server Error",
            "error": str(e)
        }), 500