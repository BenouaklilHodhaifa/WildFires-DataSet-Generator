from utils.gfed_utils import *
from datetime import date
import numpy as np

def test_gfed_emissions():
    actual = get_gfed_emissions_data_for_range(date(2015, 7, 10), date(2015, 7, 13), -7.25, -7.25,
                                           12.875, 12.875, gfed_files_folder='data/gfed').to_numpy()
    
    expected = np.array([[-7.125, 12.875, pd.Timestamp('2015-07-10 00:00:00'),
        2.34432053565979],
       [-7.125, 12.875, pd.Timestamp('2015-07-11 00:00:00'),
        1.4065908193588257],
       [-7.125, 12.875, pd.Timestamp('2015-07-12 00:00:00'),
        1.600609540939331],
       [-7.125, 12.875, pd.Timestamp('2015-07-13 00:00:00'),
        0.468868613243103]])
    
    assert((actual == expected).all())