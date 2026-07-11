from src.middlewares.error_handler import AppError
from src.models import product


VALID_CATEGORIES = {"informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"}


def list_products():
    return {"dados": product.list_all(), "sucesso": True}, 200


def get_product(product_id):
    found = product.find_by_id(product_id)
    if not found:
        raise AppError("Produto não encontrado", 404)
    return {"dados": found, "sucesso": True}, 200


def create_product(data):
    values = _validate(data)
    product_id = product.create(*values)
    return {"dados": {"id": product_id}, "sucesso": True, "mensagem": "Produto criado"}, 201


def update_product(product_id, data):
    if not product.find_by_id(product_id):
        raise AppError("Produto não encontrado", 404)
    product.update(product_id, *_validate(data))
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def delete_product(product_id):
    if not product.find_by_id(product_id):
        raise AppError("Produto não encontrado", 404)
    product.delete(product_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200


def search_products(arguments):
    try:
        min_price = float(arguments["preco_min"]) if arguments.get("preco_min") else None
        max_price = float(arguments["preco_max"]) if arguments.get("preco_max") else None
    except ValueError as error:
        raise AppError("Preço inválido") from error
    results = product.search(arguments.get("q", ""), arguments.get("categoria"), min_price, max_price)
    return {"dados": results, "total": len(results), "sucesso": True}, 200


def _validate(data):
    if not data:
        raise AppError("Dados inválidos")
    for field, label in (("nome", "Nome"), ("preco", "Preço"), ("estoque", "Estoque")):
        if field not in data:
            raise AppError(f"{label} é obrigatório")
    name = data["nome"]
    if not isinstance(name, str) or not 2 <= len(name) <= 200:
        raise AppError("Nome deve ter entre 2 e 200 caracteres")
    try:
        price = float(data["preco"])
        stock = int(data["estoque"])
    except (TypeError, ValueError) as error:
        raise AppError("Preço e estoque devem ser numéricos") from error
    if price < 0 or stock < 0:
        raise AppError("Preço e estoque não podem ser negativos")
    category = data.get("categoria", "geral")
    if category not in VALID_CATEGORIES:
        raise AppError("Categoria inválida")
    return name, data.get("descricao", ""), price, stock, category
