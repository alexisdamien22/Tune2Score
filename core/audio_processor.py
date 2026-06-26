# core/audio_processor.py
import librosa
import numpy as np

def frequency_to_note_name(freq):
    """Convertit une fréquence enHz en nom de note MIDI occidental standard"""
    if freq <= 0 or np.isnan(freq):
        return None
    midi_num = round(12 * np.log2(freq / 440.0) + 69)
    return midi_num

def analyze_audio_file(file_path: str):
    """
    Analyse le fichier audio pour extraire la séquence temporelle des notes jouées
    Retourne une liste de dicts : [{"start_time_seconds", "end_time_seconds", "pitch_midi"}]
    """
    y, sr = librosa.load(file_path, sr=None)
    
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    duration = librosa.get_duration(y=y, sr=sr)
    if len(onset_times) == 0:
        return []
        
    boundaries = list(onset_times) + [duration]
    
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    raw_sequence = []
    
    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i+1]
        
        start_frame = librosa.time_to_frames(start, sr=sr)
        end_frame = max(start_frame + 1, librosa.time_to_frames(end, sr=sr))
        
        pitch_slice = pitches[:, start_frame:end_frame]
        mag_slice = magnitudes[:, start_frame:end_frame]
        
        if mag_slice.size > 0 and np.max(mag_slice) > 0.05:
            max_idx = np.unravel_index(np.argmax(mag_slice), mag_slice.shape)
            freq = pitch_slice[max_idx[0], max_idx[1]]
            
            midi_note = frequency_to_note_name(freq)
            if midi_note and 21 <= midi_note <= 108:
                raw_sequence.append({
                    "start_time_seconds": float(start),
                    "end_time_seconds": float(end),
                    "pitch_midi": int(midi_note)
                })
                
    return raw_sequence