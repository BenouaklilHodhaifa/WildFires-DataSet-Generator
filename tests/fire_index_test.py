from utils.fire_index_utils import get_data_with_fire_indexes
import pandas as pd
import numpy as np
from datetime import date

def test_fire_index():
    data = pd.DataFrame({
        'date': [pd.Timestamp('2020-10-01 00:00:00'),
                 pd.Timestamp('2020-10-02 00:00:00'),
                 pd.Timestamp('2020-10-03 00:00:00'),
                 pd.Timestamp('2020-10-04 00:00:00'),
                 pd.Timestamp('2020-10-05 00:00:00')],
        'latitude': [36.125, 36.125, 36.125, 36.125, 36.125],
        'longitude': [1, 1, 1, 1, 1],
        'temperature': [21.48, 20.30, 16.98, 16.39, 18.90],
        'precipitation': [0.00, 0.64, 0.55, 0.22, 0.18],
        'air_humidity': [63.44, 57.00, 62.00, 57.81, 62.06],
        'wind_speed': [4.44, 9.07, 5.80, 4.73, 3.88]
    })

    new_data = get_data_with_fire_indexes(data, date(2020, 10, 1), date(2020, 10, 5), temp_meteo_folder='data/meteo')
    
    # Check for missing columns
    for c in list(data.columns):
        assert(c in list(new_data.columns))

    # Check for indices
    tolerence = 10**-5
    assert(np.allclose(new_data['ffmc'].to_numpy(), np.array([85.260025, 85.536819, 84.728874, 85.287865, 85.335670], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['dmc'].to_numpy(), np.array([7.250835, 8.645123, 9.686125, 10.804196, 11.953930], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['dc'].to_numpy(), np.array([19.570400, 23.928400, 27.688801, 31.343000, 35.449001], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['isi'].to_numpy(), np.array([4.8875294, 11.763453, 5.814761, 5.1714153, 4.4618955], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['bui'].to_numpy(), np.array([7.5284457, 9.084693, 10.334332, 11.606363, 12.971990], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['fwi'].to_numpy(), np.array([4.5548725, 11.108752, 6.377234, 6.064647, 5.5898585], dtype=np.float32), atol=tolerence, rtol=0))


def test_fire_index_splitted():
    data = pd.DataFrame({
        'date': [pd.Timestamp('2020-10-01 00:00:00'),
                 pd.Timestamp('2020-10-02 00:00:00'),
                 pd.Timestamp('2020-10-03 00:00:00'),
                 pd.Timestamp('2020-10-04 00:00:00'),
                 pd.Timestamp('2020-10-05 00:00:00')],
        'latitude': [36.125, 36.125, 36.125, 36.125, 36.125],
        'longitude': [1, 1, 1, 1, 1],
        'temperature': [21.48, 20.30, 16.98, 16.39, 18.90],
        'precipitation': [0.00, 0.64, 0.55, 0.22, 0.18],
        'air_humidity': [63.44, 57.00, 62.00, 57.81, 62.06],
        'wind_speed': [4.44, 9.07, 5.80, 4.73, 3.88]
    })

    new_data = get_data_with_fire_indexes(data, date(2020, 10, 1), date(2020, 10, 5), date_interval_size=2, temp_meteo_folder='data/meteo')
    print(new_data.to_numpy())
    # Check for missing columns
    for c in list(data.columns):
        assert(c in list(new_data.columns))

    # Check for indices
    tolerence = 10**-5
    assert(np.allclose(new_data['ffmc'].to_numpy(), np.array([85.26002502441406, 85.53681945800781, 84.59232330322266, 85.2508544921875, 85.1241683959961], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['dmc'].to_numpy(), np.array([7.250834941864014, 8.645122528076172, 7.041003227233887, 8.159073829650879, 7.149733543395996], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['dc'].to_numpy(), np.array([19.57040023803711, 23.92840003967285, 18.760400772094727, 22.414600372314453, 19.106000900268555], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['isi'].to_numpy(), np.array([4.887529373168945, 11.763452529907227, 5.707616806030273, 5.144996643066406, 4.333328723907471], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['bui'].to_numpy(), np.array([7.528445720672607, 9.08469295501709, 7.265207290649414, 8.543453216552734, 7.387862682342529], dtype=np.float32), atol=tolerence, rtol=0))
    assert(np.allclose(new_data['fwi'].to_numpy(), np.array([4.554872512817383, 11.108752250671387, 5.244157791137695, 5.129981994628906, 3.9604170322418213], dtype=np.float32), atol=tolerence, rtol=0))