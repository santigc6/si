CREATE OR REPLACE FUNCTION getTopMonths (umbralprods integer, umbralimport numeric)
  RETURNS TABLE (
    year double precision,
    month double precision,
    price numeric,
    products bigint
) as $$
BEGIN
  RETURN QUERY
  WITH tablaaux AS (
    SELECT 
	    DATE_PART('year', orders.orderdate) as year, 
	    DATE_PART('month', orders.orderdate) as month, 
	    orders.totalamount, 
	    orderdetail.quantity
  FROM orders INNER JOIN orderdetail ON (orders.orderid=orderdetail.orderid)
	  INNER JOIN products ON (products.prod_id=orderdetail.prod_id)
  ORDER BY year, month
  )
  SELECT tablaaux.year, tablaaux.month, SUM(tablaaux.totalamount), SUM(tablaaux.quantity)
  FROM tablaaux
  GROUP BY tablaaux.year, tablaaux.month
  HAVING SUM(tablaaux.totalamount) >= umbralimport OR SUM(tablaaux.quantity) >= umbralprods
  ORDER BY tablaaux.year, tablaaux.month;
END;
$$ LANGUAGE plpgsql;
