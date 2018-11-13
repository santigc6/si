CREATE OR REPLACE FUNCTION getTopVentas (anio integer)
  RETURNS TABLE (
    year integer,
    film character varying(255),
    sales integer
) as $$
BEGIN
  RETURN QUERY
  SELECT DISTINCT imdb_movies.year, imdb_movies.movietitle, inventory.sales
  FROM (inventory INNER JOIN products ON (inventory.prod_id=products.prod_id))
  INNER JOIN imdb_movies ON (products.movieid=imdb_movies.movieid)
  WHERE year >= anio
  ORDER BY year;
END;
$$ LANGUAGE plpgsql;
