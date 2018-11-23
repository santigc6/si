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

@app.route('/')
@app.route('/index')
def index():
  SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

  users_path = os.path.join(SITE_ROOT, 'usuarios')
  if os.path.exists(users_path) == False: # If users' directory doesnt exist we create it
    oldmask = os.umask(000)
    os.mkdir(users_path, 0777)
    os.umask(oldmask)

  try:
    json_url = os.path.join(SITE_ROOT, "json", "vacio.json")
    file_json = open(json_url)
    json_data = json.load(file_json)
  except IOError:
    return "<h1>There was a problem loading the catalogue</h1>"

  file_json.close()


  query_ini = "SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price\
  FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
  INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
  INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
  INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
  INNER JOIN products ON imdb_movies.movieid = products.movieid"

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

  
  cats = set()
  for peli in json_data["peliculas"]:
    cats.add(peli["categoria"])
  
  json_data["categorias"]=list(cats)
  
  if 'user' in session:
    json_data['user'] = session['user']
  
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
    if pelicula in session['cart']:
      context['inCart'] = True # The film has already been added
  
  return render_template('details.html', **context)  
    
@app.route('/filters', methods=['POST', 'GET'])
def filter():
  if request.method == 'POST': # We only allow POST requests
    filmName = request.form['SearchFilm'].lower()
    category = request.form['CategorySearch'].lower()
    
    try:
      SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
      json_url = os.path.join(SITE_ROOT, "json", "catalogo.json")
      file_json = open(json_url)
      json_data = json.load(file_json)
    except IOError:
      return "<h1>There was a problem loading the catalogue</h1>"
    
    file_json.close()
    context = {'peliculas': []}
    if filmName != '' and filmName != 'search film': # Filtro por nombre y categoria
      if category != 'default':  
        for peli in json_data['peliculas']:
          if peli['titulo'].lower().find(filmName) >= 0 and peli['categoria'].lower() == category:
            context['peliculas'].append(peli)
      else: # Filtro por nombre
        for peli in json_data['peliculas']:
          if peli['titulo'].lower().find(filmName) >= 0:
            context['peliculas'].append(peli)
    else:
      if category != 'default':  # Filtro por categoria
        for peli in json_data['peliculas']:
          if peli['categoria'].lower() == category:
            context['peliculas'].append(peli)
      else: # No hay filtro
        for peli in json_data['peliculas']:
          context['peliculas'].append(peli)
      
    cats = set()
    for peli in json_data["peliculas"]:
      cats.add(peli["categoria"])
    
    context["categorias"]=list(cats)
    if 'user' in session:
      context['user'] = session['user']
    
    return render_template('index.html', **context)

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
    session['user']=str(result[-5])
    session['email']=str(result[-10])
    session['creditcard']=str(result[-7])
    session['balance']=str(result[-2])
    session['cash']=False
    session.modified=True
 
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

    try:
      json_url = os.path.join(SITE_ROOT, "json", "catalogo.json")
      file_json = open(json_url)
      json_data = json.load(file_json)
    except IOError:
      return "<h1>There was a problem loading the catalogue</h1>"
    
    file_json.close()
    
    cats = set()
    for peli in json_data["peliculas"]:
      cats.add(peli["categoria"])
    
    json_data["categorias"]=list(cats)
    
    if 'user' in session:
      json_data['user'] = session['user']

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
     
  return redirect(url_for('index'))

@app.route('/mycart')
def myCart():
  context = {}
  context['peliculas'] = []
  context['total'] = 0.0
  if 'cart' in session:

    for id_pelicula in session['cart']:

      query_ini = text("SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price\
      FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
      INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
      INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
      INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
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
      pelicula['director'] = row['directorname']
      pelicula['actores'] = []
      pelicula['anno'] = row['year']
      pelicula['precio'] = row['price']
      pelicula['poster'] = "goldfinger.jpg" # No tenemos las fotos en la base de datos

      query_act = text("SELECT DISTINCT imdb_actors.actorname\
      FROM imdb_movies INNER JOIN imdb_actormovies ON imdb_movies.movieid = imdb_actormovies.movieid\
      INNER JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid\
      WHERE imdb_movies.movieid = :ide")

      conn_act = db.connect()
      res_act = conn_act.execute(query_act, ide=int(id))
      actors = res_act.fetchall()
      for actor in actors:
        pelicula['actores'].append(actor['actorname'])

      context['peliculas'].append(pelicula)
      context['total'] += float(pelicula['precio'])

  if 'user' in session:
    context['user'] = session['user']

  if 'cash' not in session:
    session['cash']=False

  context['error']=session['cash']
  session['cash']=False
  session.modified=True

  return render_template('shoppingCart.html', **context)

@app.route('/removeFilm/<string:film>')
def removeFromCart(film):
  session['cart'].remove(film)
  session.modified=True
  
  if request.referrer:
    url = request.referrer
        
    return redirect(url)
  else:
    return redirect(url_for('details', pelicula=film))

@app.route('/addFilm/<string:film>')
def addToCart(film):
  if 'cart' not in session:
    session['cart']=[]
  
  session['cart'].append(film)
  session.modified=True
  
  return redirect(url_for('details', pelicula=film))

@app.route('/confirmFilm/<string:film>')
def confirmFilm(film):
  if 'user' not in session:
    return redirect(url_for('loginForm'))
    
  SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

  try:
    json_url = os.path.join(SITE_ROOT, "json", "catalogo.json")
    file_json = open(json_url)
    json_data = json.load(file_json)
  except IOError:
    return "<h1>There was a problem with your operation</h1>"
  
  file_json.close()
  
  today = datetime.datetime.now()
  aux={}
  price = 0.0
  for peli in json_data['peliculas']:
    if str(peli['id']) == film:
      price = peli['precio']
      aux['id']=peli['id']
      aux['pelicula']=peli['titulo']
      aux['precio']=peli['precio']
      aux['fecha']=str(today.day)+'/'+str(today.month)+'/'+str(today.year)
      
  if float(session['balance']) < price:
    session['cash']=True
    session.modified=True
    
    return redirect(url_for('myCart'))
    
  session['balance'] = str(float(session['balance']) - price)
  
  try:
    data_url = os.path.join(SITE_ROOT, 'usuarios', session['user'], 'datos.dat')
    file_data = open(data_url, 'r')  
  except IOError:
    return "<h1>There was a problem with your operation</h1>"
  
  lines = file_data.readlines()
  lines[-1] = 'balance: '+session['balance'] # New balance

  file_data.close()
  
  try:
    file_data = open(data_url, 'w')
    file_data.writelines(lines)
  except IOError:
    return "<h1>There was a problem with your operation</h1>" 
  
  file_data.close()
  
  json_data = None
  try:
    json_url = os.path.join(SITE_ROOT, 'usuarios', session['user'], 'historial.json')
    file_json = open(json_url)  
    json_data = json.load(file_json)
  except IOError:
    pass
  
  if json_data != None:
    file_json.close()
    
    json_data['peliculas'].append(aux)
  else:
    json_data = {}
    json_data['peliculas']=[]
    json_data['peliculas'].append(aux)

  try:
    file_json = open(json_url, 'w+')  
    json.dump(json_data, file_json)
  except IOError:
    return "<h1>There was a problem with your operation</h1>" 
   
  file_json.close()
  
  session['cart'].remove(film)
  session.modified = True
  
  return redirect(url_for('myCart'))
  
@app.route('/confirmAll')
def confirmAll():
  if 'user' not in session:
    return redirect(url_for('loginForm'))

  SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

  try:
    json_url = os.path.join(SITE_ROOT, "json", "catalogo.json")
    file_json = open(json_url)
    json_data = json.load(file_json)
  except IOError:
    return "<h1>There was a problem with your operation</h1>"
  
  file_json.close()
  
  today = datetime.datetime.now()
  l_diccs=[]
  if 'cart' in session:
    price = 0.0
    for film in session['cart']:
      aux={}
      for peli in json_data['peliculas']:
        if str(peli['id']) == film:
          price += peli['precio']
          aux['id']=peli['id']
          aux['pelicula']=peli['titulo']
          aux['precio']=peli['precio']
          aux['fecha']=str(today.day)+'/'+str(today.month)+'/'+str(today.year)
          l_diccs.append(aux)
  else:
    return redirect(url_for('myCart'))
          
  if float(session['balance']) < price:
    session['cash']=True
    session.modified=True
    
    return redirect(url_for('myCart'))
  
  session['balance'] = str(float(session['balance']) - price)
  
  try:
    data_url = os.path.join(SITE_ROOT, 'usuarios', session['user'], 'datos.dat')
    file_data = open(data_url, 'r')  
  except IOError:
    return "<h1>There was a problem with your operation</h1>"
  
  lines = file_data.readlines()
  lines[-1] = 'balance: '+session['balance'] # New balance

  file_data.close()
  
  try:
    file_data = open(data_url, 'w')
    file_data.writelines(lines)
  except IOError:
    return "<h1>There was a problem with your operation</h1>" 
  
  file_data.close()
  
  json_data = None
  try:
    json_url = os.path.join(SITE_ROOT, 'usuarios', session['user'], 'historial.json')
    file_json = open(json_url)  
    json_data = json.load(file_json)
  except IOError:
    pass
  
  if json_data != None:
    file_json.close()
    for item in l_diccs:
      json_data['peliculas'].append(item)
  else:
    json_data = {}
    json_data['peliculas']=l_diccs
  
  try:
    file_json = open(json_url, 'w+')  
    json.dump(json_data, file_json)
  except IOError:
    return "<h1>There was a problem with your operation</h1>" 
   
  file_json.close()
  
  session['cart']=[]
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

    query_ini = text("SELECT DISTINCT imdb_movies.movieid, imdb_movies.movietitle, genres.name_genre, imdb_directors.directorname, imdb_movies.year, products.price, orders.orderdate\
    FROM imdb_movies INNER JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid\
    INNER JOIN genres ON imdb_moviegenres.genre = genres.id_genre\
    INNER JOIN imdb_directormovies ON imdb_movies.movieid = imdb_directormovies.movieid\
    INNER JOIN imdb_directors ON imdb_directormovies.directorid = imdb_directors.directorid\
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

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

    try:
      data_url = os.path.join(SITE_ROOT, 'usuarios', session['user'], 'datos.dat')
      file_data = open(data_url, 'r')  
    except IOError:
      return "<h1>There was a problem with your operation</h1>"
    
    session['balance'] = str(float(session['balance']) + float(cash))
    lines = file_data.readlines()
    lines[-1] = 'balance: '+session['balance'] # New balance

    file_data.close()
    
    try:
      file_data = open(data_url, 'w')
      file_data.writelines(lines)
    except IOError:
      return "<h1>There was a problem with your operation</h1>" 
    
    file_data.close()
    
    return redirect(url_for('history'))
  
@app.route('/numberOfUsers')
def numberOfUsers():
  return '<div><p>Users: '+str(random.randint(1, 1001))+'</p></div>'
  
if __name__ == '__main__':
  app.run(host='0.0.0.0')
