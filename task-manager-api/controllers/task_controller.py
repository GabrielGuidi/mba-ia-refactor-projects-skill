from datetime import datetime

from sqlalchemy import func

from database import db
from middlewares.error_handler import AppError
from models.category import Category
from models.task import Task
from models.user import User
from utils.time import utc_now


VALID_STATUSES = {"pending", "in_progress", "done", "cancelled"}


def serialize(task):
    data = task.to_dict()
    data.update(
        overdue=task.is_overdue(),
        user_name=task.user.name if task.user else None,
        category_name=task.category.name if task.category else None,
    )
    return data


def list_tasks():
    return [serialize(task) for task in db.session.scalars(db.select(Task)).all()]


def get_task(task_id):
    return serialize(_find(task_id))


def create_task(data):
    values = _validate(data, require_title=True)
    task = Task(**values)
    db.session.add(task)
    db.session.commit()
    return task.to_dict()


def update_task(task_id, data):
    task = _find(task_id)
    for key, value in _validate(data).items():
        setattr(task, key, value)
    task.updated_at = utc_now()
    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    db.session.delete(_find(task_id))
    db.session.commit()


def search_tasks(arguments):
    statement = db.select(Task)
    term = arguments.get("q")
    if term:
        statement = statement.where(db.or_(Task.title.contains(term), Task.description.contains(term)))
    if arguments.get("status"):
        statement = statement.where(Task.status == arguments["status"])
    for field, column in (("priority", Task.priority), ("user_id", Task.user_id)):
        if arguments.get(field):
            try:
                statement = statement.where(column == int(arguments[field]))
            except ValueError as error:
                raise AppError(f"{field} inválido") from error
    return [serialize(task) for task in db.session.scalars(statement).all()]


def stats():
    counts = dict(
        db.session.execute(db.select(Task.status, func.count()).group_by(Task.status)).all()
    )
    total = sum(counts.values())
    overdue = sum(task.is_overdue() for task in db.session.scalars(db.select(Task)).all())
    done = counts.get("done", 0)
    return {
        "total": total,
        "pending": counts.get("pending", 0),
        "in_progress": counts.get("in_progress", 0),
        "done": done,
        "cancelled": counts.get("cancelled", 0),
        "overdue": overdue,
        "completion_rate": round(done / total * 100, 2) if total else 0,
    }


def _find(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise AppError("Task não encontrada", 404)
    return task


def _validate(data, require_title=False):
    if not data:
        raise AppError("Dados inválidos")
    result = {}
    if require_title and not data.get("title"):
        raise AppError("Título é obrigatório")
    if "title" in data:
        title = data["title"].strip()
        if not 3 <= len(title) <= 200:
            raise AppError("Título deve ter entre 3 e 200 caracteres")
        result["title"] = title
    if "description" in data:
        result["description"] = data["description"]
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            raise AppError("Status inválido")
        result["status"] = data["status"]
    if "priority" in data:
        try:
            priority = int(data["priority"])
        except (TypeError, ValueError) as error:
            raise AppError("Prioridade inválida") from error
        if not 1 <= priority <= 5:
            raise AppError("Prioridade deve ser entre 1 e 5")
        result["priority"] = priority
    for field, model, label in (("user_id", User, "Usuário"), ("category_id", Category, "Categoria")):
        if field in data:
            value = data[field]
            if value and not db.session.get(model, value):
                raise AppError(f"{label} não encontrado", 404)
            result[field] = value
    if "due_date" in data:
        try:
            result["due_date"] = datetime.strptime(data["due_date"], "%Y-%m-%d") if data["due_date"] else None
        except ValueError as error:
            raise AppError("Formato de data inválido. Use YYYY-MM-DD") from error
    if "tags" in data:
        result["tags"] = ",".join(data["tags"]) if isinstance(data["tags"], list) else data["tags"]
    return result
