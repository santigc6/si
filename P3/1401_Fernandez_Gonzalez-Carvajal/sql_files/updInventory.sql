----------------------------------------------------------------------
-- Realizar un trigger, updInventory, que actualice la tablas
-- 'inventory' y 'orders' cuando se finalice la compra. El trigger
-- también deberá crear una alerta en una nueva tabla llamada
-- 'alertas' si la cantidad en stock llega a cero. Realizar los
-- cambios necesarios en la base de datos para incluir dicha tabla,
-- incorporándolos al script actualiza.sql.
----------------------------------------------------------------------
CREATE OR REPLACE FUNCTION updInventoryAux ()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.stock < 0 THEN
        RAISE EXCEPTION 'Intentando modificar stock a negativo en producto con id %.', OLD.prod_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--DROP TRIGGER t_updInventoryAux on inventory;

CREATE TRIGGER t_updInventoryAux BEFORE UPDATE ON inventory
FOR EACH ROW EXECUTE PROCEDURE updInventoryAux();

-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION updInventory ()
RETURNS TRIGGER AS $$
DECLARE
	product_id integer := (select MAX(products.prod_id)
			FROM
            orderdetail INNER JOIN products ON orderdetail.prod_id = products.prod_id INNER JOIN inventory ON inventory.prod_id=products.prod_id
        WHERE
            OLD.orderid = orderdetail.orderid);
BEGIN

    IF NEW.status = 'Paid' THEN

        UPDATE
            inventory
        SET
            stock = stock - orderdetail.quantity,
            sales = sales + orderdetail.quantity
        FROM
            orderdetail INNER JOIN products ON orderdetail.prod_id = products.prod_id
        WHERE
            OLD.orderid = orderdetail.orderid AND
            inventory.prod_id = products.prod_id;

    END IF;

    RETURN NEW;
EXCEPTION WHEN OTHERS THEN 
	INSERT INTO alertas (prod_id, notice, stamp)
      VALUES (product_id, 'Stock insuficiente. Imposible realizar la compra.', current_timestamp);
      RETURN OLD;


END;
$$ LANGUAGE plpgsql;

--DROP TRIGGER t_updInventory on orders;

CREATE TRIGGER t_updInventory BEFORE UPDATE OF status ON orders
FOR EACH ROW EXECUTE PROCEDURE updInventory();
