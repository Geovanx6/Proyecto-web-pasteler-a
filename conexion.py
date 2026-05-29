from flask_mysqldb import MySQL


mysql = MySQL()

class Conexion:
    @staticmethod
    def configurar(app):
      
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = ''
        app.config['MYSQL_DB'] = 'api_flask'
        

        mysql.init_app(app)
