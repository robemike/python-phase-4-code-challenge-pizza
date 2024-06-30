#!/usr/bin/env python3
# Make importations from the necessary modules for particular componenets.
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Create an instance of the Flask class 'app' (Creates the application).
app = Flask(__name__)
# The below is for configuration
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Create an instance of Migrate.
migrate = Migrate(app, db)

# db instance initialized with the flask app 'app' which we initialized with the Flask class.
db.init_app(app)

api = Api(app)

# Definition of the first route. Returns a HTML text.
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Define a route /restaurants that retrieves all restaurant objects from the database.
@app.route('/restaurants')
def restaurants():
    # Construct a list to store the dictionaries.
    restaurants = list()
    # Create the dictionaries.
    for restaurant in Restaurant.query.all():
        restaurant_dict = {
            "id" : restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
        }
        # Append the dictianaries to the list created.
        restaurants.append(restaurant_dict)
        # Create a response object containing the list created above
    response = make_response(restaurants, 200)
    # REturn the response.
    return response

# A route /restaurants/<int:id> to retrieve a particular restaurant object from the database.
# The GET method will retrieve details of a restaurant of the specified id.
@app.route('/restaurants/<int:id>', methods = ['GET', 'DELETE'])
def restaurants_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if request.method == 'GET': 
        if restaurant:
            restaurant_dict = restaurant.to_dict()
            response = make_response(restaurant_dict, 200)
            return response

        else:
            body = {"error": "Restaurant not found"}
            status = 404
            return (body, status)
        
# The DELETE method will delete restaurant of the specified id if it exists.
    elif request.method == 'DELETE':
        if restaurant:
             db.session.delete(restaurant)
            #  After every SQL operation, we need to commit our changes.
             db.session.commit()
             body = {"Deleted": True, "msg":"Restaurant deleted"}
             response = make_response(body, 204)
             return response
        else:
            body = {"error": "Restaurant not found"}
            status = 404
            return (body, status)
        
# Route /pizzas that retrieves all pizza objects from the database.
@app.route('/pizzas')
def pizzas():
    # Craete a list to store all the pizza objects in (The dictionaries).
    pizzas = list()
    # Create the dictionaries.
    for pizza in Pizza.query.all():
        pizza_dict = {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        # Append the dictionaries to the list created.
        pizzas.append(pizza_dict)
        # Create a response object containing the list created above.
    response = make_response(pizzas, 200)
    # Return the response object itself.
    return response

# Another route /restaurant_pizzas that handle POST and GET methods.
@app.route('/restaurant_pizzas', methods = ['GET', 'POST'])
def restaurant_pizzas():
    # The GET method retrieves all the restaurent_pizza objects from the database.
    if request.method == 'GET':
        # Create a list to store the restaurant pizza objects.
        restaurant_pizzas = list()
        # Create the dictionaries.
        for restaurant_pizza in RestaurantPizza.query.all():
            restaurant_pizza_dict = restaurant_pizza.to_dict()
            restaurant_pizzas.append(restaurant_pizza_dict)
            # Create a  response object to which contains the above list.
        response = make_response(restaurant_pizzas, 200)
        # Return the response object.
        return response
    
    # The POST method creates a new restaurant_pizza object in the database.
    elif request.method == 'POST':
        json_data = request.get_json()
        # Validation of the data that has been input
        try:
            new_restaurant_pizza = RestaurantPizza(
                price = json_data.get("price"),
                restaurant_id = json_data.get("restaurant_id"),
                pizza_id = json_data.get("pizza_id")
            )
        except ValueError as exc:
            response_body = {"errors": ["validation errors"]}
            status = 400
            return (response_body, status)

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        restaurant_pizza_dict = new_restaurant_pizza.to_dict()
        # Create a response object to return to commit the new relationship to the database.
        response = make_response(restaurant_pizza_dict, 201)
        # Return the response object.
        return response


if __name__ == "__main__":
    app.run(port=5555, debug=True)
