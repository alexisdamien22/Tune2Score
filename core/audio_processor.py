import librosa
import numpy as np

def hz_to_note_name(hz):
    """Convertit une fréquence en notation internationale (ex: 261.63 -> C4)"""
    if hz <= 0 or np.isnan(hz):
        return "Silence"
    return librosa.hz_to_note(hz)

def analyze_audio_file(file_path):
    y, sr = librosa.load(file_path, sr=None)
    
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    duration_total = librosa.get_duration(y=y, sr=sr)
    note_timestamps = np.append(onset_times, duration_total)

    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, 
        fmin=librosa.note_to_hz('C2'), 
        fmax=librosa.note_to_hz('C7'), 
        sr=sr
    )
    times_f0 = librosa.times_like(f0, sr=sr)

    sequence = []

    for i in range(len(note_timestamps) - 1):
        start_time = note_timestamps[i]
        end_time = note_timestamps[i+1]
        duration = end_time - start_time
        
        if duration < 0.1:
            continue
            
        indices = np.where((times_f0 >= start_time) & (times_f0 < end_time))[0]
        
        if len(indices) > 0:
            segment_pitches = f0[indices]
            valid_pitches = segment_pitches[~np.isnan(segment_pitches)]
            
            if len(valid_pitches) > 0:
                mean_hz = float(np.median(valid_pitches))
                note_name = hz_to_note_name(mean_hz)
            else:
                mean_hz = 0
                note_name = "Silence"
        else:
            mean_hz = 0
            note_name = "Silence"

        sequence.append({
            "start_time_seconds": round(start_time, 2),
            "duration_seconds": round(duration, 2),
            "frequency": round(mean_hz, 2) if mean_hz > 0 else None,
            "note": note_name
        })

    return sequence