from utils.maryland_fuoco_utils import *
import pandas as pd
import numpy as np

def test_maryland_fuoco():
    actual = get_daily_burned_area_data(date(2015, 7, 10), date(2015, 7, 13), -7.25, -7.25,
                                           12.875, 12.875, daily_burned_area_folder='data/fuoco').to_numpy()
    
    expected = np.array([[-7.125, 12.875, pd.Timestamp('2015-07-10 00:00:00'), 19292],
       [-7.125, 12.875, pd.Timestamp('2015-07-11 00:00:00'), 160770],
       [-7.125, 12.875, pd.Timestamp('2015-07-12 00:00:00'), 6431],
       [-7.125, 12.875, pd.Timestamp('2015-07-13 00:00:00'), 45016]])
    
    assert((actual == expected).all())