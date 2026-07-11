from flask import jsonify
from werkzeug.exceptions import HTTPException


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"erro": error.message, "sucesso": False}), error.status

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"erro": error.description, "sucesso": False}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception(error)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
