from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = "webboard-local-lab-secret-key"

    DATABASE = str(
        BASE_DIR / "instance" / "webboard.db"
    )

    DEBUG = True