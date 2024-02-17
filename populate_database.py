import argparse
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime, date, timedelta
import pandas as pd
from utils.power_nasa_utils import get_data as get_meteo_data
from utils.fire_index_utils import get_data_with_fire_indexes
from utils.maryland_fuoco_utils import get_daily_burned_area_data
from utils.gfed_utils import get_gfed_emissions_data_for_range as get_emissions_data
import numpy as np
import concurrent.futures
import logging
from typing import Literal

# Ignore logs from third-party modules (Change this line if you want to show all logs)
logging.getLogger().setLevel(logging.CRITICAL)

WILFIRES_DATA_INSERT_QUERY = open('sql/wildfires_data_insert.sql').read()
DATASETS_INSERT_QUERY = open('sql/datasets_insert.sql').read()
DATASETS_UPDATE_QUERY = open('sql/datasets_update.sql').read()

# Connect to database
def connect_to_database():
    """
    Connect to the database and returns a connection instance if the connexion was successfull. 
    Otherwise it returns None.
    
    Returns
    -------
    connection : PooledMySQLConnection | MySQLConnectionAbstract | None
        the created connection.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.environ['DATABASE_HOST'],
            user=os.environ['DATABASE_USERNAME'],
            passwd=os.environ['DATABASE_PASSWORD'],
            database=os.environ['DATABASE_NAME']
        )
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def execute_dql_query(connection:mysql.connector.connection.MySQLConnection, query:str, params:tuple):
    """
    Executes a specefic DQL query for a specific MySQL connection.
    
    Parameters
    ----------
    connection : MySQLConnection
        the specific MySQL connection.
    query : str
        the query to be executed.

    Returns
    -------
    out : Generator[MySQLCursor, None, None] | None
        Result of the query
    """
    res = None
    cursor = connection.cursor(buffered=True)

    try:
        cursor.execute(query, params)
        res = []
        for e in cursor:
            res.append(e)
    except Error as err:
        print(f"Error: '{err}'")

    cursor.close()
    return res

def execute_dml_query(connection:mysql.connector.connection.MySQLConnection, query:str, params:tuple|list[tuple], many=False):
    """
    Executes a specefic DML query for a specific MySQL connection.
    
    Parameters
    ----------
    connection : MySQLConnection
        the specific MySQL connection.
    query : str
        the query to be executed.
    many : bool
        specifies if there is multiple lines of data to be handled.

    Returns
    -------
    out : int | None
        id of the last inserted row if it's a AUTOINCREMENT ID
    """
    res = None
    cursor = connection.cursor(buffered=True)

    try:
        if many:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)

        connection.commit()
        res = (cursor.lastrowid, cursor.rowcount)
    except Error as err:
        print(f"Error: '{err}'")

    cursor.close()
    return res

def load_dataframe_to_db(start_date:date, end_date:date, lat_min:float, lat_max:float, lng_min:float, lng_max:float, 
                         dataset_id:int=None, date_interval_size:int=None, show_progress=Literal['none', 'all', 'meteo']):
    """
    Loads data into database for a specific geographical and time range.

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
    dataset_id : int
        id of the dataset to link retrived data to. Default is None.
    date_interval_size : int
        a date interval size in days to calculate fire weather indexes for. 
        This parameter is intended to accelerate the calculation time in detriment to results quality. 
        Default is None.
    show_progress : str
        if set to shows progress of the loading pipeline. Can take a value from the 
        specific set ('none', 'all', 'meteo'). Default is none.
    
    Returns
    -------
    out : pandas.DataFrame
        the generated dataframe.
    """
    # The generated dataframe
    df: pd.DataFrame = None
    # Get meteo data
    meteo_df = get_meteo_data(start_date, end_date, lat_min, lat_max, lng_min, lng_max, 
                              show_progress=(show_progress=='meteo' or show_progress=='all'))
    
    # Get data with fire indexes
    fire_indexes_df = get_data_with_fire_indexes(meteo_df, start_date, end_date, temp_meteo_folder="data/meteo", 
                                                 date_interval_size=date_interval_size,
                                                 show_progress=(show_progress == 'all'))
    del meteo_df # Delete meteo dataframe from memory as we don't need it anymore
    
    # Get data from burned area
    burned_area_df = get_daily_burned_area_data(start_date, end_date, lat_min, lat_max, lng_min, lng_max,
                                                 daily_burned_area_folder="data/fuoco", 
                                                 show_progress=(show_progress=='all'))

    # Get emissions data
    emissions_df = get_emissions_data(start_date, end_date, lat_min, lat_max, lng_min, lng_max,
                                       gfed_files_folder="data/gfed", 
                                       show_progress=(show_progress=='all'))
    # Join all data
    meteo_burned_area_df = pd.merge(fire_indexes_df, burned_area_df, how="left", on=['latitude', 'longitude', 'date']) # Do the first join
    del fire_indexes_df # Delete the meteo dataframe with fire indexes from memory as we don't need it anymore
    del burned_area_df # Delete the burned area dataframe from memory as we don't need it anymore
    df = pd.merge(meteo_burned_area_df, emissions_df, how="left", on=['latitude', 'longitude', 'date']) # Do the second and final merge
    del meteo_burned_area_df # Delete the first merge dataframe from memory as we don't need it anymore
    del emissions_df # Delete the emissions dataframe from memory as we don't need it anymore

    # Add a last column to specify in the location was burnt or not (boolean)
    df['burnt'] = (df['burned_area'] > 0).astype(int)

    # Transform date column to ISO Format
    df['date'] = df['date'].map(lambda x: datetime.date(x))

    # Replace Nan values with None
    df.replace(np.nan, None, inplace=True)

    # Connect to database
    if show_progress == 'all':
        print("Connecting to Database ...")
    connection = connect_to_database()

    # Insert the generated dataframe to the database
    if show_progress == 'all':
        print("Inserting into Database ...")
    
    insert_values = [(*row, dataset_id) for row in df.values]
    res = execute_dml_query(connection, WILFIRES_DATA_INSERT_QUERY, insert_values, many=True)
    
    # Number of rows inserted
    nbr_rows = 0
    if res != None:
        # Get row count
        nbr_rows = res[1]
        # Print a final message
        if show_progress == 'all':
            print("\nDatabase has been populated successfully !")
    else:
        if show_progress == 'all':
            print('\nAn error occured when executing the INSERT SQL query, check logs for more details.')
    
    # Close connection
    connection.close()
    # Delete the generated dataframe
    del df

    return nbr_rows

# Main Script
if __name__ == "__main__":
    # Get script args
    parser=argparse.ArgumentParser()

    parser.add_argument("--lat_min", help="Minimum latitude of the geographical range")
    parser.add_argument("--lat_max", help="Maximum latitude of the geographical range")
    parser.add_argument("--lng_min", help="Minimum longitude of the geographical range")
    parser.add_argument("--lng_max", help="Maximum longitude of the geographical range")
    parser.add_argument("--start_date", help="Start date of the time range in format dd/mm/yy")
    parser.add_argument("--end_date", help="End date of the time range in format dd/mm/yy")
    parser.add_argument("--dataset_name", help="Defines a name for the dataset that will be created")
    parser.add_argument("--nb_checkpoints_lat", help="Divides the geographical latitude range into the number of checkpoints specified and loads data to database at the end of each checkpoint")
    parser.add_argument("--nb_checkpoints_lng", help="Divides the geographical longitude range into the number of checkpoints specified and loads data to database at the end of each checkpoint")
    parser.add_argument("--date_interval_size", help="Specifies a date interval size in days to calculate fire weather indexes for. This parameter is intended to accelerate the calculation time in detriment to results quality.")
    parser.add_argument("--parallel", help="If set to 1, the process will be divided on the maximum number of threads available.")

    args=vars(parser.parse_args())

    # Transform args
    lat_min = float(args['lat_min'])
    lat_max = float(args['lat_max'])
    lng_min = float(args['lng_min'])
    lng_max = float(args['lng_max'])
    start_date = datetime.strptime(args['start_date'], "%d/%m/%Y").date()
    end_date = datetime.strptime(args['end_date'], "%d/%m/%Y").date()
    dataset_name = args['dataset_name'] if args['dataset_name'] != None else 'NULL'
    nb_checkpoints_lat = int(args['nb_checkpoints_lat']) if args['nb_checkpoints_lat'] != None else 1
    nb_checkpoints_lng = int(args['nb_checkpoints_lng']) if args['nb_checkpoints_lng'] != None else 1
    date_interval_size  = int(args['date_interval_size']) if args['date_interval_size'] != None else None
    parallel = bool(int(args["parallel"])) if args["parallel"] else False

    # Load env variables
    load_dotenv()

    # Connect to database and create a dataset
    connection = connect_to_database()
    nbr_rows = 0
    fwi_backtrack_size = date_interval_size if date_interval_size != None else (end_date-start_date).days
    created_at = datetime.now()
    res = execute_dml_query(connection, DATASETS_INSERT_QUERY, (dataset_name, nbr_rows, fwi_backtrack_size, created_at.isoformat()))
    connection.close()

    # If the dataset is created successfully
    if res != None:
        dataset_id = res[0]

        # Load data to database by checkpoints
        lat_step = (lat_max - lat_min) / nb_checkpoints_lat
        lng_step = (lng_max - lng_min) / nb_checkpoints_lng

        if parallel:
            cpt = 0 # Number of checkpoints passed (completed)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [] # Array to store future objects
                print(f"INFO: Running on {executor._max_workers} threads.")
                for i in range(nb_checkpoints_lat * nb_checkpoints_lng):
                    lat_index = i // nb_checkpoints_lat
                    lng_index = i % nb_checkpoints_lat
                    futures.append(executor.submit(load_dataframe_to_db, start_date, 
                                                    end_date, lat_min + lat_index * lat_step,
                                                    lat_min + (lat_index + 1) * lat_step,
                                                    lng_min + lng_index * lng_step, 
                                                    lng_min + (lng_index + 1) * lng_step,
                                                    dataset_id,
                                                    date_interval_size,
                                                    'meteo'))
                
                for future in concurrent.futures.as_completed(futures):
                    cpt += 1
                    nbr_rows += future.result()
                    print(f"Total Progress : {cpt*100/(nb_checkpoints_lat * nb_checkpoints_lng)} %")
        else:
            for i in range(nb_checkpoints_lat * nb_checkpoints_lng):
                print(f"\n============= CheckPoint {i+1} ===============\n")
                lat_index = i // nb_checkpoints_lat
                lng_index = i % nb_checkpoints_lat
                nbr_rows += load_dataframe_to_db(start_date, end_date, 
                                        lat_min + lat_index * lat_step,
                                        lat_min + (lat_index + 1) * lat_step,
                                        lng_min + lng_index * lng_step, 
                                        lng_min + (lng_index + 1) * lng_step,
                                        dataset_id=dataset_id,
                                        date_interval_size=date_interval_size,
                                        show_progress='all')
                
                print(f"Total Progress : {(i+1)*100/(nb_checkpoints_lat * nb_checkpoints_lng)} %")

        connection = connect_to_database()
        created_at = datetime.now()
        execute_dml_query(connection, DATASETS_UPDATE_QUERY, (nbr_rows, created_at.isoformat(), dataset_id))
        connection.close()
    
    else:
        print("The dataset could not be created !")