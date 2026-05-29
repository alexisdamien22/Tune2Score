# app.py
import os
from flask import Flask, request, jsonify, Response
from core.audio_processor import analyze_audio_file
from core.music_quantizer import quantize_sequence
from core.svg_generator import generate_svg_score

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

LAST_GENERATED_SVG = ""

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    global LAST_GENERATED_SVG
    
    if 'audio' not in request.files:
        return jsonify({"error": "Aucun fichier audio fourni"}), 400
        
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400

    tempo = request.form.get('tempo', default=120, type=int)
    time_signature = request.form.get('time_signature', default='4/4', type=str)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        raw_sequence = analyze_audio_file(file_path)
        final_sequence = quantize_sequence(raw_sequence, bpm=tempo)
        
        LAST_GENERATED_SVG = generate_svg_score(final_sequence)

        return jsonify({
            "metadata": {
                "file_name": file.filename,
                "user_tempo_bpm": tempo,
                "time_signature": time_signature
            },
            "sequence": final_sequence,
            "svg_url": "http://127.0.0.1:5000/api/view-svg"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erreur durant le traitement : {str(e)}"}), 500

@app.route('/api/view-svg', methods=['GET'])
def view_svg():
    global LAST_GENERATED_SVG
    if not LAST_GENERATED_SVG:
        return "Aucune partition n'a encore été générée. Envoyez d'abord un fichier audio.", 404
        
    return Response(LAST_GENERATED_SVG, mimetype='image/svg+xml')

if __name__ == '__main__':
    app.run(debug=True, port=5000)