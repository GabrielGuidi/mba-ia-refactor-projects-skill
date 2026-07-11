from datetime import datetime, UTC

from flask import Flask
from flask_cors import CORS

from config.settings import load_settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(load_settings())
    CORS(app)
    db.init_app(app)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    register_error_handlers(app)

    @app.get("/health")
    def health():
        return {"status": "ok", "timestamp": datetime.now(UTC).isoformat()}

    @app.get("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    with app.app_context():
        db.create_all()
    return app
