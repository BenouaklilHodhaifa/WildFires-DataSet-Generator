SELECT * FROM wildfires_data WHERE 
(latitude BETWEEN :lat_min AND :lat_max) 
AND (longitude BETWEEN :lng_min AND :lng_max) 
AND (date BETWEEN :start_date AND :end_date);