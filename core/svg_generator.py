# core/svg_generator.py

MIDI_TO_STAFF_STEP = {
    57: -2, 59: -1, 60: 0, 61: 0, 62: 1, 63: 1, 64: 2, 65: 3, 66: 3, 67: 4,
    68: 4, 69: 5, 70: 5, 71: 6, 72: 7, 73: 7, 74: 8, 75: 8, 76: 9, 77: 10
}

SHARP_MIT_NOTES = [61, 63, 66, 68, 70, 73, 75]

def generate_svg_score(final_sequence) -> str:
    if not final_sequence:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200"><rect width="100%" height="100%" fill="#ffffff"/><text x="40" y="100">Aucune donnée musicale.</text></svg>'

    page_width = 1100
    staff_width = 1000  
    row_height = 180
    start_y = 80        
    line_spacing = 10   
    
    x_test = 110
    total_rows = 1
    beats_in_measure_test = 0.0
    max_beats_per_measure = 4.0
    
    for item in final_sequence:
        beats_value = item.get("beats_value", 1.0)
        if beats_in_measure_test + beats_value > max_beats_per_measure:
            beats_in_measure_test = 0.0
        if x_test > staff_width:
            total_rows += 1
            x_test = 110  
        beats_in_measure_test += beats_value
        x_test += 65

    page_height = start_y + (total_rows * row_height) - 40
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width}" height="{page_height}" viewBox="0 0 {page_width} {page_height}">']
    svg.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    
    def draw_staff_row(current_staff_y):
        for l in range(5):
            y = current_staff_y + (l * line_spacing)
            svg.append(f'<line x1="30" y1="{y}" x2="{page_width-30}" y2="{y}" stroke="#222222" stroke-width="1.2"/>')
        svg.append(f'<text x="40" y="{current_staff_y + 32}" font-family="serif" font-size="45" font-weight="bold" fill="#111">𝄞</text>')

    current_row_index = 0
    staff_y = start_y + (current_row_index * row_height)
    draw_staff_row(staff_y)  
    
    x_cursor = 110
    beats_in_measure = 0.0
    
    note_group = []

    def draw_group_beams_and_stems(group):
        """Calcule la ligne de ligature idéale et ajuste la taille exacte de chaque hampe"""
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

        x_first = group[0][1]
        y_note_first = group[0][2]
        x_last = group[-1][1]
        y_note_last = group[-1][2]

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
            x_cursor = 110

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
            
            if pitch in SHARP_MIT_NOTES:
                svg.append(f'<text x="{x_cursor - 14}" y="{y_note + 5}" font-family="serif" font-size="20" font-weight="bold" fill="#111">♯</text>')
            
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