import os


def load_settings():
    return {
        "DATABASE_PATH": os.getenv("DATABASE_PATH", "loja.db"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "ADMIN_TOKEN": os.getenv("ADMIN_TOKEN"),
        "DEBUG": os.getenv("FLASK_DEBUG", "0") == "1",
    }
