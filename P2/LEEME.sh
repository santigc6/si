#!/bin/bash

# Descargar makefile y mod_wsg.tar.gz

make startapache

cd ~/apache2/var/www/html/

cat >hello.py <<EOF
from flask import Flask

app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

EOF

cat >hello.wsgi <<EOF
#!/usr/bin/python
import os
import sys

# virtualenv
this_dir = os.path.dirname(os.path.abspath(__file__))
activate_this = this_dir + '/si1pyenv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# anhadir dir de este fichero a path
sys.path.insert(0, this_dir)
from hello import app as application
EOF

virtualenv -p python2 si1pyenv

source si1pyenv/bin/activate

pip install Flask SQLAlchemy Flask-SQLAlchemy SQLAlchemy-Utils   psycopg2 Flask-Session

echo "Acceder a localhost:8080/hello.wsgi"
