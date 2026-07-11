from flask import Blueprint, current_app, jsonify, request

from src.controllers import order_controller, product_controller, user_controller
from src.database import get_db


api = Blueprint("api", __name__)


def respond(result):
    body, status = result
    return jsonify(body), status


@api.get("/")
def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


@api.get("/produtos")
def list_products():
    return respond(product_controller.list_products())


@api.get("/produtos/busca")
def search_products():
    return respond(product_controller.search_products(request.args))


@api.get("/produtos/<int:product_id>")
def get_product(product_id):
    return respond(product_controller.get_product(product_id))


@api.post("/produtos")
def create_product():
    return respond(product_controller.create_product(request.get_json(silent=True)))


@api.put("/produtos/<int:product_id>")
def update_product(product_id):
    return respond(product_controller.update_product(product_id, request.get_json(silent=True)))


@api.delete("/produtos/<int:product_id>")
def delete_product(product_id):
    return respond(product_controller.delete_product(product_id))


@api.get("/usuarios")
def list_users():
    return respond(user_controller.list_users())


@api.get("/usuarios/<int:user_id>")
def get_user(user_id):
    return respond(user_controller.get_user(user_id))


@api.post("/usuarios")
def create_user():
    return respond(user_controller.create_user(request.get_json(silent=True)))


@api.post("/login")
def login():
    return respond(user_controller.login(request.get_json(silent=True)))


@api.post("/pedidos")
def create_order():
    return respond(order_controller.create_order(request.get_json(silent=True)))


@api.get("/pedidos")
def list_orders():
    return respond(order_controller.list_orders())


@api.get("/pedidos/usuario/<int:user_id>")
def list_user_orders(user_id):
    return respond(order_controller.list_orders(user_id))


@api.put("/pedidos/<int:order_id>/status")
def update_order_status(order_id):
    return respond(order_controller.update_status(order_id, request.get_json(silent=True)))


@api.get("/relatorios/vendas")
def sales_report():
    return respond(order_controller.sales_report())


@api.get("/health")
def health():
    db = get_db()
    counts = {
        table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("produtos", "usuarios", "pedidos")
    }
    return jsonify(
        {
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": "1.0.0",
            "debug": current_app.debug,
        }
    )
