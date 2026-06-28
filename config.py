# config.py
import os
from sqlmodel import create_engine, SQLModel
from dotenv import load_dotenv
from sqlmodel import Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas configurée dans le fichier .env")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Crée les tables dans PostgreSQL si elles n'existent pas encore"""
    from app.models import User, AudioFile, Score
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session