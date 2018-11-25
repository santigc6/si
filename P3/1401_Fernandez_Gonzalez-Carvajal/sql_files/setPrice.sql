----------------------------------------------------------------------
-- Sabiendo que los precios de las películas se han ido incrementando
-- un 2% anualmente, elaborar la consulta setPrice.sql que complete
-- la columna 'price' de la tabla 'orderdetail', sabiendo que el
-- precio actual es el de la tabla 'products'.
----------------------------------------------------------------------

UPDATE
    orderdetail
SET
    price = ROUND(products.price / POWER(1.02, date_part('year', current_date) - imdb_movies.year))
FROM
    products INNER JOIN imdb_movies ON imdb_movies.movieid = products.movieid
WHERE
    products.prod_id = orderdetail.prod_id;

