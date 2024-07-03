from sqlalchemy import create_engine, func
from sqlalchemy import event
from sqlalchemy import text
from datetime import datetime
from sqlalchemy_utils import create_database, database_exists
from datetime import datetime
from flask import Flask, jsonify, request
from models import db, Device, SMS, Call, SIM, Status, Account, Authuser
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
import configparser
import ssl
from pprint import pprint
import json
import printr


config = configparser.ConfigParser()
config.read('config.ini')

dbuser = config.get('ri', 'dbuser')
dbhost = config.get('ri', 'dbhost')
dbname = config.get('ri', 'dbname')


engine = create_engine('mysql+pymysql://' + dbuser + '@' + dbhost + '/' + dbname)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = engine.url
db.init_app(app)
auth = HTTPBasicAuth()
authuser = HTTPBasicAuth()

app.config['SECRET_KEY'] = 'secret-key'
from routes_android import rtand_bp
from routes_other import rtoth_bp
app.register_blueprint(rtand_bp)
app.register_blueprint(rtoth_bp)

if database_exists(engine.url):
    print("Database already exists")
    with app.app_context():
        db.create_all()

else:
    if not create_database(engine.url):
        print('Database created successfully.')
        app.config['SQLALCHEMY_DATABASE_URI'] = engine.url
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    with app.app_context():
        app.run(host='0.0.0.0', debug=True )

