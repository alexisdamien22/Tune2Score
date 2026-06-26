# core/music_quantizer.py

def quantize_duration(beat_duration: float):
    """Associe une durée en battements à une figure de note, y compris les versions pointées"""
    if beat_duration >= 3.5:
        return "ronde", 4.0, False
    elif beat_duration >= 2.6:
        return "blanche", 3.0, True
    elif beat_duration >= 1.75:
        return "blanche", 2.0, False
    elif beat_duration >= 1.3:
        return "noire", 1.5, True
    elif beat_duration >= 0.85:
        return "noire", 1.0, False
    elif beat_duration >= 0.6:
        return "croche", 0.75, True
    elif beat_duration >= 0.35:
        return "croche", 0.5, False
    else:
        return "double-croche", 0.25, False

def quantize_sequence(raw_sequence, bpm: int):
    if not raw_sequence:
        return []
        
    bps = bpm / 60.0
    quantized_sequence = []
    
    for i, note in enumerate(raw_sequence):
        start_beat = note["start_time_seconds"] * bps
        end_beat = note["end_time_seconds"] * bps
        duration_beats = end_beat - start_beat
        
        if i > 0:
            prev_end_beat = raw_sequence[i-1]["end_time_seconds"] * bps
            gap = start_beat - prev_end_beat
            if gap >= 0.35:
                label, val, dotted = quantize_duration(gap)
                quantized_sequence.append({
                    "type": "rest",
                    "duration": label,
                    "beats_value": val,
                    "dotted": dotted
                })
                
        label, val, dotted = quantize_duration(duration_beats)
        quantized_sequence.append({
            "type": "note",
            "pitch_midi": note["pitch_midi"],
            "duration": label,
            "beats_value": val,
            "dotted": dotted
        })
        
    return quantized_sequence