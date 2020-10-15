from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'e6040f19d063c7ea55a33765df99277c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pass.db'
db = SQLAlchemy(app)

from manager import routes