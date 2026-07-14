from src.database import get_db
from src.middlewares.error_handler import AppError


ALLOWED_QUERIES = {
    "SELECT 1",
    "SELECT COUNT(*) FROM produtos",
    "SELECT COUNT(*) FROM usuarios",
    "SELECT COUNT(*) FROM pedidos",
}


def reset_database():
    db = get_db()
    for table in ("itens_pedido", "pedidos", "produtos", "usuarios"):
        db.execute(f"DELETE FROM {table}")
    db.commit()
    return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200


def execute_diagnostic(data):
    query = data.get("sql", "").strip() if data else ""
    if query not in ALLOWED_QUERIES:
        raise AppError("Query administrativa não permitida", 400)
    rows = get_db().execute(query).fetchall()
    result = [dict(row) for row in rows]
    return {"dados": result, "sucesso": True}, 200
