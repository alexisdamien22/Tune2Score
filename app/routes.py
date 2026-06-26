# app/routes.py
import os
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import Response, FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import Session, select
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

from config import engine
from app.models import User, AudioFile, Score
from core.audio_processor import analyze_audio_file
from core.music_quantizer import quantize_sequence
from core.svg_generator import generate_svg_score

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = 'pdfs'
LAST_GENERATED_SVG = ""

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Affiche la page d'accueil (Convertisseur)"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def view_register(request: Request):
    """Affiche la page d'inscription"""
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def view_login(request: Request):
    """Affiche la page de connexion"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/history", response_class=HTMLResponse)
async def view_history(request: Request):
    """Affiche la page d'historique des partitions"""
    return templates.TemplateResponse("history.html", {"request": request})


# --- ROUTES API (AUTHENTIFICATION) ---

@router.post("/api/register")
async def api_register(user_data: UserRegister, db: Session = Depends(get_session)):
    """API d'inscription"""
    existing_user = db.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris.")
        
    existing_email = db.exec(select(User).where(User.email == user_data.email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Cette adresse email est déjà enregistrée.")

    fake_hashed_password = f"hashed_{user_data.password}" 
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=fake_hashed_password
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"status": "success", "message": "Utilisateur créé avec succès", "user_id": new_user.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")

@router.post("/api/login")
async def api_login(credentials: UserLogin, db: Session = Depends(get_session)):
    """API pour connecter un utilisateur"""
    user = db.exec(
        select(User).where(
            (User.username == credentials.username) | (User.email == credentials.username)
        )
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Identifiants incorrects (utilisateur introuvable).")
        
    expected_hash = f"hashed_{credentials.password}"
    if user.password_hash != expected_hash:
        raise HTTPException(status_code=400, detail="Identifiants incorrects (mot de passe invalide).")
        
    return {
        "status": "success",
        "message": "Connexion réussie",
        "user": {
            "username": user.username,
            "email": user.email
        }
    }

@router.get("/api/history/{username}")
async def get_user_history(username: str, db: Session = Depends(get_session)):
    """Récupère l'historique des partitions d'un utilisateur spécifique"""
    user = db.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    statement = (
        select(Score, AudioFile.file_name)
        .join(AudioFile, Score.audio_file_id == AudioFile.id)
        .where(AudioFile.user_id == user.id)
        .order_by(Score.id.desc())
    )
    results = db.exec(statement).all()

    history_list = []
    for score, file_name in results:
        history_list.append({
            "id": score.id,
            "file_name": file_name,
            "tempo": score.tempo_bpm,
            "time_signature": score.time_signature,
            "pdf_url": f"http://127.0.0.1:8000/api/download-pdf/{score.id}"
        })

    return {"status": "success", "history": history_list}

@router.post("/api/upload")
async def upload_audio(
    audio: UploadFile = File(...),
    tempo: int = Form(120),
    time_signature: str = Form("4/4"),
    username: str = Form(...),
    db: Session = Depends(get_session)
):
    """API d'envoi, de conversion musicale et d'enregistrement (Sécurisée)"""
    if not username or username == "alexis_test":
        raise HTTPException(
            status_code=401, 
            detail="Action non autorisée. Vous devez créer un compte et être connecté pour convertir un fichier."
        )

    global LAST_GENERATED_SVG

    file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await audio.read())

    try:
        raw_sequence = analyze_audio_file(file_path)
        final_sequence = quantize_sequence(raw_sequence, bpm=tempo)
        LAST_GENERATED_SVG = generate_svg_score(final_sequence)

        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé pour l'association du fichier.")

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

        try:
            drawing = svg2rlg(temp_svg_path)
            renderPDF.drawToFile(drawing, pdf_path)
        except Exception as pdf_err:
            print(f"Erreur lors de la génération PDF : {str(pdf_err)}")
        finally:
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
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur durant le traitement : {str(e)}")

@router.get("/api/view-svg")
async def view_svg():
    """Permet au Frontend d'afficher le rendu de la dernière partition demandée"""
    global LAST_GENERATED_SVG
    if not LAST_GENERATED_SVG:
        return Response(content="Aucune partition générée.", status_code=404)
    return Response(content=LAST_GENERATED_SVG, media_type="image/svg+xml")

@router.get("/api/download-pdf/{score_id}")
async def download_pdf(score_id: int, db: Session = Depends(get_session)):
    """Permet le téléchargement physique d'un rapport de partition PDF depuis l'historique ou l'accueil"""
    score = db.get(Score, score_id)
    if not score or score.pdf_path == "not_generated_yet" or not os.path.exists(score.pdf_path):
        raise HTTPException(status_code=404, detail="Fichier PDF introuvable.")
    
    return FileResponse(
        path=score.pdf_path, 
        filename=os.path.basename(score.pdf_path), 
        media_type="application/pdf"
    )