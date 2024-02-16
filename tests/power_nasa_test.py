from utils.power_nasa_utils import *
import numpy as np

def test_power_nasa():
    actual = get_data(date(2015, 7, 10), date(2015, 7, 13), -7.25, -7.25,
                        12.875, 12.875, show_progress=True).to_numpy()

    expected = np.array([['20150710', -7.125, 12.875, 24.36, 0.0, 76.12, 2.48],
       ['20150711', -7.125, 12.875, 24.19, 0.0, 77.5, 2.8],
       ['20150712', -7.125, 12.875, 23.9, 0.0, 76.5, 2.79],
       ['20150713', -7.125, 12.875, 23.61, 0.0, 76.31, 2.99]], dtype=np.object_)
    
    assert((actual == expected).all())