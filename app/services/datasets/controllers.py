from flask import request
from datetime import datetime as dt
from .utils.gfed_utils import get_gfed_data_for_range
import pandas as pd

def populate():
    """Admin route controller for populating the data from sources"""
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
    open_meteo_df:pd.DataFrame = None


def query():
    """User route controller for getting requested data"""
    pass

def limits():
    """User route controller for getting limits of data"""
    pass