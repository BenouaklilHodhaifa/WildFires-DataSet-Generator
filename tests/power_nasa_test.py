from utils.power_nasa_utils import *
import numpy as np
import pandas as pd

def test_power_nasa():
   actual = get_data(date(2015, 7, 10), date(2015, 7, 13), -7.25, -7.25,
                     12.875, 12.875, show_progress=True).to_numpy()
   
   expected = np.array([[pd.Timestamp('2015-07-10 00:00:00'), -7.125, 12.875, 24.36, 0.0, 76.12, 2.48],
      [pd.Timestamp('2015-07-11 00:00:00'), -7.125, 12.875, 24.19, 0.0, 77.5, 2.8],
      [pd.Timestamp('2015-07-12 00:00:00'), -7.125, 12.875, 23.9, 0.0, 76.5, 2.79],
      [pd.Timestamp('2015-07-13 00:00:00'), -7.125, 12.875, 23.61, 0.0, 76.31, 2.99]])
   
   assert((actual == expected).all())