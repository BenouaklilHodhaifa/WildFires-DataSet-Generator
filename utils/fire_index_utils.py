from firedanger import firedanger
import pandas as pd
import os
from datetime import date, timedelta, datetime
import warnings
import pandas as pd
from tqdm import tqdm
import math

def convert_to_datetime(d:date):
    """Converts a date to datetime.
    
    Parameters
    ----------
    d : date
        entry in type date.

    Returns
    -------
    out : datetime
        converted into datetime
    """
    return datetime(d.year, d.month, d.day)

def get_data_with_fire_indexes(ds:pd.DataFrame, start_date:date, end_date:date, time_name="date", time_format="%Y%m%d", temp_name="temperature",
                                  precip_name="precipitation", hum_name="air_humidity", wind_name="wind_speed", 
                                  temp_meteo_folder=".", date_interval_size:int=None, show_progress=False,
                                   warnings_action="ignore") -> pd.DataFrame:
    """
    Adds fire indexes (ffmc, dmc, dc, isi, bui and fwi) to a specified dataset that has to include 
    for each row: the day of the observation (time), the air temperature (°C), precipitation (mm), air humidity (%)
    and wind speed (m/s).

    Parameters
    ----------
    ds : pandas.DataFrame
        dataset specified to work on. It has to include all required attributes to be able to calculate 
        fire indexes.
    start_date : date
        start date of the time range.
    end_date : date
        end date of the time range.
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
    date_interval_size : int
        a date interval size in days to calculate fire weather indexes for. 
        This parameter is intended to accelerate the calculation time in detriment to results quality. 
        Default is None.
    show_progress: bool
        if set to True shows a progress bar. Default is False.
    warnings_action : str
        decides what action to do if there is warnings displaying. Default is "ignore". Set to None, if 
        the warnings should be displayed. 

    Returns
    -------
    out : pandas.DataFrame
        the generated dataframe
    """


    first_time = True
    df = pd.DataFrame({
        'latitude': [],
        'longitude': [],
        time_name: [],
        temp_name: [],
        precip_name: [],
        hum_name: [],
        wind_name: [],
        'ffmc': [],
        'dmc': [],
        'dc': [],
        'isi': [],
        'bui': [],
        'fwi': []
    })

    with warnings.catch_warnings(action=warnings_action):
        # Create a unique name for a temporary file
        temp_file_name = os.path.join(temp_meteo_folder, f"temp_{datetime.now().isoformat().replace(':','_')}.csv")
        # Save the dataset to a the temporary file
        unique_coords = ds[["latitude","longitude"]].drop_duplicates()

        # Creating a range for the loop
        nb_intervals = math.ceil(((end_date - start_date).days + 1) / date_interval_size) if date_interval_size != None else 1
        rng = range(unique_coords.shape[0] * nb_intervals)
        if show_progress:
            rng = tqdm(range(unique_coords.shape[0] * nb_intervals), desc='Calculating Fire Weather Indexes')

        for i in rng:
            row_index = i // nb_intervals
            lat_condition = ds["latitude"]==unique_coords.iloc[row_index, 0]
            lng_condition = ds["longitude"]==unique_coords.iloc[row_index, 1]

            date_condition_gt = [True] * ds.shape[0]
            date_condition_lt = date_condition_gt
            if date_interval_size != None:
                date_index = i % nb_intervals
                temp_end_interval = start_date + timedelta(days=((date_index + 1)*date_interval_size) - 1)
                end_interval = end_date if end_date <= temp_end_interval else temp_end_interval
                date_condition_gt = ds["date"] >= convert_to_datetime(start_date + timedelta(days=date_index*date_interval_size))
                date_condition_lt = ds["date"] <= convert_to_datetime(end_interval)

            local_ds = ds[lat_condition & lng_condition & date_condition_gt & date_condition_lt]
            local_ds['date'] = local_ds['date'].dt.strftime(time_format)
            local_ds.to_csv(temp_file_name)
            # Create a firedanger instance
            fire = firedanger(temp_file_name, time_name=time_name, time_format=time_format)
            # Calculate fire indexes (ffmc, dmc, dc, isi, bui and fwi)
            fire.calc_canadian_fwi(temp=temp_name, precip=precip_name, hum=hum_name, wind=wind_name)
            
            # Return the dataset enriched with the new indexes added to it
            local_df:pd.DataFrame = fire.to_dataframe()
            # Insert date as column and remove it from index
            local_df.insert(3, 'date', local_df.index)
            local_df.set_index('Unnamed: 0', inplace=True, drop=True)
            
            if first_time:
                first_time = False
                df = local_df
            else:
                df = pd.concat([df, local_df], ignore_index=True)
    
    # Delete the temporary file
    os.remove(temp_file_name)

    return df