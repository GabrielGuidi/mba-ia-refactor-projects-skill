from sqlite3 import IntegrityError

from src.middlewares.error_handler import AppError
from src.models import user


def list_users():
    return {"dados": user.list_all(), "sucesso": True}, 200


def get_user(user_id):
    found = user.find_by_id(user_id)
    if not found:
        raise AppError("Usuário não encontrado", 404)
    return {"dados": found, "sucesso": True}, 200


def create_user(data):
    if not data or not all(data.get(field) for field in ("nome", "email", "senha")):
        raise AppError("Nome, email e senha são obrigatórios")
    try:
        user_id = user.create(data["nome"], data["email"], data["senha"])
    except IntegrityError as error:
        raise AppError("Email já cadastrado", 409) from error
    return {"dados": {"id": user_id}, "sucesso": True}, 201


def login(data):
    if not data or not data.get("email") or not data.get("senha"):
        raise AppError("Email e senha são obrigatórios")
    authenticated = user.authenticate(data["email"], data["senha"])
    if not authenticated:
        raise AppError("Email ou senha inválidos", 401)
    return {"dados": authenticated, "sucesso": True, "mensagem": "Login OK"}, 200
