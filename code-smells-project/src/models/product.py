from src.database import get_db


def list_all():
    return [dict(row) for row in get_db().execute("SELECT * FROM produtos").fetchall()]


def find_by_id(product_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (product_id,)).fetchone()
    return dict(row) if row else None


def create(name, description, price, stock, category):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (name, description, price, stock, category),
    )
    db.commit()
    return cursor.lastrowid


def update(product_id, name, description, price, stock, category):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (name, description, price, stock, category, product_id),
    )
    db.commit()


def delete(product_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    db.commit()


def search(term="", category=None, min_price=None, max_price=None):
    clauses = ["1 = 1"]
    parameters = []
    if term:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        parameters.extend((f"%{term}%", f"%{term}%"))
    if category:
        clauses.append("categoria = ?")
        parameters.append(category)
    if min_price is not None:
        clauses.append("preco >= ?")
        parameters.append(min_price)
    if max_price is not None:
        clauses.append("preco <= ?")
        parameters.append(max_price)

    query = "SELECT * FROM produtos WHERE " + " AND ".join(clauses)
    return [dict(row) for row in get_db().execute(query, parameters).fetchall()]
