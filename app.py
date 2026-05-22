import os
from flask import Flask, request, jsonify
from core.audio_processor import analyze_audio_file
from core.music_quantizer import quantize_sequence # <-- Import du nouveau module

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "Aucun fichier audio fourni"}), 400
        
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400

    # Récupération sécurisée du tempo envoyé par l'utilisateur
    tempo = request.form.get('tempo', default=120, type=int)
    time_signature = request.form.get('time_signature', default='4/4', type=str)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        # 1. Extraction brute des fréquences (en secondes)
        raw_sequence = analyze_audio_file(file_path)
        
        # 2. QUANTIFICATION (Traduction des secondes en notes de musique)
        final_sequence = quantize_sequence(raw_sequence, bpm=tempo)

        return jsonify({
            "metadata": {
                "file_name": file.filename,
                "user_tempo_bpm": tempo,
                "time_signature": time_signature
            },
            "sequence": final_sequence
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erreur durant le traitement : {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)