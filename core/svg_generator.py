# core/svg_generator.py

# Table de correspondance hauteur MIDI -> position sur les lignes (Clé de Sol)
MIDI_TO_STAFF_STEP = {
    57: -2, 59: -1, 60: 0, 61: 0, 62: 1, 63: 1, 64: 2, 65: 3, 66: 3, 67: 4,
    68: 4, 69: 5, 70: 5, 71: 6, 72: 7, 73: 7, 74: 8, 75: 8, 76: 9, 77: 10
}

SHARP_ARMOR_Y_OFFSETS = {"F": 0, "C": 3, "G": -1, "D": 2}
BEMOL_ARMOR_Y_OFFSETS = {"B": 2, "E": 5, "A": 1}

KEY_ARMORS = {
    ("C", "major"):  {"sharps": [], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": []},
    ("A", "minor"):  {"sharps": [], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": []},
    
    ("G", "major"):  {"sharps": ["F"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [6]},
    ("E", "minor"):  {"sharps": ["F"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [6]},
    
    ("D", "major"):  {"sharps": ["F", "C"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 6]},
    ("B", "minor"):  {"sharps": ["F", "C"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 6]},
    
    ("A", "major"):  {"sharps": ["F", "C", "G"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 6, 8]},
    ("F#", "minor"): {"sharps": ["F", "C", "G"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 6, 8]},
    
    ("E", "major"):  {"sharps": ["F", "C", "G", "D"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 3, 6, 8]},
    ("C#", "minor"): {"sharps": ["F", "C", "G", "D"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 3, 6, 8]},
    
    ("B", "major"):  {"sharps": ["F", "C", "G", "D", "A"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 3, 6, 8, 10]},
    ("G#", "minor"): {"sharps": ["F", "C", "G", "D", "A"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 3, 6, 8, 10]},
    
    ("F#", "major"): {"sharps": ["F", "C", "G", "D", "A", "E"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 3, 4, 6, 8, 10]},
    ("D#", "minor"): {"sharps": ["F", "C", "G", "D", "A", "E"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [1, 3, 4, 6, 8, 10]},
    
    ("C#", "major"): {"sharps": ["F", "C", "G", "D", "A", "E", "B"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [0, 1, 3, 4, 6, 8, 10]},
    ("A#", "minor"): {"sharps": ["F", "C", "G", "D", "A", "E", "B"], "flats": [], "flat_notes_mod12": [], "sharp_notes_mod12": [0, 1, 3, 4, 6, 8, 10]},

    ("F", "major"):  {"sharps": [], "flats": ["B"], "flat_notes_mod12": [10], "sharp_notes_mod12": []},
    ("D", "minor"):  {"sharps": [], "flats": ["B"], "flat_notes_mod12": [10], "sharp_notes_mod12": []},
    
    ("Bb", "major"): {"sharps": [], "flats": ["B", "E"], "flat_notes_mod12": [3, 10], "sharp_notes_mod12": []},
    ("G", "minor"):  {"sharps": [], "flats": ["B", "E"], "flat_notes_mod12": [3, 10], "sharp_notes_mod12": []},
    
    ("Eb", "major"): {"sharps": [], "flats": ["B", "E", "A"], "flat_notes_mod12": [3, 8, 10], "sharp_notes_mod12": []},
    ("C", "minor"):  {"sharps": [], "flats": ["B", "E", "A"], "flat_notes_mod12": [3, 8, 10], "sharp_notes_mod12": []},
    
    ("Ab", "major"): {"sharps": [], "flats": ["B", "E", "A", "D"], "flat_notes_mod12": [1, 3, 8, 10], "sharp_notes_mod12": []},
    ("F", "minor"):  {"sharps": [], "flats": ["B", "E", "A", "D"], "flat_notes_mod12": [1, 3, 8, 10], "sharp_notes_mod12": []},
    
    ("Db", "major"): {"sharps": [], "flats": ["B", "E", "A", "D", "G"], "flat_notes_mod12": [1, 3, 6, 8, 10], "sharp_notes_mod12": []},
    ("Bb", "minor"): {"sharps": [], "flats": ["B", "E", "A", "D", "G"], "flat_notes_mod12": [1, 3, 6, 8, 10], "sharp_notes_mod12": []},
    
    ("Gb", "major"): {"sharps": [], "flats": ["B", "E", "A", "D", "G", "C"], "flat_notes_mod12": [1, 3, 6, 8, 10, 0], "sharp_notes_mod12": []},
    ("Eb", "minor"): {"sharps": [], "flats": ["B", "E", "A", "D", "G", "C"], "flat_notes_mod12": [1, 3, 6, 8, 10, 0], "sharp_notes_mod12": []},
    
    ("Cb", "major"): {"sharps": [], "flats": ["B", "E", "A", "D", "G", "C", "F"], "flat_notes_mod12": [1, 3, 4, 6, 8, 10, 11], "sharp_notes_mod12": []},
    ("Ab", "minor"): {"sharps": [], "flats": ["B", "E", "A", "D", "G", "C", "F"], "flat_notes_mod12": [1, 3, 4, 6, 8, 10, 11], "sharp_notes_mod12": []},
}

def generate_svg_score(final_sequence, tonic: str = "C", mode: str = "major") -> str:
    """Génère un flux de données SVG structuré multi-portées incluant ligatures complexes et armures."""
    if not final_sequence:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100"><rect width="100%" height="100%" fill="#ffffff"/><text x="20" y="50">Aucune donnée</text></svg>'

    armor = KEY_ARMORS.get((tonic, mode), KEY_ARMORS[("C", "major")])
    
    page_width = 1100
    staff_width = 1000  
    row_height = 180    
    start_y = 80        
    line_spacing = 10   
    
    armor_count = max(len(armor.get("sharps", [])), len(armor.get("flats", [])))
    start_x_cursor = 110 + (armor_count * 12)

    x_test = start_x_cursor
    total_rows = 1
    beats_in_measure_test = 0.0
    max_beats_per_measure = 4.0
    
    for item in final_sequence:
        beats_value = item.get("beats_value", 1.0)
        if beats_in_measure_test + beats_value > max_beats_per_measure:
            beats_in_measure_test = 0.0
        if x_test > staff_width:
            total_rows += 1
            x_test = start_x_cursor  
        beats_in_measure_test += beats_value
        x_test += 65

    page_height = start_y + (total_rows * row_height) - 40
    
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width}" height="{page_height}" viewBox="0 0 {page_width} {page_height}">']
    svg.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    
    def draw_staff_row(current_staff_y):
        """Sous-routine traçant une portée complète et ses attributs de clé/armure."""
        for l in range(5):
            y = current_staff_y + (l * line_spacing)
            svg.append(f'<line x1="30" y1="{y}" x2="{page_width-30}" y2="{y}" stroke="#222222" stroke-width="1.2"/>')
        
        svg.append(f'<text x="40" y="{current_staff_y + 32}" font-family="serif" font-size="45" font-weight="bold" fill="#111">𝄞</text>')
        
        cx = 85
        for sharp_note in armor.get("sharps", []):
            offset = SHARP_ARMOR_Y_OFFSETS.get(sharp_note, 0)
            y_sharp = (current_staff_y + 20) - (offset * (line_spacing / 2))
            svg.append(f'<text x="{cx}" y="{y_sharp}" font-family="serif" font-size="18" font-weight="bold" fill="#111">♯</text>')
            cx += 11
            
        for flat_note in armor.get("flats", []):
            offset = BEMOL_ARMOR_Y_OFFSETS.get(flat_note, 0)
            y_flat = (current_staff_y + 20) - (offset * (line_spacing / 2))
            svg.append(f'<text x="{cx}" y="{y_flat}" font-family="serif" font-size="18" font-weight="bold" fill="#111">♭</text>')
            cx += 11

    current_row_index = 0
    staff_y = start_y + (current_row_index * row_height)
    draw_staff_row(staff_y)  
    
    x_cursor = start_x_cursor
    beats_in_measure = 0.0
    note_group = []

    def draw_group_beams_and_stems(group):
        """Calcule les lignes d'équations des ligatures et intercepte les hampes au millimètre."""
        if not group:
            return
        
        if len(group) == 1:
            item, x, y_note = group[0]
            if item["duration"] != "ronde":
                y_stem_top = y_note - 30
                svg.append(f'<line x1="{x + 5.5}" y1="{y_note}" x2="{x + 5.5}" y2="{y_stem_top}" stroke="#111111" stroke-width="1.5"/>')
                if item["duration"] == "croche":
                    svg.append(f'<path d="M {x + 5.5} {y_stem_top} Q {x + 13} {y_stem_top + 8} {x + 11} {y_stem_top + 16}" stroke="#111" stroke-width="1.5" fill="none"/>')
                elif item["duration"] == "double-croche":
                    svg.append(f'<path d="M {x + 5.5} {y_stem_top} Q {x + 13} {y_stem_top + 8} {x + 11} {y_stem_top + 16}" stroke="#111" stroke-width="1.5" fill="none"/>')
                    svg.append(f'<path d="M {x + 5.5} {y_stem_top + 5} Q {x + 13} {y_stem_top + 13} {x + 11} {y_stem_top + 21}" stroke="#111" stroke-width="1.5" fill="none"/>')
            return

        x_first, y_note_first = group[0][1], group[0][2]
        x_last, y_note_last = group[-1][1], group[-1][2]
        y_beam_first = y_note_first - 32
        y_beam_last = y_note_last - 32

        m = (y_beam_last - y_beam_first) / (x_last - x_first) if x_last != x_first else 0
        p = y_beam_first - m * x_first

        for item, x, y_note in group:
            target_y_stem_top = m * (x + 5.5) + p 
            svg.append(f'<line x1="{x + 5.5}" y1="{y_note}" x2="{x + 5.5}" y2="{target_y_stem_top}" stroke="#111111" stroke-width="1.5"/>')

        svg.append(f'<line x1="{x_first + 5.5}" y1="{y_beam_first}" x2="{x_last + 5.5}" y2="{y_beam_last}" stroke="#111111" stroke-width="3.8"/>')

        in_double = False
        sub_x_start = None
        for i, (item, x, y_note) in enumerate(group):
            is_double = (item["duration"] == "double-croche")
            if is_double and not in_double:
                in_double = True
                sub_x_start = x + 5.5
            elif not is_double and in_double:
                sub_x_end = group[i-1][1] + 5.5
                y_b2_start = m * sub_x_start + p + 6
                y_b2_end = m * sub_x_end + p + 6
                svg.append(f'<line x1="{sub_x_start}" y1="{y_b2_start}" x2="{sub_x_end}" y2="{y_b2_end}" stroke="#111111" stroke-width="3.8"/>')
                in_double = False

        if in_double:
            sub_x_end = group[-1][1] + 5.5
            y_b2_start = m * sub_x_start + p + 6
            y_b2_end = m * sub_x_end + p + 6
            svg.append(f'<line x1="{sub_x_start}" y1="{y_b2_start}" x2="{sub_x_end}" y2="{y_b2_end}" stroke="#111111" stroke-width="3.8"/>')

    ALL_SHARP_MIDI_MOD12 = [1, 3, 6, 8, 10]

    for item in final_sequence:
        beats_value = item.get("beats_value", 1.0)
        is_dotted = item.get("dotted", False)
        
        if beats_in_measure + beats_value > max_beats_per_measure:
            if note_group:
                draw_group_beams_and_stems(note_group)
                note_group = []
            svg.append(f'<line x1="{x_cursor - 15}" y1="{staff_y}" x2="{x_cursor - 15}" y2="{staff_y + 40}" stroke="#222222" stroke-width="1.5"/>')
            beats_in_measure = 0.0

        if x_cursor > staff_width:
            if note_group:
                draw_group_beams_and_stems(note_group)
                note_group = []
            svg.append(f'<line x1="{page_width-30}" y1="{staff_y}" x2="{page_width-30}" y2="{staff_y + 40}" stroke="#222222" stroke-width="1.5"/>')
            current_row_index += 1
            staff_y = start_y + (current_row_index * row_height)
            draw_staff_row(staff_y)
            x_cursor = start_x_cursor

        beats_in_measure += beats_value

        if item["type"] != "note" or item["duration"] not in ["croche", "double-croche"]:
            if note_group:
                draw_group_beams_and_stems(note_group)
                note_group = []

        if item["type"] == "rest":
            y_rest = staff_y + 15
            if item["duration"] in ["ronde", "blanche"]:
                svg.append(f'<rect x="{x_cursor}" y="{y_rest}" width="14" height="7" fill="#111"/>')
            elif item["duration"] == "noire":
                svg.append(f'<text x="{x_cursor}" y="{y_rest+16}" font-family="serif" font-size="26" fill="#111">𝄽</text>')
            else:
                svg.append(f'<text x="{x_cursor}" y="{y_rest+14}" font-family="serif" font-size="22" fill="#111">𝄾</text>')
            if is_dotted:
                svg.append(f'<circle cx="{x_cursor + 18}" cy="{staff_y + 20}" r="2" fill="#111"/>')
            x_cursor += 65

        elif item["type"] == "note":
            pitch = item["pitch_midi"]
            step = MIDI_TO_STAFF_STEP.get(pitch, 4)
            y_note = (staff_y + 40) - (step * (line_spacing / 2))
            
            pitch_mod12 = pitch % 12
            if pitch_mod12 in ALL_SHARP_MIDI_MOD12:
                if pitch_mod12 not in armor.get("sharp_notes_mod12", []):
                    svg.append(f'<text x="{x_cursor - 14}" y="{y_note + 5}" font-family="serif" font-size="20" font-weight="bold" fill="#111">♯</text>')
            else:
                if 6 in armor.get("sharp_notes_mod12", []) and pitch_mod12 == 5:
                    svg.append(f'<text x="{x_cursor - 14}" y="{y_note + 5}" font-family="serif" font-size="20" fill="#111">♮</text>')

            is_filled = item["duration"] not in ["ronde", "blanche"]
            if is_filled:
                svg.append(f'<ellipse cx="{x_cursor}" cy="{y_note}" rx="5.5" ry="4" transform="rotate(-20 {x_cursor} {y_note})" fill="#111111"/>')
            else:
                svg.append(f'<ellipse cx="{x_cursor}" cy="{y_note}" rx="5.5" ry="4" transform="rotate(-20 {x_cursor} {y_note})" stroke="#111111" stroke-width="1.8" fill="none"/>')
                
            if is_dotted:
                svg.append(f'<circle cx="{x_cursor + 9}" cy="{y_note - 2}" r="1.8" fill="#111111"/>')

            if item["duration"] in ["croche", "double-croche"]:
                note_group.append((item, x_cursor, y_note))
            elif item["duration"] != "ronde":
                svg.append(f'<line x1="{x_cursor + 5.5}" y1="{y_note}" x2="{x_cursor + 5.5}" y2="{y_note - 30}" stroke="#111111" stroke-width="1.5"/>')
            
            x_cursor += 65
            
    if note_group:
        draw_group_beams_and_stems(note_group)

    svg.append(f'<line x1="{x_cursor - 15}" y1="{staff_y}" x2="{x_cursor - 15}" y2="{staff_y + 40}" stroke="#222222" stroke-width="3"/>')
    svg.append('</svg>')
    
    return "\n".join(svg)