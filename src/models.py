from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    reservations = db.relationship('Reservation', backref='client', lazy=True)

class Chambre(db.Model):
    __tablename__ = 'chambres'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    reservations = db.relationship('Reservation', backref='chambre', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    id_chambre = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    date_arrivee = db.Column(db.Date, nullable=False)
    date_depart = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(50), nullable=False)
