from flask import Flask
from flask_cors import CORS

from src.config.settings import load_settings
from src.database import close_db, initialize_database
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import api


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(load_settings())

    CORS(app)
    app.register_blueprint(api)
    app.teardown_appcontext(close_db)
    register_error_handlers(app)

    with app.app_context():
        initialize_database()

    return app
