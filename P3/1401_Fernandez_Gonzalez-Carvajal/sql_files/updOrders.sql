CREATE OR REPLACE FUNCTION updOrders ()
  RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN --It is an insert into
    UPDATE orders
    SET netamount = (netamount + (NEW.price * NEW.quantity)),
        totalamount = (totalamount + (NEW.price * NEW.quantity))
    WHERE orders.orderid=NEW.orderid;
  ELSE --It is a delete
    UPDATE orders
    SET netamount = (netamount - (OLD.price * OLD.quantity)),
        totalamount = (totalamount - (OLD.price * OLD.quantity))
    WHERE orders.orderid=OLD.orderid;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--DROP TRIGGER t_updOrders on orderdetail;

CREATE TRIGGER t_updOrders AFTER INSERT OR DELETE ON orderdetail
FOR EACH ROW EXECUTE PROCEDURE updOrders();
