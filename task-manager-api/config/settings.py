import os


def load_settings():
    return {
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL", "sqlite:///tasks.db"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "DEBUG": os.getenv("FLASK_DEBUG", "0") == "1",
    }
