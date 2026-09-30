from flask import Flask
import os

app = Flask(__name__)
app.secret_key = 'hello_world'
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('HOTEL_DB_URI', 'sqlite:///hotel_local.db')


from hotel import models
from hotel import views

