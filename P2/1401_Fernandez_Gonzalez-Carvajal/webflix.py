from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def index():
  try:
    json_data = json.open('/json/catalogo.json')
  except:
    return "<h1>There was a problem loading the catalogue</h1>"
  
  return "<h1>Hello There</h1>"
  
  
if __name__ == '__main__':
  app.run(host='0.0.0.0')
