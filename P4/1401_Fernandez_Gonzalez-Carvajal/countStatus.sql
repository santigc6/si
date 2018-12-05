-----------------------------------------------------------------------------------------
-- Autores: Adrián Fernández Amador y Santiago González-Carvajal Centenera
-----------------------------------------------------------------------------------------

-----------------------------------------------------------------------------------------
-- Estudiar, explicar y comparar la planificación de las dos consultas
-- sobre una base de datos limpia (recién creada y cargada de datos),
-- tras crear un índice
-- y tras generar las estadísticas con la sentencia ANALYZE.
-----------------------------------------------------------------------------------------

-- Primera query
SELECT COUNT(*)
FROM orders
WHERE status IS NULL;

-- Segunda query
SELECT COUNT(*)
FROM orders
WHERE status ='Shipped';

-- Indice en orders.status
CREATE INDEX idx_status ON orders(status);

-- Generacion de estadisticas
ANALYZE VERBOSE orders;

-----------------------------------------------------------------------------------------
-- Comparar también con la planificación de las siguientes consultas,
-- una vez generadas las estadísticas:
-----------------------------------------------------------------------------------------

-- Tercera query
SELECT COUNT(*)
FROM orders
WHERE status ='Paid';

-- Cuarta query
SELECT COUNT(*)
FROM orders
WHERE status ='Processed';