from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    # Add association proxies to complete restaurant-pizza many-to-many relationship.
    pizzas = association_proxy('restaurant_pizzas', 'pizza',
                               creator=lambda pizza_obj: RestaurantPizza(pizza=pizza_obj))

    # add serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')
    # Add association proxies to complete restaurant-pizza many-to-many relationship.
    restaurants = association_proxy('restaurant_pizzas','restaurant',
                               creator=lambda restaurant_obj: RestaurantPizza(restaurant=restaurant_obj))

    # add serialization rules
    serialize_rules = ('-restaurant_pizzas.pizza',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"


    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Add the foreign key columns(resaturant_id) and (pizaa_id).
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))

    # add relationships
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    # add serialization rules
    serialize_rules = ('-restaurant.restaurant_pizzas', 'pizza.restaurant_pizzas',)

    # add validation
    @validates("price")
    def validate_price(self, key, price):
        if not 1 <= price <= 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
    

# There is a relationship between restaurants and the pizzas which is a many-many relationship.
# They are related via the RestaurantPizaa model
# Therefore, one to many relationship betweeen the association model and the related models.
# one to many relationship between restaurant and the restaurant_pizzas table.(One row in the restaurants table related to many rows in the restaurants_pizzas table)
# One-to-many relationship between pizzas and restaurant_pizzas table. (One row in the pizzas table related to many rows in the restaurant_pizzas table)
# Don't forget about the validations.