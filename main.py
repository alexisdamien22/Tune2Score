# main.py
import os
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import Response, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

from config import engine, init_db  
from app.models import User, AudioFile, Score
from core.audio_processor import analyze_audio_file
from core.music_quantizer import quantize_sequence
from core.svg_generator import generate_svg_score

app = FastAPI()

# --- CONFIGURATION DES DOSSIERS STATIQUES ET TEMPLATES ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = 'pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

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

# --- ROUTE FRONTEND : PAGE D'ACCUEIL ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Affiche la page du convertisseur en utilisant les templates Jinja2"""
    return templates.TemplateResponse("index.html", {"request": request})

# --- ROUTES API ---
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

        base_name = os.path.splitext(audio.filename)[0]
        temp_svg_path = os.path.join(PDF_FOLDER, f"{base_name}.svg")
        pdf_path = os.path.join(PDF_FOLDER, f"{base_name}.pdf")

        with open(temp_svg_path, "w", encoding="utf-8") as f:
            f.write(LAST_GENERATED_SVG)

        drawing = svg2rlg(temp_svg_path)
        renderPDF.drawToFile(drawing, pdf_path)
        
        if os.path.exists(temp_svg_path):
            os.remove(temp_svg_path)

        db_score = Score(
            audio_file_id=db_audio.id,
            tempo_bpm=tempo,
            time_signature=time_signature,
            musical_data=json.dumps(final_sequence),
            pdf_path=pdf_path
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
            "svg_url": "http://127.0.0.1:8000/api/view-svg",
            "pdf_url": f"http://127.0.0.1:8000/api/download-pdf/{db_score.id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur durant le traitement : {str(e)}")

@app.get("/api/view-svg")
async def view_svg():
    global LAST_GENERATED_SVG
    if not LAST_GENERATED_SVG:
        return Response(content="Aucune partition générée.", status_code=404)
    return Response(content=LAST_GENERATED_SVG, media_type="image/svg+xml")

@app.get("/api/download-pdf/{score_id}")
async def download_pdf(score_id: int, db: Session = Depends(get_session)):
    score = db.get(Score, score_id)
    if not score or score.pdf_path == "not_generated_yet" or not os.path.exists(score.pdf_path):
        raise HTTPException(status_code=404, detail="Fichier PDF introuvable.")
    
    return FileResponse(
        path=score.pdf_path, 
        filename=os.path.basename(score.pdf_path), 
        media_type="application/pdf"
    )