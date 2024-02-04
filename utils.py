import numpy as np
import pandas as pd
import requests
import math
import custom_exceptions


def gfed_data_loader(year:int):
    """
    This function generates a "gfed_data.hdf5" file that should be a copy of the GFED
    data file in the GFED database that corresponds to the "year" sent as parameter.
    It does that by requesting the https server of the GFED database for the matching file.
    """
    #checking for year validity
    if year<1997 or year>2016:
         raise custom_exceptions.Gfed_year_out_of_bound_exception(f"Gfed_year_out_of_bound_exception: year {year} is not accepted")
    
    #making the request to the GFED server
    remote_file_name = "GFED4.1s_" + str(year) + ".hdf5"
    print("WAITING FOR RESPONSE FROM GFED ...")
    request = requests.get("https://www.geo.vu.nl/~gwerf/GFED/GFED4/"+remote_file_name)
    #checking for the request status
    if request.status_code != 200:
        raise custom_exceptions.Gfed_request_exception(f"Gfed_request_Exception: request returned with status code = {request.status_code}", request.status_code)
    
    #writing fetched data to the local gfed_data.hdf5 file 
    print("WRITING DATA TO LOCAL FILE ...")
    with open("gfed_data.hdf5","wb") as f:
         f.write(request.content)
    print("DONE.")


def coordinates_selecter(lat_min:float, lat_max:float, lon_min:float, lon_max:float)->np.ndarray:
    """
    This function receives as input a geogrphical span :
        lon_min: longitude min
        lon_max: longitude max
        lat_min: latititude min
        lat_max: latitude max

    and returns the corresponding coordinates (center of the activated cells) in the GFED grid as an np array  
    """
    #getting the x_min and x_max indexes
    x_min = math.floor((lon_min+180)*4)
    x_max = math.floor((lon_max+180)*4)
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


def gfed_portioner(earth_map:np.ndarray, lat_min:float, lat_max:float, lon_min:float, lon_max:float)->pd.DataFrame:
    """
    This function receives as input:
        earth_map: a 720 * 1440 gfed earth map
        lon_min: longitude min
        lon_max: longitude max
        lat_min: latititude min
        lat_max: latitude max
    
    and returns a data frame corresponding to the delimited region:
        y: the latitude cell in the gfed earth map
        x: the longitude cell in the gfed earth map
        Longitude: the longitude of the center of the cell
        Latitude: the latitude of the center of the cell
        Was Burnt: a boolean indicating whether that cell was burnt
        Burnt %: The percentage of that cell that burnt
    """
    #getting the x_min and x_max indexes
    x_min = math.floor((lon_min+180)*4)
    x_max = math.floor((lon_max+180)*4)
    #getting the y_min and y_max indexes
    y_min = math.floor((lat_min+90)*4)
    y_max = math.floor((lat_max+90)*4)
    
    df = pd.DataFrame(
        data = earth_map[719-y_max:719-y_min+1, x_min:x_max+1][::-1],
        index = pd.Index(data=[-90 + i*0.25 + 0.125 for i in range(y_min, y_max+1)], name="Latitude"),
        columns = [-180+i*0.25 + 0.125 for i in range(x_min, x_max+1)]
    )
    
    df = df.stack()
    df.index.set_names(names="Longitude", level=1, inplace=True)
    df = df.reset_index(name="Burnt %")
    df.insert(2,'Was burnt', (df['Burnt %'] != 0).astype(int))
    df.insert(0, 'y', ((90-df['Latitude'])*4).astype(int))
    df.insert(1, 'x', ((df['Longitude']+180)*4).astype(int))
    return df