from flask import request
from datetime import date
from app import db
from flask import jsonify, make_response
from sqlalchemy import text
import pandas as pd

def query():
    """User route controller for getting requested data"""
    try:
        lat_min = float(request.args['lat_min'])
        lat_max = float(request.args['lat_max'])
        lng_min = float(request.args['lng_min'])
        lng_max = float(request.args['lng_max'])
        start_date = date.fromisoformat(request.args['start_date'])
        end_date = date.fromisoformat(request.args['end_date'])

        connection = db.engine.connect() # Connect to database
        print((
            "SELECT * FROM wildfires_data "
            f"WHERE (latitude BETWEEN {lat_min} AND {lat_max}) "
            f"AND (longitude BETWEEN {lng_min} AND {lng_max}) "
            f"AND (date BETWEEN {start_date.year}-{str(start_date.month).zfill(2)}-{str(start_date.day).zfill(2)} "
            f"AND {end_date.year}-{str(end_date.month).zfill(2)}-{str(end_date.day).zfill(2)})"
        ))
        df = pd.read_sql(text((
            "SELECT * FROM wildfires_data "
            f"WHERE (latitude BETWEEN {lat_min} AND {lat_max}) "
            f"AND (longitude BETWEEN {lng_min} AND {lng_max}) "
            f"AND (date BETWEEN '{start_date.year}-{str(start_date.month).zfill(2)}-{str(start_date.day).zfill(2)}' "
            f"AND '{end_date.year}-{str(end_date.month).zfill(2)}-{str(end_date.day).zfill(2)}')"
        )), connection) # Query data

        # Serve data read as a csv file
        resp = make_response(df.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=data.csv"
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
        cursor = connection.execute(text("SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude), MIN(date), MAX(date) from wildfires_data"))
        res = {}
        for r in cursor:
            res = {
            "lat_min": r[0],
            "lat_max": r[1],
            "lng_min": r[2],
            "lng_max": r[3],
            "date_min": r[4],
            "date_max": r[5]
        }
        
        return jsonify(res), 200
    except Exception as e:
        return jsonify({
            "message": "Server Error",
            "error": str(e)
        }), 500