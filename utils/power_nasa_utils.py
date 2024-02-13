import pandas as pd
import requests
from tqdm import tqdm
from datetime import date
from utils.gfed_utils import coordinates_selecter

def get_point_weather(latitude:float, longitude:float, start_date:str, end_date:str):
    """
    Fetch meteorological data for a specific geoggraphical point in a time range.
    
    Parameters
    ----------
    latitude : float
        latitude of the geographical point.
    longitude : float
        longitude of the geographical point.
    start_date: str
        start date of the time range in format %Y%M%D.
    end_date: str
        end date of the time range in format %Y%M%D.
    """
    payload = {
        'time-standard': 'UTC',
        'latitude': latitude,
        'longitude': longitude,
        'start': start_date,
        'end': end_date,
        'community': 'AG',
        'parameters': 'T2M,WS10M,RH2M,PRECIPITATIONCAL',
        'format': 'JSON'
    }
    r = requests.get('https://power.larc.nasa.gov/api/temporal/daily/point', params=payload)
    data = r.json()
    return data
    
def fill_point_in_dict(point:dict, meteo_data:dict):
    """
    Fill the meteo_data dict with meteorological data from a fetched geographical point.
    
    Parameters
    ----------
    point : dict
        meteorological data of a specific geographical point.
    meteo_data : dict
        dict to fill with the point data.
    """
    res = point['properties']['parameter']
    
    # append the time 
    for elem in list(res['T2M'].keys()):
        meteo_data['date'].append(elem)

    for j in range (len(res['T2M'])):
        meteo_data['longitude'].append(point['geometry']['coordinates'][0])
        meteo_data['latitude'].append(point['geometry']['coordinates'][1])
        meteo_data['temperature'].append(res['T2M'][meteo_data['date'][j]])
        meteo_data['precipitation'].append(res['PRECIPITATIONCAL'][meteo_data['date'][j]])
        meteo_data['wind_speed'].append(res['WS10M'][meteo_data['date'][j]])
        meteo_data['air_humidity'].append(res['RH2M'][meteo_data['date'][j]])

def get_data(start_date:date, end_date:date, lat_min:float, lat_max:float, lng_min:float, lng_max:float, show_progress=False)->pd.DataFrame:
    """
    This function returns the dataSet of the needed meteorogical data within a specific geographical span and between a start date and end date 

    Parameters:
    -----------
    start_date: date
        start date of the time range.
    end_date: date
        end date of the time range.
    lat_min: float
        minimum latitude of the geographical range.
    lat_max: float
        maximum latitude of the geographical range.
    lng_min: float
        minimum longitude of the geographical range.
    lng_max: float
        maximum longitude of the geographical range.
    show_progress: bool
        if set to True shows a progress bar. Default is False.
    """

    # Transform the dates into the required format
    start_date = f"{start_date.year}{start_date.month}{start_date.day}"
    end_date = f"{end_date.year}{end_date.month}{end_date.day}"    
        
    meteo_data = {
        'date': [],
        'latitude': [],
        'longitude': [],
        'temperature': [],
        'precipitation': [],
        'air_humidity': [],
        'wind_speed': []
    }

    coordinates_array = coordinates_selecter(lat_min=lat_min, lat_max=lat_max, lng_max=lng_max, lng_min=lng_min)

    # Create a range for the loop
    rng = range(len(coordinates_array))
    if show_progress:
        rng = tqdm(range(len(coordinates_array)), desc='Fetching Meteo Data')

    for i in rng:
        data = get_point_weather(coordinates_array[i][0], coordinates_array[i][1], start_date, end_date)
        fill_point_in_dict(data, meteo_data)

    df = pd.DataFrame(meteo_data)

    return df