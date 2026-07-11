import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def initialize_database():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            status TEXT DEFAULT 'pendente',
            total REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL
        );
        """
    )
    _seed_if_empty(db)
    _hash_legacy_passwords(db)


def _seed_if_empty(db):
    if db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] != 0:
        return

    products = [
        ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
        ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
        ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
        ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
        ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
        ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
        ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
        ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
        ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
        ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
    ]
    db.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        products,
    )

    from werkzeug.security import generate_password_hash

    users = [
        ("Admin", "admin@loja.com", generate_password_hash("admin123"), "admin"),
        ("João Silva", "joao@email.com", generate_password_hash("123456"), "cliente"),
        ("Maria Santos", "maria@email.com", generate_password_hash("senha123"), "cliente"),
    ]
    db.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", users
    )
    db.commit()


def _hash_legacy_passwords(db):
    from werkzeug.security import generate_password_hash

    rows = db.execute("SELECT id, senha FROM usuarios").fetchall()
    for row in rows:
        if not row["senha"].startswith(("scrypt:", "pbkdf2:")):
            db.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (generate_password_hash(row["senha"]), row["id"]),
            )
    db.commit()
