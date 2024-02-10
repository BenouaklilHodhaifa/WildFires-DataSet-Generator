from .custom_exceptions import GFED_YearNotAvailableException
from .custom_exceptions import GFED_RequestException
import requests
import pandas as pd
import numpy as np
import math
import h5py
import os
from flask import current_app as app
from datetime import datetime as dt
from datetime import timedelta as td

def year_not_available(year):
    MAX_YEAR = 2016  # the max year allowed in the API
    MIN_YEAR = 1997  # the min year allowed in the API
    return year < MIN_YEAR or year > MAX_YEAR

def make_remote_GFED_file_url(year):
    BASE_URL = "https://www.geo.vu.nl/~gwerf/GFED/GFED4/"

    remote_file_name = "GFED4.1s_" + str(year) + ".hdf5"
    result = BASE_URL + remote_file_name
    return result

def fetch_gfed_data_for_year(year :int):
    """
    This function generates a "gfed_data.hdf5" file that should be a copy of the GFED
    data file in the GFED database that corresponds to the "year" sent as parameter.
    It does that by requesting the https server of the GFED database for the matching file.
    """
    # checking for year validity
    if year_not_available(year):
        raise GFED_YearNotAvailableException \
            (f"GFED_YearNotAvailableException: year {year} is not available")


    remote_file_url = make_remote_GFED_file_url(year)

    print('made remote file url: {}'.format(remote_file_url))
    request = requests.get(remote_file_url)
    # checking for the request status
    if request.status_code != 200: # if the request is not successful
        raise GFED_RequestException \
            (f"GFED_RequestException: request returned with status code = {request.status_code}", request.status_code)

    # writing fetched data to the local gfed_data.hdf5 file
    path = os.path.join(app.config['GFED_FILES_FOLDER'], f"gfed_data_{year}.hdf5")
    with open(path, "wb") as f:
        f.write(request.content)

# the coordinate selector

def coordinates_selecter(lat_min:float, lat_max:float, lng_min:float, lng_max:float)->np.ndarray:
    """
    This function receives as input a geogrphical span :
        lng_min: longitude min
        lng_max: longitude max
        lat_min: latititude min
        lat_max: latitude max

    and returns the corresponding coordinates (center of the activated cells) in the GFED grid as an np array
    """
    #getting the x_min and x_max indexes
    x_min = math.floor((lng_min+180)*4)
    x_max = math.floor((lng_max+180)*4)
    #getting the y_min and y_max indexes
    y_min = math.floor((lat_min+90)*4)
    y_max = math.floor((lat_max+90)*4)

    #creating the np array
    number_of_rows = (y_max - y_min + 1) * (x_max - x_min + 1)
    ar = np.empty(shape=(number_of_rows, 2), dtype=np.float64)

    #filling the np array
    base = 0
    step = x_max - x_min
    for lat_index in range(y_min, y_max+1):
        lat_coord  = - 90 + lat_index * 0.25 + 0.125
        for row, lon_index in zip(range(base, base + step + 1), range(x_min, x_max+1)):
                ar[row, 0] = lat_coord
                ar[row, 1] = -180 + lon_index * 0.25 + 0.125
        base = base + step + 1
    return ar


#
def gfed_portioner(file_path: str, month: int, lat_min: float, lat_max: float, lng_min: float,
                   lng_max: float) -> pd.DataFrame:
    """
    This function receives as input:
        file_name: the path to the GFED file
        # earth_map: a 720 * 1440 gfed earth map
        lng_min: longitude min
        lng_max: longitude max
        lat_min: latitude min
        lat_max: latitude max

    and returns a data frame corresponding to the delimited region:
        y: the latitude cell in the gfed earth map
        x: the longitude cell in the gfed earth map
        Longitude: the longitude of the center of the cell
        Latitude: the latitude of the center of the cell
        Was Burnt: a boolean indicating whether that cell was burnt
        Burnt %: The percentage of that cell that burnt
    """
    # getting the x_min and x_max indexes
    x_min = math.floor((lng_min + 180) * 4)
    x_max = math.floor((lng_max + 180) * 4)
    # getting the y_min and y_max indexes
    y_min = math.floor((lat_min + 90) * 4)
    y_max = math.floor((lat_max + 90) * 4)

    with h5py.File(file_path, 'r') as file:
        earth_map = np.array(file.get("burned_area/{}/burned_fraction".format(str(month))))

    df = pd.DataFrame(
        data=earth_map[719 - y_max:719 - y_min + 1, x_min:x_max + 1][::-1],
        index=pd.Index(data=[-90 + i * 0.25 + 0.125 for i in range(y_min, y_max + 1)], name="latitude"),
        columns=[-180 + i * 0.25 + 0.125 for i in range(x_min, x_max + 1)]
    )

    df = df.stack()
    df.index.set_names(names="longitude", level=1, inplace=True)
    df = df.reset_index(name="burnt")
    # df.insert(2, 'Was burnt', (df['Burnt %'] != 0).astype(int))
    # df.insert(0, 'y', ((90 - df['Latitude']) * 4).astype(int))
    # df.insert(1, 'x', ((df['Longitude'] + 180) * 4).astype(int))

    return df

def get_gfed_data_for_range(start_date:dt, end_date:dt, lat_min:float, lat_max:float, lng_min:float, lng_max:float):
    """Gets data from GFED official open data for a specified range in time and space (geographical space) then 
    returns three dataframes:
        - A dataframe containing all geographical positions retrieved (latitude, longitude)
        - A dataframe containing all months retreived (month and year of the month)
        - A dataframe containing data about burned area fraction and emissions fraction for each month and position within the range
    
    Parameters
    ----------
    start_date : datetime
        start date of the time range.
    end_date : datetime
        end date of the time range.
    lat_min : float
        minimum bound of the latitude for the geographical range.
    lat_max : float
        maximum bound of the latitude for the geographical range.
    lng_min : float
        minimum bound of the longitude for the geographical range.
    lng_max : float
        maximum bound of the longitude for the geographical range.
    """

    geo_pos_df:pd.DataFrame = None
    time_df:pd.DataFrame = None
    gfed_df:pd.DataFrame = None

    for year in range(start_date.year, end_date.year): # Iterate in years

        month_min = start_date.month if year == start_date.year else 1 # Begin with the start_date month if it's the first year iteration
        month_max = end_date.month if year == end_date.year else 12 # End with the end_date month if reached (the last year iteration)

        file_path = os.path.join(app.config['GFED_FILES_FOLDER'], f"gfed_data_{year}.hdf5") # Path of the gfed data file for the current year
        if not(os.path.isfile(file_path)): # If the file doesn't exist locally
            fetch_gfed_data_for_year(year) # Fetch GFED data file for the year

        for month in range(month_min, month_max): # Iterate in months
            temp_gfed_df = gfed_portioner(f"gfed_data_{year}.hdf5", month, lat_min, lat_max, lng_min, lng_max) # Get data in the geographical range
            temp_gfed_df.insert(2, 'month', month) # Add a month column
            temp_gfed_df.insert(3, 'year', year) # Add a year column

            # Set the geographical positions dataframe
            if geo_pos_df == None:
                geo_pos_df = temp_gfed_df[['latitude', 'longitude']]

            # Concatenate produced dataframes for time data (month/year)
            if time_df == None:
                time_df = pd.DataFrame({
                    'month': month,
                    'year': year
                })
            else:
                temp_time_df = pd.DataFrame({
                    'month': month,
                    'year': year
                })
                time_df = pd.concat([time_df, temp_time_df], ignore_index=True)

            # Concatenate produced dataframes for gfed data
            if gfed_df == None:
                gfed_df = temp_gfed_df
            else:
                gfed_df = pd.concat([gfed_df, temp_gfed_df], ignore_index=True)

    return geo_pos_df, time_df, gfed_df


def gfed_modular_portioner(earth_map:np.ndarray, output_column_name:str, lat_min: float, lat_max: float, lng_min: float, lng_max: float) -> pd.DataFrame:
    """
    This function receives as input:
        file_name: the path to the GFED file
        # earth_map: a 720 * 1440 gfed earth map
        lng_min: longitude min
        lng_max: longitude max
        lat_min: latitude min
        lat_max: latitude max

    and returns a data frame corresponding to the delimited region:
        y: the latitude cell in the gfed earth map
        x: the longitude cell in the gfed earth map
        Longitude: the longitude of the center of the cell
        Latitude: the latitude of the center of the cell
        Was Burnt: a boolean indicating whether that cell was burnt
        Burnt %: The percentage of that cell that burnt
    """
    # getting the x_min and x_max indexes
    x_min = math.floor((lng_min + 180) * 4)
    x_max = math.floor((lng_max + 180) * 4)
    # getting the y_min and y_max indexes
    y_min = math.floor((lat_min + 90) * 4)
    y_max = math.floor((lat_max + 90) * 4)

    df = pd.DataFrame(
        data=earth_map[719 - y_max:719 - y_min + 1, x_min:x_max + 1][::-1],
        index=pd.Index(data=[-90 + i * 0.25 + 0.125 for i in range(y_min, y_max + 1)], name="latitude"),
        columns=[-180 + i * 0.25 + 0.125 for i in range(x_min, x_max + 1)]
    )

    df = df.stack()
    df.index.set_names(names="longitude", level=1, inplace=True)
    df = df.reset_index(name=output_column_name)
    # df.insert(2, 'Was burnt', (df['Burnt %'] != 0).astype(int))
    df.insert(0, 'y', ((90 - df['Latitude']) * 4).astype(int))
    df.insert(1, 'x', ((df['Longitude'] + 180) * 4).astype(int))

    return df


def get_gfed_emissions_data_for_range(start_date:dt, end_date:dt, lat_min:float, lat_max:float, lng_min:float, lng_max:float) ->pd.DataFrame:
    def date_iterator(start_date:dt, end_date:dt):
        delta = td(days=1)
        current_date = start_date
        while(current_date <= end_date):
            yield current_date
            current_date = current_date + delta
    
    final_emissions_df:pd.DataFrame = None

    for year in range(start_date.year, end_date.year+1):
        # preparing the file corresponding to the year
        # i believe this should be in a separate module for respecting the ETL architecture + separation of concerns
        file_path = os.path.join(app.config['GFED_FILES_FOLDER'], f"gfed_data_{year}.hdf5") # Path of the gfed data file for the current year
        if not(os.path.isfile(file_path)): # If the file doesn't exist locally
            fetch_gfed_data_for_year(year) # Fetch GFED data file for the year
        
        #preparing the local_start_date and local_end_date for the current year
        if year == start_date.year:
            local_start_date = start_date 
        else:
            local_start_date = dt(year,1,1) # year - january - 1st

        if year == end_date.year:
            local_end_date = end_date
        else:
            local_end_date = dt(year,12,31) # year  - december - 31st
        
        # opening the file
        file = h5py.File(file_path, 'r')
        
        for date in date_iterator(local_start_date, local_end_date):
            earth_map = np.array(file.get("emissions/"+str(date.month).zfill(2)+"/daily_fraction/day_"+str(date.day)))
            temp_emissions_df = gfed_modular_portioner(f"gfed_data_{year}.hdf5", "emission", lat_min, lat_max, lng_min, lng_max) # Get data in the geographical range
            temp_emissions_df.insert(2, 'day', date.day) # Add a day column
            temp_emissions_df.insert(3, 'month', date.month) # Add a month column
            temp_emissions_df.insert(4, 'year', date.year) # Add a year column
        
            if final_emissions_df == None:
                final_emissions_df = temp_emissions_df
            else:
                final_emissions_df = pd.concat([final_emissions_df, temp_emissions_df], ignore_index=True)

        file.close()
    
    return final_emissions_df