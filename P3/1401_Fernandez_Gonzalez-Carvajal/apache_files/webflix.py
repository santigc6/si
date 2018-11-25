from flask import Flask, render_template, json, url_for, request, redirect, session, make_response
import sqlalchemy
from sqlalchemy.sql import text
import os
import sys
import md5
import random
import datetime

# We link the app
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# We link the database
db_route = "postgres://alumnodb:alumnodb@localhost:5432/si1"
db = sqlalchemy.create_engine(db_route)

def addToCartAux(film):
  if 'user' in session and session['generatedOrder']==False:
    # We get the current orderid and update it
    results = db.execute("SELECT MAX(orders.orderid) FROM orders")
    id_ord = results.fetchall()[0][0]
    id_ord += 1
    session['orderid']=str(id_ord) # orderid to use later
    session['generatedOrder']=True
    session.modified=True
    
    consult="INSERT INTO orders(orderid, orderdate, customerid, netamount, tax, totalamount, status)\
    VALUES ("+str(id_ord)+", CURRENT_DATE, "+session['userid']+", 0, 15, 0, NULL)"
    db.execute(consult)
  
  # Triggers do the rest of the job
  if 'user' in session:
    consult="SELECT products.prod_id, products.price\
    FROM products\
    WHERE products.movieid="+film
    res = db.execute(consult)
    aux = res.fetchall()[0]
    prodid = aux[0]
    priceFilm = aux[1]

    consult="INSERT INTO orderdetail(orderid, prod_id, price, quantity)\
    VALUES ("+session['orderid']+", "+str(prodid)+", "+str(priceFilm)+", 1)"
    db.execute(consult)

@app.route('/')
@app.route('/index')
def index():
  SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

  users_path = os.path.join(SITE_ROOT, 'usuarios')
  if os.path.exists(users_path) == False: # If users' directory doesnt exist we create it
    oldmask = os.umask(000)
    os.mkdir(users_path, 0777)
    os.umask(oldmask)

  json_data = {}
  json_data['peliculas'] = []

  query_ini = "SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price\
  FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
  INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
  INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
  INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
  INNER JOIN products ON imdb_movies.movieid = products.movieid\
  LIMIT 100"

  conn_ini = db.connect()
  res_ini = conn_ini.execute(query_ini)
  chunk = res_ini.fetchall()
  for row in chunk:
    pelicula = {}
    id = row['movieid']
    pelicula['id'] = id
    pelicula['titulo'] = row['movietitle']
    pelicula['categoria'] = row['name_genre']
    pelicula['director'] = row['directorname']
    pelicula['actores'] = []
    pelicula['anno'] = row['year']
    pelicula['precio'] = row['price']
    pelicula['poster'] = "goldfinger.jpg" # No tenemos las fotos en la base de datos

    query_act = "SELECT DISTINCT imdb_actors.actorname\
    FROM imdb_movies INNER JOIN imdb_actormovies ON imdb_movies.movieid = imdb_actormovies.movieid\
    INNER JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid\
    WHERE imdb_movies.movieid = " + "'" + str(id) + "'"

    conn_act = db.connect()
    res_act = conn_act.execute(query_act)
    actors = res_act.fetchall()
    for actor in actors:
      pelicula['actores'].append(actor['actorname'])

    json_data['peliculas'].append(pelicula)

  
  json_data['categorias'] = []

  query_cats = "SELECT DISTINCT genres.name_genre\
  FROM genres"

  conn_cats = db.connect()
  res_cats = conn_cats.execute(query_cats)
  cats = res_cats.fetchall()
  for cat in cats:
    json_data['categorias'].append(cat['name_genre'])
  
  if 'user' in session:
    json_data['user'] = session['user']
  
  topventasaux = db.execute("SELECT * FROM getTopVentasForIndex(2016)")
  topventas = topventasaux.fetchall()

  json_data['showTop'] = True
  json_data['topVentas']={
    topventas[0][3]: [int(topventas[0][0]), topventas[0][1], topventas[0][2]],
    topventas[1][3]: [int(topventas[1][0]), topventas[1][1], topventas[1][2]],
    topventas[2][3]: [int(topventas[2][0]), topventas[2][1], topventas[2][2]]
  }

  return render_template('index.html', **json_data)

@app.route('/details/<string:pelicula>')
def details(pelicula):
  id = int(pelicula)

  query_ini = text("SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price\
  FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
  INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
  INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
  INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
  INNER JOIN products ON imdb_movies.movieid = products.movieid\
  WHERE imdb_movies.movieid = :ide ")

  conn_ini = db.connect()
  res_ini = conn_ini.execute(query_ini, ide=id)
  row = res_ini.fetchone()

  pelicula = {}
  pelicula['id'] = id
  pelicula['titulo'] = row['movietitle']
  pelicula['categoria'] = row['name_genre']
  pelicula['director'] = row['directorname']
  pelicula['actores'] = []
  pelicula['anno'] = row['year']
  pelicula['precio'] = row['price']
  pelicula['poster'] = "goldfinger.jpg" # No tenemos las fotos en la base de datos

  query_act = text("SELECT DISTINCT imdb_actors.actorname\
  FROM imdb_movies INNER JOIN imdb_actormovies ON imdb_movies.movieid = imdb_actormovies.movieid\
  INNER JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid\
  WHERE imdb_movies.movieid = :ide ")

  conn_act = db.connect()
  res_act = conn_act.execute(query_act, ide=id)
  actors = res_act.fetchall()
  for actor in actors:
    pelicula['actores'].append(actor['actorname'])

  context = pelicula
      
  if 'user' in session:
    context['user'] = session['user']
    
  context['inCart'] = False
  if 'cart' in session:
    if str(id) in session['cart']:
      context['inCart'] = True # The film has already been added
  
  return render_template('details.html', **context)  
    
@app.route('/filters', methods=['POST', 'GET'])
def filter():
  json_data = None

  if request.method == 'POST': # We only allow POST requests
    filmName = request.form['SearchFilm']
    category = request.form['CategorySearch']

    json_data = {}
    json_data['peliculas'] = []

    if filmName != '' and filmName != 'Search films by name':
      if category != 'Default': # Filtro por nombre y categoria

        query_ini = text("SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price\
        FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
        INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
        INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
        INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
        INNER JOIN products ON imdb_movies.movieid = products.movieid\
        WHERE genres.name_genre = " + "'" + category + "'" + " AND imdb_movies.movietitle LIKE '%" + filmName + "%'")

      else: # Filtro por nombre
        
        query_ini = text("SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price\
        FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
        INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
        INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
        INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
        INNER JOIN products ON imdb_movies.movieid = products.movieid\
        WHERE imdb_movies.movietitle LIKE '%" + filmName + "%'")

    else:
      if category != 'default': # Filtro por categoria
        
        query_ini = text("SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price\
        FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
        INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
        INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
        INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
        INNER JOIN products ON imdb_movies.movieid = products.movieid\
        WHERE genres.name_genre = " + "'" + category + "'")

      else: # No hay filtro
        
        query_ini = text("SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price\
        FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
        INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
        INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
        INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
        INNER JOIN products ON imdb_movies.movieid = products.movieid")

    conn_ini = db.connect()
    res_ini = conn_ini.execute(query_ini)
    chunk = res_ini.fetchmany(100)
    for row in chunk:
      pelicula = {}
      id = row['movieid']
      pelicula['id'] = id
      pelicula['titulo'] = row['movietitle']
      pelicula['categoria'] = row['name_genre']
      pelicula['director'] = row['directorname']
      pelicula['actores'] = []
      pelicula['anno'] = row['year']
      pelicula['precio'] = row['price']
      pelicula['poster'] = "goldfinger.jpg" # No tenemos las fotos en la base de datos

      query_act = "SELECT DISTINCT imdb_actors.actorname\
      FROM imdb_movies INNER JOIN imdb_actormovies ON imdb_movies.movieid = imdb_actormovies.movieid\
      INNER JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid\
      WHERE imdb_movies.movieid = " + "'" + str(id) + "'"

      conn_act = db.connect()
      res_act = conn_act.execute(query_act)
      actors = res_act.fetchall()
      for actor in actors:
        pelicula['actores'].append(actor['actorname'])

      json_data['peliculas'].append(pelicula)

    

    json_data['categorias'] = []

    query_cats = "SELECT DISTINCT genres.name_genre\
    FROM genres"

    conn_cats = db.connect()
    res_cats = conn_cats.execute(query_cats)
    cats = res_cats.fetchall()
    for cat in cats:
      json_data['categorias'].append(cat['name_genre'])
    
    if 'user' in session:
      json_data['user'] = session['user']
    
  return render_template('index.html', **json_data)

@app.route('/regform')
def registerForm():
  return render_template('register.html', error=False)

@app.route('/register', methods=['POST', 'GET'])
def register():
  if request.method == 'POST': # We only allow POST requests
    user = request.form['Username'].lower()
    password = request.form['Password'].lower()
    email = request.form['E-mail'].lower()
    cCard = request.form['CreditCard'].lower()
    
    consult = "SELECT * FROM customers WHERE customers.username='"+user+"'"
    results = db.execute(consult)
    rows = results.fetchall() # We can fetchall because maximum number of returned objects is one
    if len(rows) != 0: # The user already exists
      return render_template('register.html', error=True)

    # We get the current customerid and update it
    results = db.execute("SELECT MAX(customers.customerid) FROM customers")
    id_cost = results.fetchall()[0][0]
    id_cost += 1

    consult = "INSERT INTO customers(customerid, firstname, lastname, address1, city, country, region, email, creditcardtype, creditcard, creditcardexpiration, username, password, income)\
    VALUES ("+str(id_cost)+", 'first', 'last', 'random street 12', 'madrid', 26, 'driven', '"+email+"', 'VISA', '"+cCard+"', '201502', '"+user+"', '"+password+"', "+str(random.randint(0, 101))+")"
    db.execute(consult)

    return render_template('login.html', error=False)
    
@app.route('/logform')
def loginForm():
  user=request.cookies.get('lastUser')
  if user:
    return render_template('login.html', error=False, cookie=user)
  
  return render_template('login.html', error=False)

@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'POST': # We only allow POST requests
    user = request.form['Username'].lower()
    password = request.form['Password'].lower()

    consult = "SELECT * FROM customers WHERE customers.username='"+user+"'"
    results = db.execute(consult)
    rows = results.fetchall() # We can fetchall because maximum number of returned objects is one
    if len(rows) == 0: # The user doesnt exist
      return render_template('login.html', error=True)

    result = rows[0]
    passwordFromDb = str(result[-4]) # First result password
    if password != passwordFromDb: # Wrong password
      return render_template('login.html', error=True)

    # Update the session
    session['userid']=str(result[0])
    session['user']=str(result[-5])
    session['email']=str(result[-10])
    session['creditcard']=str(result[-7])
    session['balance']=str(result[-2])
    session['cash']=False
    session['generatedOrder']=False
    session.modified=True

    # We create a order for the given cart with the given films in orderdetail
    if 'cart' in session:
      if len(session['cart']) > 0:
        for peli in session['cart']:
          addToCartAux(peli) # We can do this since user is already in session

    response = make_response(redirect(url_for('index')))
    response.set_cookie('lastUser', user)    
        
    return response
    
@app.route('/logout')
def logOut():
  # Update the session
  for key in session.keys():
    if key != 'cart':
      session.pop(key)
  
  if 'cart' in session:
    session['cart']=[]
  
  # Check if there is a NULL status order
  consult="SELECT * FROM orders WHERE status IS NULL"
  results=db.execute(consult)
  rows=results.fetchall()
  if len(rows) > 0:
    order_id = str(rows[0][0])

    # Delete all the orderdetail products attached to the order
    consult="DELETE FROM orderdetail\
    WHERE orderdetail.orderid="+order_id
    db.execute(consult)

    # Delete the current order (because it hasnt been purchased)
    consult="DELETE FROM orders\
    WHERE orders.status IS NULL"
    db.execute(consult)

  return redirect(url_for('index'))

@app.route('/mycart')
def myCart():
  context = {}
  context['peliculas'] = []
  context['total'] = 0.0
  if 'cart' in session:

    for id_pelicula in session['cart']:

      query_ini = text("SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, products.price\
      FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
      INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
      INNER JOIN products ON imdb_movies.movieid = products.movieid\
      WHERE imdb_movies.movieid = :ide")

      conn_ini = db.connect()
      res_ini = conn_ini.execute(query_ini, ide=int(id_pelicula))
      row = res_ini.fetchone()

      pelicula = {}
      id = row['movieid']
      pelicula['id'] = id
      pelicula['titulo'] = row['movietitle']
      pelicula['categoria'] = row['name_genre']
      pelicula['precio'] = row['price']

      context['peliculas'].append(pelicula)
      context['total'] += float(pelicula['precio'])

  if 'user' in session:
    context['user'] = session['user']

  if 'cash' not in session:
    session['cash']=False

  session['total']=context['total']
  context['error']=session['cash']
  session['cash']=False
  session.modified=True

  return render_template('shoppingCart.html', **context)

@app.route('/removeFilm/<string:film>')
def removeFromCart(film):
  session['cart'].remove(film)
  session.modified=True
  
  if 'user' in session and session['generatedOrder']==True: 
    consult="SELECT products.prod_id\
    FROM products\
    WHERE products.movieid="+film
    results = db.execute(consult)
    prodid = results.fetchall()[0][0]
 
    consult="DELETE FROM orderdetail\
    WHERE orderdetail.prod_id="+str(prodid)+" and orderdetail.orderid="+session['orderid']
    db.execute(consult)

  if request.referrer:
    url = request.referrer
        
    return redirect(url)
  else:
    return redirect(url_for('details', pelicula=film))

@app.route('/addFilm/<string:film>')
def addToCart(film):
  if 'cart' not in session:
    session['cart']=[]
    session.modified=True

  if 'user' in session and session['generatedOrder']==False:
    # We get the current orderid and update it
    results = db.execute("SELECT MAX(orders.orderid) FROM orders")
    id_ord = results.fetchall()[0][0]
    id_ord += 1
    session['orderid']=str(id_ord) # orderid to use later
    session['generatedOrder']=True
    session.modified=True
    
    consult="INSERT INTO orders(orderid, orderdate, customerid, netamount, tax, totalamount, status)\
    VALUES ("+str(id_ord)+", CURRENT_DATE, "+session['userid']+", 0, 15, 0, NULL)"
    db.execute(consult)

  session['cart'].append(film)
  session.modified=True
  
  # Triggers do the rest of the job
  if 'user' in session:
    consult="SELECT products.prod_id, products.price\
    FROM products\
    WHERE products.movieid="+film
    res = db.execute(consult)
    aux = res.fetchall()[0]
    prodid = aux[0]
    priceFilm = aux[1]

    consult="INSERT INTO orderdetail(orderid, prod_id, price, quantity)\
    VALUES ("+session['orderid']+", "+str(prodid)+", "+str(priceFilm)+", 1)"
    db.execute(consult)

  return redirect(url_for('details', pelicula=film))
  
@app.route('/confirmAll')
def confirmAll():
  if 'user' not in session:
    return redirect(url_for('loginForm'))

  if 'cart' not in session or len(session['cart']) == 0:
    return redirect(url_for('myCart'))
  
  consult="SELECT *\
  FROM orders\
  WHERE orders.status IS NULL"
  results = db.execute(consult)
  res = results.fetchall()[0] # We get the current order
  totalPrice = res[5]

  if float(session['balance']) < float(totalPrice): # User has not enough money
    session['cash']=True # Money error
    session.modified=True
    
    return redirect(url_for('myCart'))
  
  session['balance'] = str(float(session['balance']) - float(totalPrice))

  consult="UPDATE customers\
  SET income="+session['balance']+" WHERE customers.customerid="+session['userid']
  db.execute(consult)
  
  # The order has been paid
  db.execute("UPDATE orders\
    SET status='Paid'\
    WHERE orders.status IS NULL")
  
  session['cart']=[]
  session['generatedOrder']=False
  session.modified = True
  
  return redirect(url_for('myCart'))
  
@app.route('/shoppingHistory')
def history():
  SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
  json_data=None

  if session:
    query_customer = text("SELECT customerid, income\
    FROM customers\
    WHERE username = :cname")

    conn_customer = db.connect()
    res_customer = conn_customer.execute(query_customer, cname=str(session['user']))
    customer = res_customer.fetchone()
    
    id_costumer = customer['customerid']

    json_data = {}
    json_data['user'] = session['user']
    json_data['money'] = customer['income']
    json_data['fechas'] = {}

    query_ini = text("SELECT DISTINCT ON (imdb_movies.movietitle) imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, products.price, orders.orderdate\
    FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
    INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
    INNER JOIN products ON imdb_movies.movieid = products.movieid\
    INNER JOIN orderdetail ON products.prod_id = orderdetail.prod_id\
    INNER JOIN orders ON orderdetail.orderid = orders.orderid\
    WHERE orders.customerid = :cid")

    conn_ini = db.connect()
    res_ini = conn_ini.execute(query_ini, cid=int(id_costumer))
    chunk = res_ini.fetchall()
    for row in chunk:
      pelicula = {}
      id = row['movieid']
      pelicula['id'] = id
      pelicula['pelicula'] = row['movietitle']
      pelicula['categoria'] = row['name_genre']
      pelicula['precio'] = row['price']
      
      if row['orderdate'] not in json_data['fechas']:
        json_data['fechas'][row['orderdate']]=[]
          
      json_data['fechas'][row['orderdate']].append(pelicula)
  
  return render_template('history.html', **json_data)
  
@app.route('/raiseCash', methods=['POST', 'GET'])
def cash():
  if request.method == 'POST': # We only allow POST requests
    cash = request.form['cash']
    
    session['balance'] = str(float(session['balance']) + float(cash))
    consult="UPDATE customers\
    SET income="+session['balance']+" WHERE customers.customerid="+session['userid']
    db.execute(consult)
    
    return redirect(url_for('history'))
  
@app.route('/numberOfUsers')
def numberOfUsers():
  return '<div><p>Users: '+str(random.randint(1, 1001))+'</p></div>'
  
if __name__ == '__main__':
  db.execute("DELETE FROM orders WHERE orders.status IS NULL") # We have on delete cascade, this is necessary because the user might close the browser in the middle of the session
  app.run(host='0.0.0.0')
