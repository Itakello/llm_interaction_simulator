from flask import Flask
from pymongo import MongoClient


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = (
        "mongodb://localhost:27017/your_database"  # Update with your actual MongoDB URI
    )

    # Initialize MongoDB client
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client.get_default_database()

    with app.app_context():
        from .routes import initialize_routes

        initialize_routes(app)

    return app
