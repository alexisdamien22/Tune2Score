# main.py
import os
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

# Nos modules
from config import engine, init_db
from app.models import User, AudioFile, Score
from core.audio_processor import analyze_audio_file
from core.music_quantizer import quantize_sequence
from core.svg_generator import generate_svg_score

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LAST_GENERATED_SVG = ""

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

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/api/upload")
async def upload_audio(
    audio: UploadFile = File(...),
    tempo: int = Form(120),
    time_signature: str = Form("4/4"),
    db: Session = Depends(get_session)
):
    global LAST_GENERATED_SVG

    file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await audio.read())

    try:
        raw_sequence = analyze_audio_file(file_path)
        final_sequence = quantize_sequence(raw_sequence, bpm=tempo)
        LAST_GENERATED_SVG = generate_svg_score(final_sequence)

        user = db.exec(select(User).where(User.username == "alexis_test")).one()

        db_audio = AudioFile(
            user_id=user.id,
            file_name=audio.filename,
            file_path=file_path,
            duration_seconds=raw_sequence[-1]["start_time_seconds"] if raw_sequence else 0.0
        )
        db.add(db_audio)
        db.commit()
        db.refresh(db_audio)

        db_score = Score(
            audio_file_id=db_audio.id,
            tempo_bpm=tempo,
            time_signature=time_signature,
            musical_data=json.dumps(final_sequence),
            pdf_path="not_generated_yet"
        )
        db.add(db_score)
        db.commit()

        return {
            "metadata": {
                "file_name": audio.filename,
                "user_tempo_bpm": tempo,
                "time_signature": time_signature,
                "saved_in_db": True
            },
            "sequence": final_sequence,
            "svg_url": "http://127.0.0.1:8000/api/view-svg"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur durant le traitement : {str(e)}")

@app.get("/api/view-svg")
async def view_svg():
    global LAST_GENERATED_SVG
    if not LAST_GENERATED_SVG:
        return Response(content="Aucune partition générée.", status_code=404)
    return Response(content=LAST_GENERATED_SVG, media_type="image/svg+xml")