from functools import wraps
from hmac import compare_digest

from flask import current_app, request

from src.middlewares.error_handler import AppError


def admin_required(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        expected = current_app.config.get("ADMIN_TOKEN")
        provided = request.headers.get("X-Admin-Token", "")
        if not expected or not compare_digest(provided, expected):
            raise AppError("Não autorizado", 401)
        return function(*args, **kwargs)

    return wrapped
