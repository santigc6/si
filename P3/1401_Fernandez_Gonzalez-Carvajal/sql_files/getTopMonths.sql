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
      orders.orderid,
      DATE_PART('year', orders.orderdate) as year, 
      DATE_PART('month', orders.orderdate) as month, 
      orders.totalamount, 
      SUM(orderdetail.quantity) as quantity
  FROM orders INNER JOIN orderdetail ON (orders.orderid=orderdetail.orderid)
  GROUP BY orders.orderid, year, month, totalamount
  )
  SELECT tablaaux.year, tablaaux.month, SUM(tablaaux.totalamount), SUM(tablaaux.quantity)
  FROM tablaaux
  GROUP BY tablaaux.year, tablaaux.month
  HAVING SUM(tablaaux.totalamount) >= umbralimport OR SUM(tablaaux.quantity) >= umbralprods
  ORDER BY tablaaux.year, tablaaux.month;
END;
$$ LANGUAGE plpgsql;
