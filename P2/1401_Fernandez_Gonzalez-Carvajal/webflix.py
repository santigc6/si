from flask import Flask, render_template, json, url_for, request, redirect, session, make_response
import os
import sys
import md5
import random
import json

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
  
  return render_template('index.html', **json_data)

@app.route('/details/<string:pelicula>')
def details(pelicula):
  try:
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "json", "catalogo.json")
    file_json = open(json_url)
    json_data = json.load(file_json)
  except IOError:
    return "<h1>There was a problem loading the information of the film</h1>"
  
  file_json.close()
  
  for peli in json_data['peliculas']:
    if str(peli['id']) == pelicula:
      context = dict(peli)
      break
      
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
    
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    userFolder = os.path.join(SITE_ROOT, "usuarios", user)
    
    if os.path.exists(userFolder) == True: # The user already exists
      return render_template('register.html', error=True)
    
    oldmask = os.umask(000)
    os.mkdir(userFolder, 0777)
    os.umask(oldmask)
    f = open(os.path.join(userFolder, 'datos.dat'), 'w+')
    f.write('username: '+user+'\n'+'password: '+md5.new(password).hexdigest()+'\n'+'email: '+email+'\n'+'creditcard: '+cCard+'\n'+'balance: '+str(random.randint(0, 101))+'\n')
    f.close()
    
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
    
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    userFolder = os.path.join(SITE_ROOT, "usuarios", user)
    
    if os.path.exists(userFolder) == False: # The user doesnt exist
      return render_template('login.html', error=True)
    
    try:
      f = open(os.path.join(userFolder, 'datos.dat'), 'r')
      lines = f.readlines()
    except IOError:
      return "<h1>Something went wrong</h1>"
    f.close()
    
    if lines[1].find(md5.new(password).hexdigest()) == -1: # Wrong password
      return render_template('login.html', error=True)
    
    # Update the session
    session['user']=lines[0].split()[1]
    session['email']=lines[2].split()[1]
    session['creditcard']=lines[3].split()[1]
    session['balance']=lines[4].split()[1]
    session.modified=True
 
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

    response = make_response(render_template('index.html', **json_data))
    response.set_cookie('lastUser', user)    
        
    return response
    
@app.route('/logout')
def logOut():
  # Update the session
  for key in session.keys():
    if key != 'cart':
      session.pop(key)
     
  return redirect(url_for('index'))

@app.route('/mycart')
def myCart():
  
  return render_template('shoppingCart.html', error=False)

@app.route('/removeFilm/<string:film>')
def removeFromCart(film):
  session['cart'].remove(film)
  session.modified=True
      
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
  
  price = 0
  for peli in json_data['peliculas']:
    if str(peli['id']) == film:
      price = peli['precio']
      
  if user['balance'] < price:
    return render_template('shoppingCart.html', error=False) # You are oom
    
  session['balance'] -= price
  
  
  
@app.route('/confirmAll')
def confirmAll():
  if 'user' not in session:
    return redirect(url_for('logForm'))

  SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

  try:
    json_url = os.path.join(SITE_ROOT, "json", "catalogo.json")
    file_json = open(json_url)
    json_data = json.load(file_json)
  except IOError:
    return "<h1>There was a problem with your operation</h1>"
  
  file_json.close()
  
  if 'cart' in session:
    price = 0
    for film in user['cart']:
      for peli in json_data['peliculas']:
        if str(peli['id']) == film:
          price += peli['precio']
          
  if user['balance'] < price:
    return render_template('shoppingCart.html', error=False) # You are oom
  
  session['balance'] -= price
  
  try:
    json_url = os.path.join(SITE_ROOT, 'usuarios', session['user'], 'historial.json')
    file_json = open(json_url)
    json_data = json.load(file_json)
  except IOError:
    return "<h1>There was a problem with your operation</h1>"
  
  file_json.close()
  
if __name__ == '__main__':
  app.run(host='0.0.0.0')
