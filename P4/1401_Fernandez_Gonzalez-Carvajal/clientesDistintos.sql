-----------------------------------------------------------------------------------------
-- Autores: Adrian Fernandez Amador y Santiago González- Carvajal Centenera
-----------------------------------------------------------------------------------------

-- Query inicial
SELECT COUNT(DISTINCT customers.customerid)
FROM customers INNER JOIN orders ON (customers.customerid=orders.customerid)
WHERE orders.totalamount > 100 AND TO_CHAR(orders.orderdate, 'YYYYMM') = '201504';

-----------------------------------------------------------------------------------------

-- Query en forma de funcion
CREATE OR REPLACE FUNCTION clientesDistintos (importe numeric, fecha char(6))
  RETURNS TABLE (
    n_clientes integer
  ) as $$
BEGIN
  RETURN QUERY
  SELECT COUNT(DISTINCT customers.customerid)
  FROM customers INNER JOIN orders ON (customers.customerid=orders.customerid)
  WHERE orders.totalamount > importe AND TO_CHAR(orders.orderdate, 'YYYYMM') = fecha;
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------------------------------------------------

-- Borrar la primary key de customers
ALTER TABLE customers DROP CONSTRAINT customers_pkey CASCADE;

-- Indice en orders.totalamount
CREATE INDEX idx_totalamount_orders ON orders(totalamount);

-- Indice en orders.orderdate
CREATE INDEX idx_orderdate_orders ON orders(orderdate);
