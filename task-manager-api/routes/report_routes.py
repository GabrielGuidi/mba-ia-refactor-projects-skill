from flask import Blueprint, jsonify, request

from controllers import report_controller
from middlewares.auth import authenticated


report_bp = Blueprint("reports", __name__)


@report_bp.get("/reports/summary")
def summary_report(): return jsonify(report_controller.summary())


@report_bp.get("/reports/user/<int:user_id>")
@authenticated()
def user_report(user_id): return jsonify(report_controller.user_report(user_id))


@report_bp.get("/categories")
def get_categories(): return jsonify(report_controller.list_categories())


@report_bp.post("/categories")
@authenticated(admin=True)
def create_category(): return jsonify(report_controller.create_category(request.get_json(silent=True))), 201


@report_bp.put("/categories/<int:category_id>")
@authenticated(admin=True)
def update_category(category_id): return jsonify(report_controller.update_category(category_id, request.get_json(silent=True)))


@report_bp.delete("/categories/<int:category_id>")
@authenticated(admin=True)
def delete_category(category_id):
    report_controller.delete_category(category_id)
    return jsonify({"message": "Categoria deletada"})
