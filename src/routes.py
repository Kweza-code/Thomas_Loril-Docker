from flask import Blueprint, render_template
from .database import db
from .models import Chambre, Client, Reservation
from flask import jsonify, request

main = Blueprint('main', __name__)

@main.route('/' , methods=['GET'])
def index():
    return jsonify({"message": "bonjour"})

@main.route('/api/chambres', methods=['POST'])
def ajouter_chambre():

    # Vérification basique des données reçues
    if not data or 'numero' not in data or 'type' not in data or 'prix' not in data:
        return jsonify({'success': False, 'message': "Données manquantes ou incorrectes."}), 400

    # Vérifier si la chambre existe déjà
    if Chambre.query.filter_by(numero=data['numero']).first() is not None:
        return jsonify({'success': False, 'message': "Une chambre avec ce numéro existe déjà."}), 400

    nouvelle_chambre = Chambre(
        numero=data['numero'],
        type=data['type'],
        prix=data['prix']
    )

    try:
        db.session.add(nouvelle_chambre)
        db.session.commit()
        return jsonify({'success': True, 'message': "Chambre ajoutée avec succès."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': "Erreur lors de l'ajout de la chambre."}), 500

@main.route('/api/chambres/<int:id>', methods=['PUT'])
def modifier_chambre(id):
    chambre = Chambre.query.get(id)
    if not chambre:
        return jsonify({'success': False, 'message': "Chambre non trouvée."}), 404

    
    try:
        if 'numero' in data:
            chambre.numero = data['numero']
        if 'type' in data:
            chambre.type = data['type']
        if 'prix' in data:
            chambre.prix = data['prix']
        
        db.session.commit()
        return jsonify({'success': True, 'message': "Chambre mise à jour avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': "Erreur lors de la mise à jour de la chambre."}), 500
    
@main.route('/api/chambres/<int:id>', methods=['DELETE'])
def supprimer_chambre(id):
    chambre = Chambre.query.get(id)
    if not chambre:
        return jsonify({'success': False, 'message': "Chambre non trouvée."}), 404
    
    try:
        db.session.delete(chambre)
        db.session.commit()
        return jsonify({'success': True, 'message': "Chambre supprimée avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': "Erreur lors de la suppression de la chambre."}), 500

@main.route('/api/reservations', methods=['POST'])
def creer_reservation():

    # Vérification des données reçues
    if not all(key in data for key in ('id_client', 'date_arrivee', 'date_depart')):
        return jsonify({'success': False, 'message': "Données manquantes pour la réservation."}), 400

    id_client = data['id_client']
    date_arrivee = datetime.strptime(data['date_arrivee'], '%Y-%m-%d')
    date_depart = datetime.strptime(data['date_depart'], '%Y-%m-%d')

    # Vérifier si les dates sont valides
    if date_arrivee >= date_depart:
        return jsonify({'success': False, 'message': "Les dates de réservation sont invalides."}), 400

    # Recherche des chambres disponibles
    chambres_disponibles = Chambre.query.filter(
        ~Chambre.reservations.any(
            (Reservation.date_arrivee < date_depart) & (Reservation.date_depart > date_arrivee)
        )
    ).all()

    if not chambres_disponibles:
        return jsonify({'success': False, 'message': "Aucune chambre disponible pour les dates sélectionnées."}), 404

    # Créer la réservation avec la première chambre disponible
    nouvelle_reservation = Reservation(
        client_id=id_client,
        chambre_id=chambres_disponibles[0].id,
        date_arrivee=date_arrivee,
        date_depart=date_depart,
        statut='Confirmée'
    )

    try:
        db.session.add(nouvelle_reservation)
        db.session.commit()
        return jsonify({'success': True, 'message': "Réservation créée avec succès."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': "Erreur lors de la création de la réservation."}), 500
    
@main.route('/api/reservations/<int:id>', methods=['DELETE'])
def annuler_reservation(id):
    reservation = Reservation.query.get(id)
    if not reservation:
        return jsonify({'success': False, 'message': "Réservation non trouvée."}), 404

    try:
        db.session.delete(reservation)
        db.session.commit()
        return jsonify({'success': True, 'message': "Réservation annulée avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': "Erreur lors de l'annulation de la réservation."}), 500

@main.route('/api/chambres/disponibles', methods=['GET'])
def rechercher_chambres_disponibles():
    date_arrivee = request.args.get('date_arrivee', None)
    date_depart = request.args.get('date_depart', None)

    # Vérification que les dates sont fournies
    if not date_arrivee or not date_depart:
        return jsonify({'success': False, 'message': "Veuillez fournir les dates d'arrivée et de départ."}), 400

    # Conversion des dates en objets datetime
    try:
        date_arrivee = datetime.strptime(date_arrivee, '%Y-%m-%d')
        date_depart = datetime.strptime(date_depart, '%Y-%m-%d')
    except ValueError:
        return jsonify({'success': False, 'message': "Format de date invalide. Utilisez YYYY-MM-DD."}), 400

    # Vérification que la date de départ est après la date d'arrivée
    if date_arrivee >= date_depart:
        return jsonify({'success': False, 'message': "La date de départ doit être après la date d'arrivée."}), 400

    # Recherche des chambres disponibles
    chambres_disponibles = Chambre.query.filter(
        ~Chambre.reservations.any(
            (Reservation.date_arrivee < date_depart) & (Reservation.date_depart > date_arrivee)
        )
    ).all()

    chambres = [
        {
            "id": chambre.id,
            "numero": chambre.numero,
            "type": chambre.type,
            "prix": chambre.prix
        } for chambre in chambres_disponibles
    ]

    return jsonify(chambres), 200