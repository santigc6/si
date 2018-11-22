----------------------------------------------------------------------
-- Una vez se disponga de esta información, realizar un procedimiento
-- almacenado, setOrderAmount, que complete las columnas 'netamount'
-- (suma de los precios de las películas del pedido) y 'totalamount'
-- ('netamount' más impuestos) de la tabla 'orders' cuando éstas no
-- contengan ningún valor. Invocadlo para realizar una carga inicial.
----------------------------------------------------------------------

CREATE OR REPLACE FUNCTION setOrderAmount ()
    RETURNS void
AS $$
BEGIN
    WITH total AS (
        SELECT orders.orderid AS id, SUM(products.price) AS suma
        FROM orders INNER JOIN orderdetail ON orders.orderid = orderdetail.orderid
            INNER JOIN products ON products.prod_id = orderdetail.prod_id
        GROUP BY orders.orderid)
    UPDATE
        orders
    SET
        netamount = total.suma,
        totalamount = ROUND(total.suma * (1 + (tax / 100)))
    FROM
        total
    WHERE
        orders.orderid = total.id AND
        orders.netamount IS NULL;
END;
$$ LANGUAGE plpgsql;
