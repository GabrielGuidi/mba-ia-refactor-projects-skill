from flask import Blueprint, jsonify, request

from controllers import user_controller
from middlewares.auth import authenticated


user_bp = Blueprint("users", __name__)


@user_bp.get("/users")
@authenticated(admin=True)
def get_users(): return jsonify(user_controller.list_users())


@user_bp.get("/users/<int:user_id>")
@authenticated()
def get_user(user_id): return jsonify(user_controller.get_user(user_id))


@user_bp.post("/users")
@authenticated(admin=True)
def create_user(): return jsonify(user_controller.create_user(request.get_json(silent=True))), 201


@user_bp.put("/users/<int:user_id>")
@authenticated(admin=True)
def update_user(user_id): return jsonify(user_controller.update_user(user_id, request.get_json(silent=True)))


@user_bp.delete("/users/<int:user_id>")
@authenticated(admin=True)
def delete_user(user_id):
    user_controller.delete_user(user_id)
    return jsonify({"message": "Usuário deletado com sucesso"})


@user_bp.get("/users/<int:user_id>/tasks")
@authenticated()
def get_user_tasks(user_id): return jsonify(user_controller.user_tasks(user_id))


@user_bp.post("/login")
def login(): return jsonify(user_controller.login(request.get_json(silent=True)))
