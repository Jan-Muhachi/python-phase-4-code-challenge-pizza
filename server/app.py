#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return make_response([r.to_dict() for r in restaurants])

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return make_response({
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [rp.to_dict(only=("id", "pizza", "price", "restaurant_id")) for rp in restaurant.restaurant_pizzas]
        })
    else:
        return make_response({"error": "Restaurant not found"}), 404

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return make_response({"error": "Restaurant not found"}), 404

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return make_response([pizza.to_dict() for pizza in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    if 'price' not in data or data['price'] < 1 or data['price'] > 30:
        return make_response({"errors": ["Price must be between 1 and 30"]}), 400
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'], pizza_id=data['pizza_id'], restaurant_id=data['restaurant_id'])
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        restaurant_pizza_dict = new_restaurant_pizza.to_dict()
        restaurant_pizza_dict["pizza"] = new_restaurant_pizza.pizza.to_dict()
        restaurant_pizza_dict["restaurant"] = new_restaurant_pizza.restaurant.to_dict()

        return make_response(restaurant_pizza_dict), 201
    except Exception as e:
        return make_response({"errors": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)

