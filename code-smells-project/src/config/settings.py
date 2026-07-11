import os


def load_settings():
    return {
        "DATABASE_PATH": os.getenv("DATABASE_PATH", "loja.db"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "DEBUG": os.getenv("FLASK_DEBUG", "0") == "1",
    }
