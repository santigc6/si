# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine
from sqlalchemy.sql import text

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()

def getListaCliMes(db_conn, mes, anio, iumbral, iintervalo, use_prepare, break0, niter):    
    if use_prepare:
      # code for prepare
      db_conn.execute("PREPARE cons AS SELECT\
        COUNT(DISTINCT customers.customerid) AS cc\
      FROM\
        customers\
        INNER JOIN orders ON (\
          customers.customerid=orders.customerid)\
      WHERE\
        orders.totalamount > $1 AND\
        EXTRACT(year from orders.orderdate) = $2 AND\
        EXTRACT(month from orders.orderdate) = $3")
  
    # Array con resultados de la consulta para cada umbral
    dbr=[]

    for ii in range(niter):
        if use_prepare:
          result = db_conn.execute("EXECUTE cons (%s, %s, %s)", (iumbral, int(anio), int(mes)))
          res = result.fetchone()
        else:
          result = db_conn.execute("SELECT\
            COUNT(DISTINCT customers.customerid) AS cc\
          FROM\
            customers\
            INNER JOIN orders ON (\
              customers.customerid=orders.customerid)\
          WHERE\
            orders.totalamount > "+ str(iumbral) +" AND\
            EXTRACT(year from orders.orderdate) = "+ str(anio) +" AND\
            EXTRACT(month from orders.orderdate) = "+ str(mes))

          res = result.fetchone()

        # Guardar resultado de la query
        dbr.append({"umbral":iumbral,"contador":res['cc']})

        if break0 and res['cc'] == 0:
          break

        # Actualizacion de umbral
        iumbral = iumbral + iintervalo
    
    if use_prepare:            
      db_conn.execute("DEALLOCATE cons")

    return dbr

def getMovies(anio):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select movietitle from imdb_movies where year = '" + anio + "'"
    resultproxy=db_conn.execute(query)

    a = []
    for rowproxy in resultproxy:
        d={}
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d[tup[0]] = tup[1]
        a.append(d)
        
    resultproxy.close()  
    
    db_conn.close()  
    
    return a
    
def getCustomer(username, password):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select * from customers where username='" + username + "' and password='" + password + "'"
    res=db_conn.execute(query).first()
    
    db_conn.close()  

    if res is None:
        return None
    else:
        return {'firstname': res['firstname'], 'lastname': res['lastname']}
    
def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):
    # Array de trazas a mostrar en la página
    dbr=[]

    # customerid = request.form["customerid"]
    # bSQL       = request.form["txnSQL"]
    # bCommit = "bCommit" in request.form
    # bFallo  = "bFallo"  in request.form
    # duerme  = request.form["duerme"]

    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()
    
    try:

        db_conn = db_engine.connect()

        if bSQL == 1:

            if bFallo == False:
                query = text("BEGIN;\
                SAVEPOINT save;\
                DELETE\
                FROM orderdetail\
                USING customers INNER JOIN orders ON customers.customerid = orders.customerid\
                WHERE orders.orderid = orderdetail.orderid AND customers.customerid = :cid;\
                DELETE\
                FROM orders\
                USING customers\
                WHERE customers.customerid = orders.customerid AND customers.customerid = :cid;\
                DELETE\
                FROM customers\
                WHERE customers.customerid = :cid;")
            else:
                if bCommit == True:
                    query = text("BEGIN;\
                    DELETE\
                    FROM orderdetail\
                    USING customers INNER JOIN orders ON customers.customerid = orders.customerid\
                    WHERE orders.orderid = orderdetail.orderid AND customers.customerid = :cid;\
                    COMMIT;\
                    BEGIN;\
                    SAVEPOINT save;\
                    DELETE\
                    FROM customers\
                    WHERE customers.customerid = :cid;\
                    DELETE\
                    FROM orders\
                    USING customers\
                    WHERE customers.customerid = orders.customerid AND customers.customerid = :cid;")
                else:
                    query = text("BEGIN;\
                    DELETE\
                    FROM orderdetail\
                    USING customers INNER JOIN orders ON customers.customerid = orders.customerid\
                    WHERE orders.orderid = orderdetail.orderid AND customers.customerid = :cid;\
                    SAVEPOINT save;\
                    DELETE\
                    FROM customers\
                    WHERE customers.customerid = :cid;\
                    DELETE\
                    FROM orders\
                    USING customers\
                    WHERE customers.customerid = orders.customerid AND customers.customerid = :cid;")

            res = db_conn.execute(query, cid=customerid)
            dbr.append(res)

        else:

            db_trans = db_conn.begin()

            if bFallo == False:
                customers = select()
                Customers.query.filter_by(username='peter').first()
                query = text("DELETE\
                FROM orderdetail\
                USING customers INNER JOIN orders ON customers.customerid = orders.customerid\
                WHERE orders.orderid = orderdetail.orderid AND customers.customerid = :cid;\
                DELETE\
                FROM orders\
                USING customers\
                WHERE customers.customerid = orders.customerid AND customers.customerid = :cid;\
                DELETE\
                FROM customers\
                WHERE customers.customerid = :cid;")
                res = db_conn.execute(query, cid=customerid)
                dbr.append(res)
            else:
                if bCommit == True:
                    query = text("DELETE\
                    FROM orderdetail\
                    USING customers INNER JOIN orders ON customers.customerid = orders.customerid\
                    WHERE orders.orderid = orderdetail.orderid AND customers.customerid = :cid;")
                    res = db_conn.execute(query, cid=customerid)
                    dbr.append(res)

                    db_trans.commit()
                    db_trans.begin_nested()

                    text("DELETE\
                    FROM customers\
                    WHERE customers.customerid = :cid;\
                    DELETE\
                    FROM orders\
                    USING customers\
                    WHERE customers.customerid = orders.customerid AND customers.customerid = :cid;")
                    res = db_conn.execute(query, cid=customerid)
                    dbr.append(res)
                else:
                    query = text("DELETE\
                    FROM orderdetail\
                    USING customers INNER JOIN orders ON customers.customerid = orders.customerid\
                    WHERE orders.orderid = orderdetail.orderid AND customers.customerid = :cid;")
                    res = db_conn.execute(query, cid=customerid)
                    dbr.append(res)

                    db_trans.begin_nested()

                    query = text("DELETE\
                    FROM customers\
                    WHERE customers.customerid = :cid;\
                    DELETE\
                    FROM orders\
                    USING customers\
                    WHERE customers.customerid = orders.customerid AND customers.customerid = :cid;")
                    res = db_conn.execute(query, cid=customerid)
                    dbr.append(res)


    except Exception as e:
        # TODO: deshacer en caso de error
        if bSQL == 1:
            query = text("ROLLBACK TO SAVEPOINT save;\
            COMMIT;")
            res = db_conn.execute(query)
            dbr.append(res)
        else:
            res = db_trans.rollback()
            dbr.append(res)
            res = db_trans.commit()
            dbr.append(res)

    else:
        # TODO: confirmar cambios si todo va bien
        if bSQL == 1:
            query = text("COMMIT;")
            res = db_conn.execute(query)
            dbr.append(res)
        else:
            res = db_trans.commit()
            dbr.append(res)

    db_conn.close()

    return dbr

