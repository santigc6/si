CREATE OR REPLACE FUNCTION getTopVentas (anio integer)
  RETURNS TABLE (
    year double precision,
    film character varying(255),
    sales bigint
) as $$
BEGIN
  RETURN QUERY
  WITH tablaaux AS (
  SELECT
    DATE_PART('year', orders.orderdate) as anyo,
    imdb_movies.movietitle as titulo,
    SUM(orderdetail.quantity) as sales
  FROM 
    orders
    INNER JOIN orderdetail ON (
      orders.orderid=orderdetail.orderid)
	  INNER JOIN products ON (
	    products.prod_id=orderdetail.prod_id)
	  INNER JOIN imdb_movies ON (
	    imdb_movies.movieid=products.movieid)
  GROUP BY imdb_movies.movietitle, anyo
  )
  SELECT
    top.anyo,
    top.titulo,
    top.sales
  FROM (
	  SELECT
	    *,
	    ROW_NUMBER() OVER (
		    PARTITION BY tablaaux.anyo ORDER BY tablaaux.sales DESC) as rowid
	  FROM
	    tablaaux
  ) as top
  WHERE
    rowid < 2
    and top.anyo >= anio
  ORDER BY top.anyo;
END;
$$ LANGUAGE plpgsql;
