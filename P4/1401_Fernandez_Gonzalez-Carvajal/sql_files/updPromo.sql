ALTER TABLE
	customers 
ADD COLUMN 
	promo numeric;

CREATE OR REPLACE FUNCTION updPromo()
  RETURNS TRIGGER AS $$
BEGIN
  PERFORM pg_sleep(3);

  UPDATE
    orders
  SET
    netamount = netamount - (netamount * NEW.promo),
    totalamount = totalamount - (totalamount * NEW.promo)
  WHERE
    orders.customerid = NEW.customerid;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--DROP TRIGGER t_updPromo ON customers

CREATE TRIGGER t_updPromo AFTER UPDATE OF promo ON customers
FOR EACH ROW EXECUTE PROCEDURE updPromo();