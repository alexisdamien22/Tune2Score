from fastapi import FastAPI
import sqlmodel
import librosa

app = FastAPI()

@app.get("/")
def test_route():
    return {
        "status": "Success", 
        "librosa_version": librosa.__version__,
        "sqlmodel_status": "Loaded"
    }