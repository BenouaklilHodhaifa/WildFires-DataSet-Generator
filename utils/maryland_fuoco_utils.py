import pysftp
import warnings
from datetime import date, timedelta
import os

HOST = "fuoco.geog.umd.edu"
USER_NAME = "fire"
PWD = "burnt"
PORT = 22

def fetch_daily_burnt_area(start_date:date, end_date:date, daily_burnt_area_folder=".", warnings_action="ignore"):
    """
    This function generates a "daily_burnt_area.hdf" file that should be a copy of the GFED4
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
        path of the folder where to store fetched files from GFED4 remote site.
    warnings_action : str
        decides what action to do if there is warnings displaying. Default is "ignore". Set to None, if 
        the warnings should be displayed. 
    """

    with warnings.catch_warnings(action=warnings_action):
        # Get known host public keys
        cnopts = pysftp.CnOpts(knownhosts='known_hosts')
        # Set the keys to None (this alternative is a little bit risky in term of security)
        # Do not use it for an untrusted source, it trusts the host without checking the keys
        cnopts.hostkeys = None
        
        # Open an SFTP connection
        connection = pysftp.Connection(host=HOST, username=USER_NAME, password=PWD, port=PORT, cnopts=cnopts)

        # Download files from the server
        for year in range(start_date.year, end_date.year): # Iterate over years
            with connection.cd(f'data/GFED/GFED4/daily/{year}'):
                files = connection.listdir() # Get all files names in directory
                for file in files: # Iterate over files
                    file_day_in_year = int(file.split('_')[-2][-3:]) # Get the day corresponding to the file Ex : In 'GFED4.0_DQ_2015001_BA.hdf' it's 1
                    file_date = date(year, 1, 1) + timedelta(file_day_in_year - 1) # Converting (year, day in year) to complete date (year, month, day)

                    # Generate a local path for the data file
                    local_path = os.path.join(daily_burnt_area_folder, f'daily_burnt_area_{file_date.day}_{file_date.month}_{file_date.year}.hdf')
                    # Check if the data file doesn't exist already and if the date is within the time range specified
                    if not(os.path.isfile(local_path)) and file_date >= start_date and file_date <= end_date:
                        connection.get(remotepath=file, localpath=local_path) # Download the file in the generated local path
        
        connection.close() # Close the connection