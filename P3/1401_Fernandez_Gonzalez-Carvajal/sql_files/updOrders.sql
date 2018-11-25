CREATE OR REPLACE FUNCTION updOrders ()
  RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN --It is an insert into
    UPDATE
      orders
    SET
      netamount = (netamount + (NEW.price * NEW.quantity)),
      totalamount = ROUND((netamount + (NEW.price * NEW.quantity)) * (1 + (tax / 100)))
    WHERE
      orders.orderid=NEW.orderid;
  ELSE --It is a delete
    UPDATE
      orders
    SET
      netamount = (netamount - (OLD.price * OLD.quantity)),
      totalamount = ROUND((netamount - (OLD.price * OLD.quantity)) * (1 + (tax / 100)))
    WHERE
      orders.orderid=OLD.orderid;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--DROP TRIGGER t_updOrders on orderdetail;

CREATE TRIGGER t_updOrders AFTER INSERT OR DELETE ON orderdetail
FOR EACH ROW EXECUTE PROCEDURE updOrders();
