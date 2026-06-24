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
    Génère une partition SVG avec retours à la ligne automatiques 
    toutes les X mesures (4 mesures par défaut).
    """
    if not quantized_sequence:
        # Retourne un SVG vide minimal si aucune note
        return '<svg width="100%" height="100" xmlns="http://www.w3.org/2000/svg"></svg>'

    # --- CONFIGURATION MISE EN PAGE ---
    beats_per_measure = 4   # On suppose du 4/4 pour l'instant
    measures_per_line = 4   # Nombre de mesures avant de revenir à la ligne
    beats_per_line = beats_per_measure * measures_per_line # 16 temps par ligne
    
    margin_left = 80
    margin_right = 50
    beat_pixels = 55        # Espace horizontal pour 1 temps (beat)
    line_height = 160       # Espace vertical entre deux portées
    
    # Calcul de la largeur totale d'une ligne
    line_width = margin_left + (beats_per_line * beat_pixels) + margin_right
    
    # Déterminer le nombre de lignes requises
    last_item = quantized_sequence[-1]
    total_beats = last_item["start_beat"] + last_item["duration_beat"]
    total_lines = int(total_beats // beats_per_line) + 1
    
    # Hauteur dynamique du SVG global
    svg_height = (total_lines * line_height) + 60
    
    # Début du document SVG
    svg = f'<svg viewBox="0 0 {line_width} {svg_height}" width="100%" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'  <rect width="100%" height="100%" fill="white" />\n'
    
    # --- TRACÉ DES PORTÉES (LIGNES vides) ---
    for line_idx in range(total_lines):
        y_offset = line_idx * line_height + 40
        
        # Les 5 lignes de la portée de musique
        for staff_y in [40, 60, 80, 100, 120]:
            y_pos = y_offset + staff_y
            svg += f'  <line x1="{margin_left}" y1="{y_pos}" x2="{line_width - margin_right}" y2="{y_pos}" stroke="black" stroke-width="1" />\n'
        
        # Barre verticale de début de portée
        svg += f'  <line x1="{margin_left}" y1="{y_offset + 40}" x2="{margin_left}" y2="{y_offset + 120}" stroke="black" stroke-width="2" />\n'
        # Barre verticale de fin de portée
        svg += f'  <line x1="{line_width - margin_right}" y1="{y_offset + 40}" x2="{line_width - margin_right}" y2="{y_offset + 120}" stroke="black" stroke-width="2" />\n'

        # Tracé des barres de mesures intermédiaires
        for m in range(1, measures_per_line):
            m_x = margin_left + (m * beats_per_measure * beat_pixels)
            svg += f'  <line x1="{m_x}" y1="{y_offset + 40}" x2="{m_x}" y2="{y_offset + 120}" stroke="#ccc" stroke-width="1" />\n'

    # --- POSITIONNEMENT DES NOTES ---
    for item in quantized_sequence:
        note_name = item["note"]
        start_beat = item["start_beat"]
        
        if note_name == "Silence" or note_name not in NOTE_Y_POSITIONS:
            continue
            
        # Trouver sur quelle ligne se situe la note et son beat local sur cette ligne
        line_number = int(start_beat // beats_per_line)
        local_beat = start_beat % beats_per_line
        
        # Coordonnées calculées par rapport à sa ligne
        y_offset = line_number * line_height + 40
        x = margin_left + (local_beat * beat_pixels)
        y = y_offset + NOTE_Y_POSITIONS[note_name]
        
        # Dessin de la note (ovale incliné)
        svg += f'  <ellipse cx="{x}" cy="{y}" rx="7" ry="5" fill="black" transform="rotate(-15 {x} {y})" />\n'
        
        # Dessin de la hampe de la note (la barre verticale)
        svg += f'  <line x1="{x + 7}" y1="{y}" x2="{x + 7}" y2="{y - 35}" stroke="black" stroke-width="1.5" />\n'
        
        # Si c'est un Do central (C4), on dessine la petite ligne supplémentaire sous la portée
        if note_name == "C4":
            svg += f'  <line x1="{x - 12}" y1="{y}" x2="{x + 12}" y2="{y}" stroke="black" stroke-width="1" />\n'
            
    svg += '</svg>'
    return svg