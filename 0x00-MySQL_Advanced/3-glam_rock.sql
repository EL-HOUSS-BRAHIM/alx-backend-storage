-- Use the appropriate database
-- Select bands with Glam rock as their main style, calculating lifespan and ordering by it


SELECT band_name, 
    (YEAR('2022-01-01') - SUBSTRING_INDEX(lifespan, '-', 1)) AS lifespan
FROM metal_bands
WHERE style LIKE '%Glam rock%'
ORDER BY lifespan DESC;