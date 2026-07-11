from src.middlewares.error_handler import AppError
from src.models import order, user


VALID_STATUSES = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}


def create_order(data):
    if not data or not data.get("usuario_id") or not data.get("itens"):
        raise AppError("Usuario ID e pelo menos 1 item são obrigatórios")
    if not user.find_by_id(data["usuario_id"]):
        raise AppError("Usuário não encontrado", 404)
    _validate_items(data["itens"])
    try:
        result = order.create(data["usuario_id"], data["itens"])
    except ValueError as error:
        raise AppError(str(error)) from error
    return {"dados": result, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201


def list_orders(user_id=None):
    return {"dados": order.list_all(user_id), "sucesso": True}, 200


def update_status(order_id, data):
    status = data.get("status") if data else None
    if status not in VALID_STATUSES:
        raise AppError("Status inválido")
    order.update_status(order_id, status)
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200


def sales_report():
    return {"dados": order.sales_report(), "sucesso": True}, 200


def _validate_items(items):
    for item in items:
        try:
            product_id = int(item["produto_id"])
            quantity = int(item["quantidade"])
        except (KeyError, TypeError, ValueError) as error:
            raise AppError("Item inválido") from error
        if product_id <= 0 or quantity <= 0:
            raise AppError("Produto e quantidade devem ser positivos")
        item["produto_id"] = product_id
        item["quantidade"] = quantity
