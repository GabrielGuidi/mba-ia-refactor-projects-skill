from werkzeug.security import check_password_hash, generate_password_hash

from src.database import get_db


PUBLIC_FIELDS = "id, nome, email, tipo, criado_em"


def list_all():
    rows = get_db().execute(f"SELECT {PUBLIC_FIELDS} FROM usuarios").fetchall()
    return [dict(row) for row in rows]


def find_by_id(user_id):
    row = get_db().execute(
        f"SELECT {PUBLIC_FIELDS} FROM usuarios WHERE id = ?", (user_id,)
    ).fetchone()
    return dict(row) if row else None


def create(name, email, password, user_type="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (name, email, generate_password_hash(password), user_type),
    )
    db.commit()
    return cursor.lastrowid


def authenticate(email, password):
    row = get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not row or not check_password_hash(row["senha"], password):
        return None
    return {field: row[field] for field in ("id", "nome", "email", "tipo")}
