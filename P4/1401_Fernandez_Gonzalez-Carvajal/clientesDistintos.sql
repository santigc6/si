-- Autores: Adrian Fernandez Amador y Santiago González- Carvajal Centenera
SELECT DISTINCT customers.firstname
FROM customers INNER JOIN orders ON (customers.customerid=orders.customerid)
WHERE orders.totalamount > 100 AND TO_CHAR(orders.orderdate, 'YYYYMM') = '201504';