import argparse
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import pandas as pd
from utils.power_nasa_utils import get_data as get_meteo_data
from utils.fire_index_utils import get_data_with_fire_indexes
from utils.maryland_fuoco_utils import get_data as get_burned_area_data
from utils.gfed_utils import get_gfed_emissions_data_for_range as get_emissions_data

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
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def execute_query(connection:mysql.connector.connection.MySQLConnection, query:str):
    """
    Executes a specefic query for a specific MySQL connection.
    
    Parameters
    ----------
    connection : MySQLConnection
        the specific MySQL connection.
    query : str
        the query to be executed.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as err:
        print(f"Error: '{err}'")

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

    args=vars(parser.parse_args())

    # Transform args
    lat_min = float(args['lat_min'])
    lat_max = float(args['lat_max'])
    lng_min = float(args['lng_min'])
    lng_max = float(args['lng_max'])
    start_date = datetime.strptime(args['start_date'], "%d/%m/%Y").date()
    end_date = datetime.strptime(args['end_date'], "%d/%m/%Y").date()

    # Load env variables
    load_dotenv()

    # The presumed final dataframe
    df: pd.DataFrame = None

    # Get meteo data
    print("Fetching Meteo Data ...")
    meteo_df = get_meteo_data(start_date, end_date, lat_min, lat_max, lng_min, lng_max)
    
    # Get data with fire indexes
    print("Calculating Fire Indexes ...")
    fire_indexes_df = get_data_with_fire_indexes(meteo_df, temp_meteo_folder="data/meteo")
    del meteo_df # Delete meteo dataframe from memory as we don't need it anymore
    
    # Get data from burned area
    print("Fetching Burned Area Data ...")
    burned_area_df = get_burned_area_data(start_date, end_date, lat_min, lat_max, lng_min, lng_max, daily_burned_area_folder="data/fuoco")
    print(burned_area_df)