INSERT IGNORE INTO wildfires_data 
(latitude, longitude, date, temperature, precipitation, air_humidity, wind_speed, ffmc, dmc, 
dc, isi, bui, fwi, burned_area, emissions, burnt, dataset_id) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 
%s, %s, %s, %s, %s, %s, %s, %s);