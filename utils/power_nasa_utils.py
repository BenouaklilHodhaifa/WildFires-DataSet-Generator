import pandas as pd
import requests
from fire_index_utils import get_data_with_fire_indexes
from tqdm import tqdm

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
        start date in the format 'YYYYMMDD'
    end_date: str
        end date in the format 'YYYYMMDD'
    """

    def get_point_weather(latitude, longitude, start_date, end_date):
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
    
    def fill_point_in_dict(point, meteo_data):
        res = point['properties']['parameter']
     
        # append the time 
        for elem in list(res['T2M'].keys()):
            meteo_data['time'].append(elem)

        for j in range (len(res['T2M'])):
            meteo_data['longitude'].append(data['geometry']['coordinates'][0])
            meteo_data['latitude'].append(data['geometry']['coordinates'][1])
            meteo_data['T'].append(res['T2M'][meteo_data['time'][j]])
            meteo_data['P'].append(res['PRECIPITATIONCAL'][meteo_data['time'][j]])
            meteo_data['U'].append(res['WS10M'][meteo_data['time'][j]])
            meteo_data['H'].append(res['RH2M'][meteo_data['time'][j]])    
        
    meteo_data = {
        'time': [],
        'latitude': [],
        'longitude': [],
        'T': [],
        'P': [],
        'H': [],
        'U': []
    }

    coordinates_array = coordinates_selecter(lat_min=lat_min, lat_max=lat_max, lng_max=lon_max, lng_min=lon_min)

    for i in tqdm(range(len(coordinates_array))):
        data = get_point_weather(coordinates_array[i][0], coordinates_array[i][1], start_date, end_date)
        fill_point_in_dict(data, meteo_data)

    df = pd.DataFrame(meteo_data)
    df = get_data_with_fire_indexes(df)

    return df