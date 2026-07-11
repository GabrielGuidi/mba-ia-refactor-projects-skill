import re

from database import db
from middlewares.auth import create_token
from middlewares.error_handler import AppError
from models.task import Task
from models.user import User


VALID_ROLES = {"user", "admin", "manager"}


def list_users():
    statement = db.select(User, db.func.count(Task.id)).outerjoin(Task).group_by(User.id)
    return [dict(user.to_dict(), task_count=count) for user, count in db.session.execute(statement)]


def get_user(user_id):
    user = _find(user_id)
    return dict(user.to_dict(), tasks=[task.to_dict() for task in user.tasks])


def create_user(data):
    values = _validate(data, require_password=True)
    user = User(name=values["name"], email=values["email"], role=values["role"])
    user.set_password(values["password"])
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def update_user(user_id, data):
    user = _find(user_id)
    values = _validate(data, partial=True, current_user_id=user_id)
    password = values.pop("password", None)
    for key, value in values.items():
        setattr(user, key, value)
    if password:
        user.set_password(password)
    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = _find(user_id)
    for task in list(user.tasks):
        db.session.delete(task)
    db.session.delete(user)
    db.session.commit()


def user_tasks(user_id):
    return [task.to_dict() | {"overdue": task.is_overdue()} for task in _find(user_id).tasks]


def login(data):
    if not data or not data.get("email") or not data.get("password"):
        raise AppError("Email e senha são obrigatórios")
    user = db.session.scalar(db.select(User).where(User.email == data["email"]))
    if not user or not user.check_password(data["password"]):
        raise AppError("Credenciais inválidas", 401)
    if not user.active:
        raise AppError("Usuário inativo", 403)
    return {"message": "Login realizado com sucesso", "user": user.to_dict(), "token": create_token(user)}


def _find(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise AppError("Usuário não encontrado", 404)
    return user


def _validate(data, require_password=False, partial=False, current_user_id=None):
    if not data:
        raise AppError("Dados inválidos")
    result = {}
    required = () if partial else ("name", "email")
    if require_password:
        required += ("password",)
    if any(not data.get(field) for field in required):
        raise AppError("Nome, email e senha são obrigatórios")
    if "name" in data:
        result["name"] = data["name"].strip()
    if "email" in data:
        email = data["email"].strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise AppError("Email inválido")
        existing = db.session.scalar(db.select(User).where(User.email == email))
        if existing and existing.id != current_user_id:
            raise AppError("Email já cadastrado", 409)
        result["email"] = email
    if "password" in data:
        if len(data["password"]) < 8:
            raise AppError("Senha deve ter no mínimo 8 caracteres")
        result["password"] = data["password"]
    if "role" in data:
        if data["role"] not in VALID_ROLES:
            raise AppError("Role inválido")
        result["role"] = data["role"]
    elif not partial:
        result["role"] = "user"
    if "active" in data:
        result["active"] = bool(data["active"])
    return result
