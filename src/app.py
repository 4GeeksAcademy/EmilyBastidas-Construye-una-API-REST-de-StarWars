"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite, Vehicle
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# listar characters


@app.route('/characters', methods=['GET'])
def get_character():
    characters = Character.query.all()
    characters_list = [char.serialize() for char in characters]
    return jsonify(characters_list), 200

# información character 


@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character_id(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    return jsonify({
        "character": character.serialize(),
        "favorites": [favorite.serialize() for favorite in character.favorites]
    }), 200

# listar planet


@app.route('/planets', methods=['GET'])
def planets_hello():
    planets = Planet.query.all()
    planets_list = [planet.serialize() for planet in planets]
    return jsonify(planets_list), 200

# información planet


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    favorites = [favorite.serialize() for favorite in planet.favorites]
    return jsonify(planet.serialize()), 200

# listar users


@app.route('/users', methods=['GET'])
def get_user():
    users = User.query.all()
    users_list = [user.serialize() for user in users]
    return jsonify(users_list), 200

# listar favoritos del user actual


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    favorites = [favorite.serialize() for favorite in user.favorites]
    return jsonify(favorites), 200

# Add planet fav al user actual


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_favorite(planet_id):
    user_id = 1

    planet = Planet.query.get(planet_id)
    if not planet:

        return jsonify({"error": "Planet not found"}), 404

    favorite = Favorite(
        user_id=user_id,
        planet_id=planet_id,
        character_id=None,
        vehicle_id=None
    )
    db.session.add(favorite)
    db.session.commit()

    return jsonify(favorite.serialize()), 201

# add nuevo character fav al usuario actual


@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_character_favorite(character_id):
    user_id = 1

    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    favorite = Favorite(
        user_id=user_id,
        character_id=character_id,
        planet_id=None,
        vehicle_id=None
    )
    db.session.add(favorite)
    db.session.commit()

    return jsonify(favorite.serialize()), 201

# Delete planet favorito 


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    user_id = 1

    favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorite planet not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite planet deleted"}), 200

# Delete character favorito 


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    user_id = 1

    favorite = Favorite.query.filter_by(
        user_id=user_id, character_id=character_id,).first()
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
