from flask import Flask, request, jsonify, Blueprint
from models import Reservation, Chambre, Client, db  
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/' , methods=['GET'])
def index():
    return jsonify({"message": "bonjour"})

@main.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()

    # Convertir les dates en objets datetime
    date_arrivee = datetime.strptime(data['date_arrivee'], '%Y-%m-%d')
    date_depart = datetime.strptime(data['date_depart'], '%Y-%m-%d')

    # Vérifier la disponibilité de la chambre pour les dates demandées
    chambre_disponible = Chambre.query.filter(
        ~Chambre.reservations.any(
            (Reservation.date_arrivee <= date_depart) &
            (Reservation.date_depart >= date_arrivee)
        )
    ).first()

    if chambre_disponible:
        # Créer et enregistrer la nouvelle réservation
        new_reservation = Reservation(id_client=data['id_client'], date_arrivee=date_arrivee, date_depart=date_depart)
        db.session.add(new_reservation)
        db.session.commit()
        return jsonify({"success": True, "message": "Réservation créée avec succès."}), 201
    else:
        return jsonify({"success": False, "message": "La chambre n'est pas disponible pour les dates demandées."}), 400

@main.route('/api/reservations/<int:id>', methods=['DELETE'])
def cancel_reservation(id):
    # Recherche la réservation dans la base de données
    reservation = Reservation.query.get(id)

    if not reservation:
        return jsonify({'success': False, 'message': 'Réservation non trouvée.'}), 404

    # Supprime la réservation de la base de données
    db.session.delete(reservation)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Réservation annulée avec succès.'}), 200

@main.route('/api/chambres', methods=['POST'])
def add_chambre():
    data = request.get_json()

    numero = data.get('numero')
    type = data.get('type')
    prix = data.get('prix')

    if not numero or not type or not prix:
        return jsonify({"success": False, "message": "Tous les champs sont requis."}), 400

    # Créer et enregistrer la nouvelle chambre
    nouvelle_chambre = Chambre(numero=numero, type=type, prix=prix)
    db.session.add(nouvelle_chambre)
    db.session.commit()

    return jsonify({"success": True, "message": "Chambre ajoutée avec succès."}), 201

@main.route('/api/chambres/<int:id>', methods=['PUT'])
def update_chambre(id):
    data = request.get_json()

    numero = data.get('numero')
    type = data.get('type')
    prix = data.get('prix')

    chambre = Chambre.query.get(id)

    if not chambre:
        return jsonify({'success': False, 'message': 'Chambre non trouvée.'}), 404

    chambre.numero = numero if numero else chambre.numero
    chambre.type = type if type else chambre.type
    chambre.prix = prix if prix else chambre.prix

    db.session.commit()

    return jsonify({'success': True, 'message': 'Chambre mise à jour avec succès.'}), 200

@main.route('/api/chambres/<int:id>', methods=['DELETE'])
def delete_chambre(id):
    chambre = Chambre.query.get(id)

    if not chambre:
        return jsonify({'success': False, 'message': 'Chambre non trouvée.'}), 404

    db.session.delete(chambre)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Chambre supprimée avec succès.'}), 200

# Endpoint pour rechercher les chambres disponibles
@main.route('/api/chambres/disponibles', methods=['GET'])
def chambres_disponibles():
    date_arrivee = request.args.get('date_arrivee')
    date_depart = request.args.get('date_depart')

    # Convertir les dates en objets datetime
    date_arrivee = datetime.strptime(date_arrivee_str, '%Y-%m-%d')
    date_depart = datetime.strptime(date_depart_str, '%Y-%m-%d')

    # Recherche des chambres disponibles
    chambres_disponibles = Chambre.query.filter(
        ~Chambre.reservations.any(
            (Reservation.date_arrivee <= date_depart) &
            (Reservation.date_depart >= date_arrivee)
        )
    ).all()

    # Construction de la réponse JSON
    response = []
    for chambre in chambres_disponibles:
        response.append({
            'id': chambre.id,
            'numero': chambre.numero,
            'type': chambre.type,
            'prix': float(chambre.prix)  # Assure-toi que le prix est un float
        })

    return jsonify(response), 200

