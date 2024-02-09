from flask import Flask
from flask_migrate import Migrate
from .models import *
from .database import db

migrate = Migrate()

def create_app():
  app = Flask(__name__)

  app.config['SECRET_KEY'] = 'mysecretkey'
  # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@domaine:port/database'
  # exemple en dessous 
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pass@db/tp'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



  db.init_app(app)
  # Creation de la base de données
  with app.app_context():
    db.create_all()

  from .routes import main
  app.register_blueprint(main)

  migrate.init_app(app, db)
  
  return app