CREATE OR REPLACE FUNCTION getTopVentas (anio integer)
  RETURNS TABLE (
    year double precision,
    film character varying(255),
    sales integer
) as $$
BEGIN
  RETURN QUERY
  WITH tablaaux AS (
  SELECT DATE_PART('year', orders.orderdate) as year, imdb_movies.movietitle, inventory.sales
  FROM orders INNER JOIN orderdetail ON (orders.orderid=orderdetail.orderid)
	  INNER JOIN products ON (products.prod_id=orderdetail.prod_id)
	  INNER JOIN inventory ON (products.prod_id=inventory.prod_id)
	  INNER JOIN imdb_movies ON (imdb_movies.movieid=products.prod_id)
  ORDER BY year
  )
  SELECT top.year, top.movietitle, top.sales
  FROM (
	  SELECT *, ROW_NUMBER() OVER (
		  PARTITION BY tablaaux.year ORDER BY tablaaux.sales DESC) as rowid
	  FROM tablaaux
  ) as top
  WHERE rowid < 2 and top.year >= anio
  ORDER BY top.year;
END;
$$ LANGUAGE plpgsql;
