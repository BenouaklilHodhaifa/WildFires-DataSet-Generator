from firedanger import firedanger
import pandas as pd
import os
from datetime import datetime as dt

def get_dataset_with_fire_indexes(ds:pd.DataFrame, time_name="time", time_format="%Y%m%d", temp_name="T",
                                  precip_name="P", hum_name="H", wind_name="U", temp_meteo_folder=".") -> pd.DataFrame:
    """
    Adds fire indexes (ffmc, dmc, dc, isi, bui and fwi) to a specified dataset that has to include 
    for each row: the day of the observation (time), the air temperature (°C), precipitation (mm), air humidity (%)
    and wind speed (m/s).

    Parameters
    ----------
    ds : pandas.DataFrame
        dataset specified to work on. It has to include all required attributes to be able to calculate 
        fire indexes.
    time_name : str
        name of the column referring to the time (day) of each observation. Default is "time".
    time_format : str
        format used for the day of the observation. Default is "%Y%m%d".
    temp_name : str
        name of the column referring to the temperature (°C) of each observation. Default is "T".
    precip_name : str
        name of the column referring to the precipitation (mm) of each observation. Default is "P".
    hum_name : str
        name of the column referring to the air humidity (%) of each observation. Default is "H".
    wind_name : str
        name of the column referring to the wind speed (m/s) of each observation. Default is "U".
    temp_meteo_folder : str
        path of the folder where to store temporary files made from meteo data
    """
    # Create a unique name for a temporary file
    temp_file_name = os.path.join(temp_meteo_folder, f'temp{int(dt.now().timestamp())}.csv')
    # Save the dataset to a the temporary file
    ds.to_csv(temp_file_name)
    # Create a firedanger instance
    fire = firedanger(temp_file_name, time_name=time_name, time_format=time_format)
    # Calculate fire indexes (ffmc, dmc, dc, isi, bui and fwi)
    fire.calc_canadian_fwi(temp=temp_name, precip=precip_name, hum=hum_name, wind=wind_name)
    # Return the dataset enriched with the new indexes added to it
    return fire.to_dataframe()