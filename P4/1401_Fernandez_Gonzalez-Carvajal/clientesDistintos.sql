-----------------------------------------------------------------------------------------
-- Autores: Adrian Fernandez Amador y Santiago González- Carvajal Centenera
-----------------------------------------------------------------------------------------

-- Query inicial
SELECT 
  COUNT(DISTINCT customers.customerid)
FROM 
  customers 
  INNER JOIN orders ON (
    customers.customerid=orders.customerid)
WHERE 
  orders.totalamount > 100 AND 
  EXTRACT(year from orders.orderdate) = 2015 AND
  EXTRACT(month from orders.orderdate) = 4;

-----------------------------------------------------------------------------------------

-- Query en forma de funcion
CREATE OR REPLACE FUNCTION clientesDistintos (importe numeric, yearin integer, monthin integer)
  RETURNS TABLE (
    n_clientes bigint
  ) as $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(DISTINCT customers.customerid)
	FROM 
	  customers 
	  INNER JOIN orders ON (
		customers.customerid=orders.customerid)
	WHERE 
	  orders.totalamount > importe AND 
	  EXTRACT(year from orders.orderdate) = yearin AND
	  EXTRACT(month from orders.orderdate) = monthin;
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------------------------------------------------

-- Indice en orders.totalamount
CREATE INDEX idx_amount ON orders(totalamount);

-- Indices en orders.orderdate
CREATE INDEX idx_year ON orders(EXTRACT(year from orders.orderdate));
CREATE INDEX idx_month ON orders(EXTRACT(month from orders.orderdate));
