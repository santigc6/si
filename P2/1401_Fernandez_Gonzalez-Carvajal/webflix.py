from flask import Flask, render_template, json, url_for, request, redirect
import os
import sys
import md5
import random

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
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
    if peli['titulo'] == pelicula:
      context = dict(peli)
      break
      
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
          if peli['titulo'].lower().find(filmName) >= 0 and  peli['categoria'].lower() == category:
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
    
    return render_template('index.html', **context)

@app.route('/regform', methods=['POST', 'GET'])
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
    
    os.mkdir(userFolder, 0777)
    f = open(os.path.join(userFolder, 'datos.dat'), 'w+')
    f.write('username: '+user+'\n'+'password: '+md5.new(password).hexdigest()+'\n'+'email: '+email+'\n'+'creditcard: '+cCard+'\n'+'balance: '+str(random.randint(0, 101))+'\n')
    f.close()
    
    return render_template('login.html', error=False)
    
@app.route('/logform', methods=['POST', 'GET'])
def loginForm():
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
    
    f = open(os.path.join(userFolder, 'datos.dat'), 'r')
    lines = f.readlines()
    f.close()
    
    if lines[1].find(md5.new(password).hexdigest()) == -1: # Wrong password
      return render_template('login.html', error=True)
    
    return redirect(url_for('index'))
    
if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
