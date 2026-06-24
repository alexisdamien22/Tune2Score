# config.py
import os
from sqlmodel import create_engine, SQLModel
from dotenv import load_dotenv

# Charge les variables d'environnement du fichier .env
load_dotenv()

# os.getenv va chercher la valeur de DATABASE_URL définie dans ton fichier .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas configurée dans le fichier .env")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Crée les tables dans PostgreSQL si elles n'existent pas encore"""
    from app.models import User, AudioFile, Score
    SQLModel.metadata.create_all(engine)