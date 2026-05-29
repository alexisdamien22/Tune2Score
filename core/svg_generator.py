# core/svg_generator.py
NOTE_Y_POSITIONS = {
    "C4": 140,  # Do (ligne supplémentaire sous la portée)
    "D4": 130,  # Ré
    "E4": 120,  # Mi (première ligne du bas)
    "F4": 110,  # Fa
    "G4": 100,  # Sol
    "A4": 90,   # La
    "B4": 80,   # Si
    "C5": 70,   # Do (haut)
    "D5": 60,   # Ré (haut)
    "E5": 50,   # Mi (haut)
    "F5": 40,   # Fa (haut)
}

def generate_svg_score(quantized_sequence):
    """
    Prend la séquence quantifiée et génère une chaîne de caractères au format SVG
    représentant la partition musicale.
    """
    width = 1000
    height = 200
    
    svg = f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '  <rect width="100%" height="100%" fill="white" />\n'
    
    for y_line in [40, 60, 80, 100, 120]:
        svg += f'  <line x1="50" y1="{y_line}" x2="{width - 50}" y2="{y_line}" stroke="black" stroke-width="1" />\n'
    
    svg += '  <line x1="50" y1="40" x2="50" y2="120" stroke="black" stroke-width="2" />\n'

    margin_left = 100
    beat_pixels = 60
    
    for item in quantized_sequence:
        note_name = item["note"]
        start_beat = item["start_beat"]
        
        if note_name == "Silence" or note_name not in NOTE_Y_POSITIONS:
            continue
            
        x = margin_left + (start_beat * beat_pixels)
        y = NOTE_Y_POSITIONS[note_name]
        
        svg += f'  <ellipse cx="{x}" cy="{y}" rx="7" ry="5" fill="black" transform="rotate(-15 {x} {y})" />\n'
        
        svg += f'  <line x1="{x + 7}" y1="{y}" x2="{x + 7}" y2="{y - 35}" stroke="black" stroke-width="1.5" />\n'
        
        if note_name == "C4":
            svg += f'  <line x1="{x - 12}" y1="{y}" x2="{x + 12}" y2="{y}" stroke="black" stroke-width="1" />\n'
            
    # Fin du document SVG
    svg += '</svg>'
    return svg