from utils.fire_index_utils import get_data_with_fire_indexes
import pandas as pd
import numpy as np
import logging

# Ignore logs from third-party modules (Change this line if you want to show all logs)
logging.getLogger().setLevel(logging.CRITICAL)

def test_fire_index():
    data = pd.DataFrame({
        'date': ['20201001', '20201002', '20201003', '20201004', '20201005'],
        'latitude': [36.125, 36.125, 36.125, 36.125, 36.125],
        'longitude': [1, 1, 1, 1, 1],
        'temperature': [21.48, 20.30, 16.98, 16.39, 18.90],
        'precipitation': [0.00, 0.64, 0.55, 0.22, 0.18],
        'air_humidity': [63.44, 57.00, 62.00, 57.81, 62.06],
        'wind_speed': [4.44, 9.07, 5.80, 4.73, 3.88]
    })

    new_data = get_data_with_fire_indexes(data, temp_meteo_folder='data/meteo')
    
    # Check for missing columns
    for c in list(data.columns):
        assert(c in list(new_data.columns))

    print(new_data)
    # Check for indices
    assert((new_data['ffmc'].to_numpy() == np.array([85.260025, 85.536819, 84.728874, 85.287865, 85.335670], dtype=np.float32)).all())
    assert((new_data['dmc'].to_numpy() == np.array([7.250835, 8.645123, 9.686125, 10.804196, 11.953930], dtype=np.float32)).all())
    assert((new_data['dc'].to_numpy() == np.array([19.570400, 23.928400, 27.688801, 31.343000, 35.449001], dtype=np.float32)).all())
    assert((new_data['isi'].to_numpy() == np.array([4.8875294, 11.763453, 5.814761, 5.1714153, 4.4618955], dtype=np.float32)).all())
    assert((new_data['bui'].to_numpy() == np.array([7.528446, 9.084693, 10.334332, 11.606363, 12.971990], dtype=np.float32)).all())
    assert((new_data['fwi'].to_numpy() == np.array([4.554873, 11.108752, 6.377234, 6.064647, 5.589859], dtype=np.float32)).all())