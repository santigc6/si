-Ha de incluirse un "virtualenv" en el directorio "1401_Fernandez_Gonzalez-Carvajal" de nombre "si1pyenv" tal y como indican las instrucciones de plataforma (no se incluye en la entrega porque el zip supera el tamaño permitido). Este, se supone que usará Python 2.

-Acceder a http://localhost/~<usuario>/webflix.wsgi/ para el índice.

-Hay que darle permisos de escritura en "public_html" a "Apache" para que pueda crear archivos:
  -sudo chgrp www-data public_html/
  -sudo chmod g+w public_html/

-Cuidado con los permisos de la carpeta usuarios, porque al descargar de Moodle se cambian a que el grupo y otros solo tienen lectura (y por lo tanto Apache también). Hay que volver a darles escritura a ambos (y en todas las subcarpetas y subarchivos).

Autores: Adrián Fernández Amador y Santiago González- Carvajal Centenera.
