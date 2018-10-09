from flask import Flask, render_template, json, url_for
import os
import sys

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def index():
  try:
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "json", "catalogo.json")
    file_json = open(json_url)
    json_data = json.load(file_json)
  except IOError:
    return "<h1>There was a problem loading the catalogue</h1>"
  
  file_json.close()
  
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
    
  
if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
