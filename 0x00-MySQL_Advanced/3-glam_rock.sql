-- Use the appropriate database
-- Select bands with Glam rock as their main style, calculating lifespan and ordering by it
SELECT
    band_name,
    YEAR(MAX(year_end)) - YEAR(MIN(year_start)) AS lifespan
FROM bands
WHERE style = 'Glam rock'
GROUP BY band_name
ORDER BY lifespan DESC;