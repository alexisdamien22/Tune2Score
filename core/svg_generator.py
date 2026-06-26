# core/svg_generator.py
import copy

# --- CONSTANTES DE BASE ---
NOTE_LETTERS = ["C", "D", "E", "F", "G", "A", "B"]
NATURAL_MIDI_VALUES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LETTER_TO_BASE_STEP = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}

SCALE_DEGREES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 11]
}

SHARP_ARMOR_Y_OFFSETS = {"F": 5, "C": 2, "G": 6, "D": 3, "A": 0, "E": 4, "B": 1}
BEMOL_ARMOR_Y_OFFSETS = {"B": 2, "E": 5, "A": 1, "D": 4, "G": 0, "C": 3, "F": -1}


def get_armor_from_cycle(tonic: str, mode: str) -> dict:
    """Calcule l'armure d'une tonalité via le cycle des quintes."""
    SHARPS_ORDER = ["F", "C", "G", "D", "A", "E", "B"]
    FLATS_ORDER = ["B", "E", "A", "D", "G", "C", "F"]
    
    MAJOR_CYCLE = {
        "C": 0,  "G": 1,  "D": 2,  "A": 3,  "E": 4,  "B": 5,  "F#": 6, "C#": 7,
        "F": -1, "Bb": -2, "Eb": -3, "Ab": -4, "Db": -5, "Gb": -6, "Cb": -7
    }
    
    MINOR_RELATIVES = {
        "A": "C", "E": "G", "B": "D", "F#": "A", "C#": "E", "G#": "B", "D#": "F#", "A#": "C#",
        "D": "F", "G": "Bb", "C": "Eb", "F": "Ab", "Bb": "Db", "Eb": "Gb", "Ab": "Cb"
    }
    
    target_tonic = MINOR_RELATIVES.get(tonic, tonic) if mode == "minor" else tonic
    cycle_value = MAJOR_CYCLE.get(target_tonic, 0)
    
    if cycle_value > 0:
        return {"sharps": SHARPS_ORDER[:cycle_value], "flats": []}
    elif cycle_value < 0:
        return {"sharps": [], "flats": FLATS_ORDER[:abs(cycle_value)]}
    return {"sharps": [], "flats": []}


def derive_scale_spellings(tonic: str, mode: str) -> dict:
    """Génère la structure de la gamme (MIDI mod 12 -> Lettre) sans décalage indésirable."""
    # Normalisation des toniques reçues depuis l'UI
    clean_tonic = tonic.replace("b", "♭").replace("#", "♯")
    tonic_letter = clean_tonic[0]
    
    start_midi = NATURAL_MIDI_VALUES[tonic_letter]
    if "♯" in clean_tonic: start_midi += 1
    if "♭" in clean_tonic: start_midi -= 1
    start_midi %= 12
    
    letter_idx = NOTE_LETTERS.index(tonic_letter)
    scale_map = {}
    degrees = SCALE_DEGREES.get(mode, SCALE_DEGREES["major"])
    
    for i in range(7):
        current_midi = (start_midi + degrees[i]) % 12
        current_letter = NOTE_LETTERS[(letter_idx + i) % 7]
        scale_map[current_midi] = current_letter
        
    return scale_map


def detect_and_correct_tuning_issue(sequence: list, tonic: str, mode: str) -> int:
    """Détecte si l'instrument souffre d'un décalage global d'accordage."""
    if not sequence:
        return 0

    correct_scale = derive_scale_spellings(tonic, mode)
    correct_pitches_mod12 = set(correct_scale.keys())

    score_as_is = 0
    score_shifted_down = 0
    score_shifted_up = 0

    for item in sequence:
        p = item.get("pitch_midi", 0) % 12
        if p in correct_pitches_mod12:
            score_as_is += 1
        if (p + 1) % 12 in correct_pitches_mod12:
            score_shifted_down += 1
        if (p - 1) % 12 in correct_pitches_mod12:
            score_shifted_up += 1

    # Le garde-fou : on ne corrige que s'il y a un avantage massif et évident
    if score_shifted_down > score_as_is and score_shifted_down > score_shifted_up:
        return 1
    elif score_shifted_up > score_as_is and score_shifted_up > score_shifted_down:
        return -1
    return 0


def get_clean_note_display(pitch_midi: int, armor: dict, tonic: str, mode: str) -> tuple[int, str]:
    """Donne la position verticale et l'altération sans inventer de fausses notes."""
    pitch_mod12 = pitch_midi % 12
    scale = derive_scale_spellings(tonic, mode)
    is_flat_tonality = len(armor.get("flats", [])) > 0
    
    if pitch_mod12 in scale:
        letter = scale[pitch_mod12]
        step = LETTER_TO_BASE_STEP[letter]
        natural_midi = NATURAL_MIDI_VALUES[letter]
        
        diff = (pitch_mod12 - natural_midi) % 12
        if diff > 6: diff -= 12
        
        if abs(diff) <= 2:
            accidental = ""
            if diff == 1:
                if letter not in armor.get("sharps", []): accidental = "♯"
            elif diff == 2:
                accidental = "𝄪"
            elif diff == -1:
                if letter not in armor.get("flats", []): accidental = "♭"
            elif diff == -2:
                accidental = "𝄫"
            elif diff == 0:
                if letter in armor.get("sharps", []) or letter in armor.get("flats", []):
                    accidental = "♮"
            return step, accidental

    # Plan de secours enharmonique strict
    if is_flat_tonality:
        fallback_letters = {0:"C", 1:"D", 2:"D", 3:"E", 4:"E", 5:"F", 6:"G", 7:"G", 8:"A", 9:"A", 10:"B", 11:"B"}
        letter = fallback_letters[pitch_mod12]
        step = LETTER_TO_BASE_STEP[letter]
        natural_midi = NATURAL_MIDI_VALUES[letter]
        diff = (pitch_mod12 - natural_midi) % 12
        if diff > 6: diff -= 12
        accidental = "♭" if diff == -1 else ("♮" if (letter in armor.get("flats", [])) and diff == 0 else "")
    else:
        fallback_letters = {0:"C", 1:"C", 2:"D", 3:"D", 4:"E", 5:"F", 6:"F", 7:"G", 8:"G", 9:"A", 10:"A", 11:"B"}
        letter = fallback_letters[pitch_mod12]
        step = LETTER_TO_BASE_STEP[letter]
        natural_midi = NATURAL_MIDI_VALUES[letter]
        diff = (pitch_mod12 - natural_midi) % 12
        if diff > 6: diff -= 12
        accidental = "♯" if diff == 1 else ("♮" if (letter in armor.get("sharps", [])) and diff == 0 else "")

    return step, accidental


def generate_svg_score(sequence: list, tonic: str = "C", mode: str = "major") -> str:
    """Génère le rendu SVG en protégeant l'intégrité de la séquence originale."""
    # SÉCURITÉ : On fait une copie profonde pour éviter les effets de bord d'une Tonalité à l'autre !
    local_sequence = copy.deepcopy(sequence)
    
    armor = get_armor_from_cycle(tonic, mode)
    if not local_sequence:
        return '<svg viewBox="0 0 1100 300" width="100%"><text x="50" y="100" font-family="sans-serif">Aucune note détectée.</text></svg>'

    tuning_correction = detect_and_correct_tuning_issue(local_sequence, tonic, mode)

    page_width = 1100
    row_height = 180    
    start_y = 80        
    line_spacing = 10   
    
    armor_count = max(len(armor.get("sharps", [])), len(armor.get("flats", [])))
    start_x_cursor = 150 + (armor_count * 15)

    current_row = 0
    x_cursor = start_x_cursor
    notes_with_positions = []

    for item in local_sequence:
        duration = item.get("duration_seconds", 0.4)
        if duration <= 0.3:
            note_type = "eighth"
            note_width = 45
        elif duration <= 0.6:
            note_type = "quarter"
            note_width = 65
        else:
            note_type = "half"
            note_width = 90
            
        if x_cursor + note_width > page_width - 50:
            current_row += 1
            x_cursor = start_x_cursor
            
        notes_with_positions.append({
            "item": item, "row": current_row, "x": x_cursor, "width": note_width, "type": note_type
        })
        x_cursor += note_width

    total_rows = current_row + 1
    page_height = start_y + (total_rows * row_height) + 50
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {page_width} {page_height}" width="100%" height="{page_height}" style="background-color: #fff;">']

    def draw_staff_row(current_staff_y):
        for l in range(5):
            y = current_staff_y + (l * line_spacing)
            svg.append(f'<line x1="30" y1="{y}" x2="{page_width-30}" y2="{y}" stroke="#222" stroke-width="1.2"/>')
        svg.append(f'<text x="45" y="{current_staff_y + 32}" font-family="serif" font-size="45" font-weight="bold" fill="#111">𝄞</text>')
        
        cx = 95
        for sharp_note in armor.get("sharps", []):
            offset = SHARP_ARMOR_Y_OFFSETS.get(sharp_note, 0)
            y_sharp = (current_staff_y + 20) - (offset * (line_spacing / 2))
            svg.append(f'<text x="{cx}" y="{y_sharp}" font-family="serif" font-size="24" font-weight="bold" fill="#111">♯</text>')
            cx += 14
        for flat_note in armor.get("flats", []):
            offset = BEMOL_ARMOR_Y_OFFSETS.get(flat_note, 0)
            y_flat = (current_staff_y + 20) - (offset * (line_spacing / 2))
            svg.append(f'<text x="{cx}" y="{y_flat}" font-family="serif" font-size="24" fill="#111">♭</text>')
            cx += 14

    for r in range(total_rows):
        staff_y = start_y + (r * row_height)
        draw_staff_row(staff_y)
        row_notes = [n for n in notes_with_positions if n["row"] == r]
        eighth_group = []

        for idx, n_pos in enumerate(row_notes):
            item = n_pos["item"]
            nx = n_pos["x"]
            ntype = n_pos["type"]
            
            # Application de la correction sur une variable locale étanche
            pitch = item["pitch_midi"] + tuning_correction
            
            step_in_octave, accidental = get_clean_note_display(pitch, armor, tonic, mode)
            octave = (pitch // 12) - 5
            total_step = step_in_octave + (octave * 7)
            ny = (staff_y + 40) - (total_step * (line_spacing / 2))

            if total_step <= -2:
                for l_sup in range(total_step, 0, 2):
                    if l_sup % 2 == 0:
                        y_sup = (staff_y + 40) - (l_sup * (line_spacing / 2))
                        svg.append(f'<line x1="{nx-6}" y1="{y_sup}" x2="{nx+20}" y2="{y_sup}" stroke="#333" stroke-width="1"/>')
            elif total_step >= 10:
                for l_sup in range(10, total_step + 1, 2):
                    if l_sup % 2 == 0:
                        y_sup = (staff_y + 40) - (l_sup * (line_spacing / 2))
                        svg.append(f'<line x1="{nx-6}" y1="{y_sup}" x2="{nx+20}" y2="{y_sup}" stroke="#333" stroke-width="1"/>')

            if accidental:
                svg.append(f'<text x="{nx-15}" y="{ny+6}" font-family="serif" font-size="20" font-weight="bold" fill="#111">{accidental}</text>')

            fill_color = "#111" if ntype in ["quarter", "eighth"] else "none"
            svg.append(f'<ellipse cx="{nx+7}" cy="{ny}" rx="6.5" ry="4.5" transform="rotate(-20 {nx+7} {ny})" fill="{fill_color}" stroke="#111" stroke-width="1.5"/>')

            go_down = total_step >= 4
            hx = nx + 0.5 if go_down else nx + 13.5
            hy_end = ny + 28 if go_down else ny - 28
            svg.append(f'<line x1="{hx}" y1="{ny}" x2="{hx}" y2="{hy_end}" stroke="#111" stroke-width="1.8"/>')

            if ntype == "eighth":
                eighth_group.append((hx, hy_end))
                if idx == len(row_notes) - 1 or row_notes[idx+1]["type"] != "eighth" or len(eighth_group) >= 4:
                    if len(eighth_group) > 1:
                        x1, y1 = eighth_group[0]
                        x2, y2 = eighth_group[-1]
                        svg.append(f'<polygon points="{x1},{y1} {x2},{y2} {x2},{y2+4} {x1},{y1+4}" fill="#111"/>')
                    else:
                        cx_flag, cy_flag = eighth_group[0]
                        dy = 12 if go_down else -12
                        svg.append(f'<path d="M {cx_flag} {cy_flag} Q {cx_flag+6} {cy_flag+dy/2} {cx_flag+2} {cy_flag+dy}" stroke="#111" stroke-width="1.8" fill="none"/>')
                    eighth_group = []
            else:
                eighth_group = []

    svg.append('</svg>')
    return "".join(svg)