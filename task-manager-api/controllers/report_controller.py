from datetime import timedelta

from database import db
from middlewares.error_handler import AppError
from models.category import Category
from models.task import Task
from models.user import User
from utils.time import utc_now


def summary():
    tasks = db.session.scalars(db.select(Task)).all()
    users = db.session.scalars(db.select(User)).all()
    status_counts = {status: 0 for status in ("pending", "in_progress", "done", "cancelled")}
    priority_counts = {priority: 0 for priority in range(1, 6)}
    overdue = []
    user_counts = {user.id: [0, 0] for user in users}
    for task in tasks:
        status_counts[task.status] += 1
        priority_counts[task.priority] += 1
        if task.user_id in user_counts:
            user_counts[task.user_id][0] += 1
            user_counts[task.user_id][1] += task.status == "done"
        if task.is_overdue():
            overdue.append({"id": task.id, "title": task.title, "due_date": str(task.due_date), "days_overdue": (utc_now() - task.due_date).days})
    seven_days_ago = utc_now() - timedelta(days=7)
    return {
        "generated_at": str(utc_now()),
        "overview": {"total_tasks": len(tasks), "total_users": len(users), "total_categories": db.session.scalar(db.select(db.func.count(Category.id)))},
        "tasks_by_status": status_counts,
        "tasks_by_priority": dict(zip(("critical", "high", "medium", "low", "minimal"), priority_counts.values())),
        "overdue": {"count": len(overdue), "tasks": overdue},
        "recent_activity": {
            "tasks_created_last_7_days": sum(task.created_at >= seven_days_ago for task in tasks),
            "tasks_completed_last_7_days": sum(task.status == "done" and task.updated_at >= seven_days_ago for task in tasks),
        },
        "user_productivity": [
            {"user_id": user.id, "user_name": user.name, "total_tasks": user_counts[user.id][0], "completed_tasks": user_counts[user.id][1], "completion_rate": round(user_counts[user.id][1] / user_counts[user.id][0] * 100, 2) if user_counts[user.id][0] else 0}
            for user in users
        ],
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise AppError("Usuário não encontrado", 404)
    tasks = list(user.tasks)
    counts = {status: sum(task.status == status for task in tasks) for status in ("done", "pending", "in_progress", "cancelled")}
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": dict(
            total_tasks=len(tasks),
            **counts,
            overdue=sum(task.is_overdue() for task in tasks),
            high_priority=sum(task.priority <= 2 for task in tasks),
            completion_rate=round(counts["done"] / len(tasks) * 100, 2) if tasks else 0,
        ),
    }


def list_categories():
    statement = db.select(Category, db.func.count(Task.id)).outerjoin(Task).group_by(Category.id)
    return [dict(category.to_dict(), task_count=count) for category, count in db.session.execute(statement)]


def create_category(data):
    values = _category_values(data)
    category = Category(**values)
    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(category_id, data):
    category = _find_category(category_id)
    for key, value in _category_values(data, partial=True).items():
        setattr(category, key, value)
    db.session.commit()
    return category.to_dict()


def delete_category(category_id):
    db.session.delete(_find_category(category_id))
    db.session.commit()


def _find_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        raise AppError("Categoria não encontrada", 404)
    return category


def _category_values(data, partial=False):
    if not data or (not partial and not data.get("name")):
        raise AppError("Nome é obrigatório")
    result = {key: data[key] for key in ("name", "description") if key in data}
    if "color" in data:
        color = data["color"]
        if not isinstance(color, str) or len(color) != 7 or not color.startswith("#"):
            raise AppError("Cor inválida")
        result["color"] = color
    elif not partial:
        result["color"] = "#000000"
    return result
