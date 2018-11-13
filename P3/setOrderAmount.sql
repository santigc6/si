----------------------------------------------------------------------
-- Una vez se disponga de esta información, realizar un procedimiento
-- almacenado, setOrderAmount, que complete las columnas 'netamount'
-- (suma de los precios de las películas del pedido) y 'totalamount'
-- ('netamount' más impuestos) de la tabla 'orders' cuando éstas no
-- contengan ningún valor. Invocadlo para realizar una carga inicial.
----------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE setOrderAmount ()
LANGUAGE SQL
AS $$
UPDATE
    orders;
SET
    netamount = SUM(products.price)
    totalamount = netamount + tax
FROM
    products
    RIGHT OUTER JOIN
    orderdetail
    ON products.prod_id = orderdetail.prod_id
WHERE
    orders.orderid = orderdetail.orderid;
$$;
