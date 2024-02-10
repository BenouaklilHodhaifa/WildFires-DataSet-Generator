import numpy as np
import pandas as pd
import requests
from gfed_utils import coordinates_selecter

def get_data(lat_min:float, lat_max:float, lon_min:float, lon_max:float, start_date:str, end_date:str)->pd.DataFrame:
    """
    This function returns the dataSet of the needed meteorogical data within a specific geographical span and between a start date and end date 

    Parameters:
    -----------
    lat_min: float
        latitude min
    lat_max: float
        latitude max
    lon_min: float
        longitude min
    lon_max: float
        longitude max
    start_date: str
        start date in the format 'YYYY-MM-DD'
    end_date: str
        end date in the format 'YYYY-MM-DD'
    """
    #getting the coordinates
    coordinates = coordinates_selecter(lat_min, lat_max, lon_min, lon_max)
    #getting the data using open meteo api
    lat = ''
    long = ''

    for i in range(len(coordinates)):
        lat += str(coordinates[i][0]) + ','
        long += str(coordinates[i][1]) + ','
    
    payload = {
        'wind_speed_unit': 'ms',
        'latitude': lat,
        'longitude': long,
        'start_date': start_date, 
        'end_date': end_date,
        'daily': 'temperature_2m_max,precipitation_sum,wind_speed_10m_max'
    }

    r = requests.get('https://archive-api.open-meteo.com/v1/archive', params=payload)

    if r.status_code != 200:
        print(r.json())
        return None
    
    data = r.json()

    meteo_data = {
        'time': [],
        'latitude': [],
        'longitude': [],
        'T': [],
        'P': [],
        'H': [],
        'U': []
    }

    for i in range (len(data)):
        res = data[i]
        for j in range (len(res['daily']['time'])):
            meteo_data['time'].append(res['daily']['time'][j])
            meteo_data['latitude'].append(res['latitude'])
            meteo_data['longitude'].append(res['longitude'])
            meteo_data['T'].append(res['daily']['temperature_2m_max'][j])
            meteo_data['P'].append(res['daily']['precipitation_sum'][j])
            meteo_data['U'].append(res['daily']['wind_speed_10m_max'][j])
    
    #get humidity data
    payload.pop('wind_speed_unit')
    payload.update({'daily': 'relative_humidity_2m'})
    payload['hourly'] = payload.pop('daily')
    r = requests.get('https://archive-api.open-meteo.com/v1/archive', params=payload)

    if r.status_code != 200:
        print('Error: ', r.status_code)
        print(r.json())
        return None
    
    data = r.json()

    for i in range (len(data)):
        res = data[i]
        for j in range (int(len(res['hourly']['time'])/24)):
            humidity = res['hourly']['relative_humidity_2m'][j*24:(j+1)*24]
            meteo_data['H'].append(np.mean(humidity))
    
    df = pd.DataFrame(meteo_data)

    return df
