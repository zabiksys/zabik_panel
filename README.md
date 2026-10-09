Multipage App
https://discourse.holoviz.org/t/multi-page-app-documentation/3108/3

Ejecutar:
$ panel serve --allow-websocket-origin=pc-jcn.local.zabik:5006 --enable-xsrf-cookies --auth-module=auth.py app.py

Hay que instalar unixodbc y msodbcsql (la última versión en AUR es 18). Dependiendo de la versión del
odbc de mssql hay que modificar los params de navision y sql server.

# Crear las Miniaturas

El tamaño de las miniaturas es 300 x 200.

Para crearlas entrar en las herramientas de desarrollador de Firefox y
seleccionar la vista adaptable y allí se leccionar la resolución 900 x 600,
hacer una captura de pantalla y reducirla en Gimp a 300 x 200.

