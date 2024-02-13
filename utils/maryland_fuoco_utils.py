import pysftp
import warnings
from datetime import date, timedelta
import os
from pyhdf.SD import *
import math
import pandas as pd
from tqdm import tqdm

HOST = "fuoco.geog.umd.edu"
USER_NAME = "fire"
PASSWORD = "burnt"
PORT = 22

def fetch_daily_files(start_date:date, end_date:date, daily_burned_area_folder=".", warnings_action="ignore", show_progress=False):
    """
    This function generates a "daily_burned_area.hdf" file that should be a copy of the GFED4
    data files in the GFED4 database hosted on the Maryland University SFTP server (fuoco) that correspond
    to dates in the date range sent as parameter. It does that by requesting the SFTP server for 
    the matching files.

    Parameters
    ----------
    start_date : date
        start date of the time range.
    end_date : date
        end date of the time range.
    gfed_files_folder : str
        path of the folder where to store fetched files from GFED4 database of the Fuoco remote server.
    warnings_action : str
        decides what action to do if there is warnings displaying. Default is "ignore". Set to None, if 
        the warnings should be displayed. 
    show_progress : bool
        if set to True shows a progress bar. Default is False.
    """

    with warnings.catch_warnings(action=warnings_action):
        # Get known host public keys
        cnopts = pysftp.CnOpts(knownhosts='known_hosts')
        # Set the keys to None (this alternative is a little bit risky in term of security)
        # Do not use it for an untrusted source, it trusts the host without checking the keys
        cnopts.hostkeys = None
        
        # Open an SFTP connection
        connection = pysftp.Connection(host=HOST, username=USER_NAME, password=PASSWORD, port=PORT, cnopts=cnopts, log=False)

        # Create a range for the loop
        rng = range((end_date - start_date).days + 1)
        if show_progress:
            rng = tqdm(range((end_date - start_date).days + 1), desc='Fetching Data Files From SFTP Server')
        
        # Download files from the server
        for nb_days in rng: # Iterate over days
            d = start_date + timedelta(days=nb_days)
            # Generate a local path for the data file
            local_path = os.path.join(daily_burned_area_folder, f'daily_burned_area_{d.day}_{d.month}_{d.year}.hdf')
            if not(os.path.isfile(local_path)): # Check if it's not already downloaded
                # Get the remote path of the data file
                day_in_year = (d - date(d.year, 1, 1)).days + 1 # Get the day number in the year from the complete date (year, month, day) 
                remote_path = f"data/GFED/GFED4/daily/{d.year}/GFED4.0_DQ_{d.year}{str(day_in_year).zfill(3)}_BA.hdf"
                
                # Check if the remote path exists in the server
                if connection.isfile(remote_path):
                    connection.get(remotepath=remote_path, localpath=local_path) # Download the file in the generated local path
        
        connection.close() # Close the connection

def get_daily_burned_area_data(start_date:date, end_date:date, lat_min:float, lat_max:float, lng_min:float, lng_max:float, daily_burned_area_folder=".",
                               show_progress=False):
    """
    Gets data from Maryland University SFTP server (fuoco) open data of daily burned area for a specified range in time and space 
    (geographical space) then returns a dataframe containing data about burned area for each day and 
    position within the range.

    Parameters
    ----------
    start_date : date
        start date of the time range.
    end_date : date
        end date of the time range.
    lat_min : float
        minimum bound of the latitude for the geographical range.
    lat_max : float
        maximum bound of the latitude for the geographical range.
    lng_min : float
        minimum bound of the longitude for the geographical range.
    lng_max : float
        maximum bound of the longitude for the geographical range.
    gfed_files_folder : str
        path of the folder from where to get GFED4 Fuoco files.
    show_progress: bool
        if set to True shows a progress bar. Default is False.

    Returns
    -------
    out : pandas.DataFrame
        the generated dataframe
    """

    # Fetch data file from server
    fetch_daily_files(start_date, end_date, daily_burned_area_folder, show_progress=show_progress)

    # Getting the x_min and x_max indexes
    x_min = math.floor((lng_min + 180) * 4)
    x_max = math.floor((lng_max + 180) * 4)
    # Getting the y_min and y_max indexes
    y_min = math.floor((lat_min + 90) * 4)
    y_max = math.floor((lat_max + 90) * 4)

    df = pd.DataFrame() # Final Dataframe to be returned

    # Creating a range for the loop
    rng = range((end_date - start_date).days + 1)
    if show_progress:
        tqdm(range((end_date - start_date).days + 1), desc='Reading HDF Files')

    for nb_days in rng:
        d = start_date + timedelta(days=nb_days)
        # Get the local path to read data from
        local_path = os.path.join(daily_burned_area_folder, f"daily_burned_area_{d.day}_{d.month}_{d.year}.hdf")

        if os.path.isfile(local_path):
            local_file = SD(local_path, SDC.READ) # Read the hdf file
            database = local_file.select('BurnedArea') # Open the burned area database
            earth_map = database.get() # get data from the database

            # Transform data into a dataframe
            temp_df = pd.DataFrame(
                data=earth_map[719 - y_max:719 - y_min + 1, x_min:x_max + 1][::-1],
                index=pd.Index(data=[-90 + i * 0.25 + 0.125 for i in range(y_min, y_max + 1)], name="latitude"),
                columns=[-180 + i * 0.25 + 0.125 for i in range(x_min, x_max + 1)]
            )

            temp_df = temp_df.stack()
            temp_df.index.set_names(names="longitude", level=1, inplace=True)
            temp_df = temp_df.reset_index(name="burned_area")
            temp_df.insert(2, 'date', pd.to_datetime(d))

            # Concatenate dataframes into one
            if df.empty:
                df = temp_df
            else:
                df = pd.concat([df, temp_df], ignore_index=True)

            # Close database and file
            database.endaccess()
            local_file.end()

    return df

def get_tree_cover_data(start_date:date, end_date:date, lat_min:float, lat_max:float, lng_min:float, lng_max:float, daily_burned_area_folder="."):
    """
    Gets data from Maryland University SFTP server (fuoco) open data of daily burned area for a specified range in time and space 
    (geographical space) by tree cover fraction then returns a dataframe containing data about burned area for each day and 
    position within the range and for each tree cover bin.

    Parameters
    ----------
    start_date : date
        start date of the time range.
    end_date : date
        end date of the time range.
    lat_min : float
        minimum bound of the latitude for the geographical range.
    lat_max : float
        maximum bound of the latitude for the geographical range.
    lng_min : float
        minimum bound of the longitude for the geographical range.
    lng_max : float
        maximum bound of the longitude for the geographical range.
    gfed_files_folder : str
        path of the folder from where to get GFED4 Fuoco files.

    Returns
    -------
    out : pandas.DataFrame
        the generated dataframe
    """
    # Fetch data file from server
    fetch_daily_files(start_date, end_date, daily_burned_area_folder)

    # Getting the x_min and x_max indexes
    x_min = math.floor((lng_min + 180) * 4)
    x_max = math.floor((lng_max + 180) * 4)
    # Getting the y_min and y_max indexes
    y_min = math.floor((lat_min + 90) * 4)
    y_max = math.floor((lat_max + 90) * 4)

    df = pd.DataFrame() # Final Dataframe to be returned

    print("Reading HDF Files ...")
    for nb_days in tqdm(range(0, (end_date - start_date).days + 1)):
        d = start_date + timedelta(days=nb_days)
        # Get the local path to read data from
        local_path = os.path.join(daily_burned_area_folder, f"daily_burned_area_{d.day}_{d.month}_{d.year}.hdf")

        if os.path.isfile(local_path):
            local_file = SD(local_path, SDC.READ) # Read the hdf file
            database = local_file.select('TreeCoverDist') # Open the tree cover database
            earth_map = database.get() # get data from the database

            tree_cover_per = 0
            for tree_cover_map in earth_map:
                # Transform data into a dataframe
                temp_df = pd.DataFrame(
                    data=tree_cover_map[719 - y_max:719 - y_min + 1, x_min:x_max + 1][::-1],
                    index=pd.Index(data=[-90 + i * 0.25 + 0.125 for i in range(y_min, y_max + 1)], name="latitude"),
                    columns=[-180 + i * 0.25 + 0.125 for i in range(x_min, x_max + 1)]
                )

                temp_df = temp_df.stack()
                temp_df.index.set_names(names="longitude", level=1, inplace=True)
                temp_df = temp_df.reset_index(name="burned_area")
                temp_df.insert(2, 'date', pd.to_datetime(d))

                # Add a tree cover bin column
                if tree_cover_per == 95:
                    temp_df['tree_cover_fraction'] = f'{tree_cover_per}% - 100%'
                else:
                    temp_df['tree_cover_fraction'] = f'{tree_cover_per}% - {tree_cover_per+4}%'
                    tree_cover_per += 5

                # Concatenate dataframes into one
                if df.empty:
                    df = temp_df
                else:
                    df = pd.concat([df, temp_df], ignore_index=True)

            # Close database and file
            database.endaccess()
            local_file.end()

    return df

def get_land_cover_data(start_date:date, end_date:date, lat_min:float, lat_max:float, lng_min:float, lng_max:float, daily_burned_area_folder="."):
    """
    Gets data from Maryland University SFTP server (fuoco) open data of daily burned area for a specified range in time and space 
    (geographical space) by land cover classes then returns a dataframe containing data about burned area for each day and 
    position within the range and for each land cover class.

    Parameters
    ----------
    start_date : date
        start date of the time range.
    end_date : date
        end date of the time range.
    lat_min : float
        minimum bound of the latitude for the geographical range.
    lat_max : float
        maximum bound of the latitude for the geographical range.
    lng_min : float
        minimum bound of the longitude for the geographical range.
    lng_max : float
        maximum bound of the longitude for the geographical range.
    gfed_files_folder : str
        path of the folder from where to get GFED4 Fuoco files.

    Returns
    -------
    out : pandas.DataFrame
        the generated dataframe
    """
    # Enumerate land classes (values to None, means that the class at that is not used)
    LAND_CLASSES = ['water', 'evergreen needleleaf forest', 'evergreen broadleaf forest', 'deciduous needleleaf forest', 
                    'deciduous broadleaf forest', 'mixed forests', 'closed shrubland', 'open shrubland', 'woody savannas',
                    'savannas', 'grasslands', None, 'croplands', 'urban and built-up', None, None, 'barren or sparsely vegetated',
                    'unclassified']
    # Fetch data file from server
    fetch_daily_files(start_date, end_date, daily_burned_area_folder)

    # Getting the x_min and x_max indexes
    x_min = math.floor((lng_min + 180) * 4)
    x_max = math.floor((lng_max + 180) * 4)
    # Getting the y_min and y_max indexes
    y_min = math.floor((lat_min + 90) * 4)
    y_max = math.floor((lat_max + 90) * 4)

    df = pd.DataFrame() # Final Dataframe to be returned

    print("Reading HDF Files ...")
    for nb_days in tqdm(range(0, (end_date - start_date).days + 1)):
        d = start_date + timedelta(days=nb_days)
        # Get the local path to read data from
        local_path = os.path.join(daily_burned_area_folder, f"daily_burned_area_{d.day}_{d.month}_{d.year}.hdf")

        if os.path.isfile(local_path):
            local_file = SD(local_path, SDC.READ) # Read the hdf file
            database = local_file.select('LandCoverDist') # Open the land cover database
            earth_map = database.get() # get data from the database

            land_class_index = 0
            for land_cover_map in earth_map:
                # Transform data into a dataframe
                temp_df = pd.DataFrame(
                    data=land_cover_map[719 - y_max:719 - y_min + 1, x_min:x_max + 1][::-1],
                    index=pd.Index(data=[-90 + i * 0.25 + 0.125 for i in range(y_min, y_max + 1)], name="latitude"),
                    columns=[-180 + i * 0.25 + 0.125 for i in range(x_min, x_max + 1)]
                )

                temp_df = temp_df.stack()
                temp_df.index.set_names(names="longitude", level=1, inplace=True)
                temp_df = temp_df.reset_index(name="burned_area")
                temp_df.insert(2, 'date', pd.to_datetime(d))

                # Add a land cover column
                if land_class_index < len(LAND_CLASSES):
                    temp_df['land_class'] = LAND_CLASSES[land_class_index]
                    land_class_index += 1
                else:
                    temp_df['land_class'] = None

                # Concatenate dataframes into one
                if df.empty:
                    df = temp_df
                else:
                    df = pd.concat([df, temp_df], ignore_index=True)

            # Close database and file
            database.endaccess()
            local_file.end()

    return df