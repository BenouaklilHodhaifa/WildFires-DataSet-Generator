SELECT d.id, d.name, d.nbr_rows, d.fwi_backtrack_size, d.created_at, COUNT(*)*100/d.nbr_rows ratio FROM wildfires_data w, datasets d WHERE 
(latitude BETWEEN :lat_min AND :lat_max) 
AND (longitude BETWEEN :lng_min AND :lng_max) 
AND (date BETWEEN :start_date AND :end_date)
AND (w.dataset_id = d.id)
ORDER BY ratio DESC;