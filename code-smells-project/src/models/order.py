from src.database import get_db


def create(user_id, items):
    db = get_db()
    total = 0
    products = []
    try:
        db.execute("BEGIN")
        for item in items:
            product = db.execute(
                "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            if product is None:
                raise ValueError(f"Produto {item['produto_id']} não encontrado")
            if product["estoque"] < item["quantidade"]:
                raise ValueError(f"Estoque insuficiente para {product['nome']}")
            products.append((item, product))
            total += product["preco"] * item["quantidade"]

        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (user_id, total),
        )
        order_id = cursor.lastrowid
        for item, product in products:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (order_id, item["produto_id"], item["quantidade"], product["preco"]),
            )
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        db.commit()
        return {"pedido_id": order_id, "total": total}
    except Exception:
        db.rollback()
        raise


def list_all(user_id=None):
    db = get_db()
    where = "WHERE p.usuario_id = ?" if user_id is not None else ""
    parameters = (user_id,) if user_id is not None else ()
    rows = db.execute(
        f"""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
        {where}
        ORDER BY p.id, i.id
        """,
        parameters,
    ).fetchall()
    return _group_orders(rows)


def _group_orders(rows):
    orders = {}
    for row in rows:
        order = orders.setdefault(
            row["id"],
            {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            },
        )
        if row["produto_id"] is not None:
            order["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return list(orders.values())


def update_status(order_id, status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, order_id))
    db.commit()


def sales_report():
    row = get_db().execute(
        """
        SELECT COUNT(*) AS total_pedidos, COALESCE(SUM(total), 0) AS faturamento,
               SUM(status = 'pendente') AS pendentes,
               SUM(status = 'aprovado') AS aprovados,
               SUM(status = 'cancelado') AS cancelados
        FROM pedidos
        """
    ).fetchone()
    revenue = row["faturamento"]
    discount = revenue * (0.1 if revenue > 10000 else 0.05 if revenue > 5000 else 0.02 if revenue > 1000 else 0)
    count = row["total_pedidos"]
    return {
        "total_pedidos": count,
        "faturamento_bruto": round(revenue, 2),
        "desconto_aplicavel": round(discount, 2),
        "faturamento_liquido": round(revenue - discount, 2),
        "pedidos_pendentes": row["pendentes"],
        "pedidos_aprovados": row["aprovados"],
        "pedidos_cancelados": row["cancelados"],
        "ticket_medio": round(revenue / count, 2) if count else 0,
    }
