def quantize_sequence(raw_sequence, bpm):
    """
    Prend la séquence brute en secondes et traduit les durées ET les départs
    en temps musicaux (beats) en fonction du BPM.
    """
    if bpm <= 0:
        bpm = 120
        
    crotchet_duration = 60.0 / bpm
    
    NOTE_TYPES = [
        {"name": "ronde", "beats": 4.0},
        {"name": "blanche", "beats": 2.0},
        {"name": "noire", "beats": 1.0},
        {"name": "croche", "beats": 0.5},
        {"name": "double-croche", "beats": 0.25}
    ]
    
    quantized_sequence = []
    current_beat_cursor = 0.0

    for item in raw_sequence:
        duration_sec = item["duration_seconds"]
        
        exact_beats = duration_sec / crotchet_duration
        
        closest_type = min(NOTE_TYPES, key=lambda x: abs(x["beats"] - exact_beats))
        quantized_beats = closest_type["beats"]
        
        quantized_item = {
            "start_time_seconds": item["start_time_seconds"],
            "duration_seconds": duration_sec,
            "frequency": item["frequency"],
            "note": item["note"],
            
            "start_beat": current_beat_cursor,
            "duration_beat": quantized_beats,
            "note_type": closest_type["name"]
        }
        
        quantized_sequence.append(quantized_item)
        
        current_beat_cursor += quantized_beats
        
    return quantized_sequence