# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

# Nos modules de configuration
from config import engine, init_db
from app.models import User
from app.routes import router as main_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs('uploads', exist_ok=True)
os.makedirs('pdfs', exist_ok=True)

@app.on_event("startup")
def on_startup():
    init_db()
    with Session(engine) as session:
        statement = select(User).where(User.username == "alexis_test")
        user = session.exec(statement).first()
        if not user:
            test_user = User(
                username="alexis_test",
                email="alexis@test.com",
                password_hash="fake_hash_for_now"
            )
            session.add(test_user)
            session.commit()

app.include_router(main_router)