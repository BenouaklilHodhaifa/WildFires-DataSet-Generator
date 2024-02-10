import pandas as pd
import requests
import csv
#from gfed_utils import coordinates_selecter

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
    #getting the coordinates
    #coordinates = coordinates_selecter(lat_min, lat_max, lon_min, lon_max)

    #temperature, wind speed, humidity
    bulk_payload = {
        'latitude-min': lat_min,
        'latitude-max': lat_max,
        'longitude-min': lon_min,
        'longitude-max': lon_max,
        'parameters': 'T2M,WS10M,RH2M',
        'community': 'AG',
        'start': start_date,
        'end': end_date,
        'format': 'JSON'
    }

    r = requests.get('https://power.larc.nasa.gov/api/temporal/daily/regional', params=bulk_payload)

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

    for i in range (len(data['features'])):
        res = data['features'][i]['properties']['parameter']

        for elem in list(res['T2M'].keys()):
            meteo_data['time'].append(elem)

        for j in range (len(res['T2M'])):
            meteo_data['longitude'].append(data['features'][i]['geometry']['coordinates'][0])
            meteo_data['latitude'].append(data['features'][i]['geometry']['coordinates'][1])
            meteo_data['T'].append(res['T2M'][meteo_data['time'][j]])
            meteo_data['P'].append(0)
            meteo_data['U'].append(res['WS10M'][meteo_data['time'][j]])
            meteo_data['H'].append(res['RH2M'][meteo_data['time'][j]])
    
    # we have to implement getting the precipitation data also

    df = pd.DataFrame(meteo_data)
    return df