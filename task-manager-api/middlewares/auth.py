from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database import db
from middlewares.error_handler import AppError
from models.user import User


def create_token(user):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user.id, "role": user.role})


def authenticated(admin=False):
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            token = request.headers.get("Authorization", "").removeprefix("Bearer ")
            try:
                data = URLSafeTimedSerializer(current_app.config["SECRET_KEY"]).loads(
                    token, max_age=86400
                )
            except (BadSignature, SignatureExpired):
                raise AppError("Não autorizado", 401)
            user = db.session.get(User, data["user_id"])
            if not user or not user.active or (admin and user.role != "admin"):
                raise AppError("Acesso negado", 403)
            g.current_user = user
            return function(*args, **kwargs)

        return wrapped

    return decorator
