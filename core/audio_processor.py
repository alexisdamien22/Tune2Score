# core/audio_processor.py
import librosa
import numpy as np


def _weighted_median(values: np.ndarray, weights: np.ndarray) -> int:
    sorted_idx = np.argsort(values)
    values = values[sorted_idx]
    weights = weights[sorted_idx]
    cumulative = np.cumsum(weights)
    half = cumulative[-1] / 2.0
    median_idx = np.searchsorted(cumulative, half)
    return int(values[min(median_idx, len(values) - 1)])


def _select_pitch_from_segment(f0_segment: np.ndarray, voiced_prob_segment: np.ndarray | None = None) -> int | None:
    """Retourne la note MIDI la plus probable d'un segment de pitch."""
    if f0_segment.size == 0:
        return None

    valid = np.isfinite(f0_segment)
    if voiced_prob_segment is not None:
        strong = valid & (voiced_prob_segment >= 0.75)
        if np.any(strong):
            valid = strong

    if not np.any(valid):
        return None

    f0_values = f0_segment[valid]
    midi_floats = librosa.hz_to_midi(f0_values)

    if voiced_prob_segment is not None:
        weights = voiced_prob_segment[valid].astype(float)
    else:
        weights = np.ones_like(midi_floats, dtype=float)

    midi_values = np.round(midi_floats).astype(int)
    valid_mask = (midi_values >= 21) & (midi_values <= 108)
    if not np.any(valid_mask):
        return None

    midi_values = midi_values[valid_mask]
    weights = weights[valid_mask]

    counts = np.bincount(midi_values - 21, weights=weights)
    best_midi = int(np.argmax(counts) + 21)
    total_weight = float(np.sum(counts))
    best_weight = float(counts[best_midi - 21])

    if best_weight >= total_weight * 0.5:
        return best_midi

    median_midi = _weighted_median(midi_values, weights)
    if 21 <= median_midi <= 108:
        return median_midi

    return best_midi


def analyze_audio_file(file_path: str):
    """
    Analyse un fichier audio monophonique en détectant les notes et leurs durées.
    Retourne une liste de dicts : [{"start_time_seconds", "end_time_seconds", "pitch_midi"}]
    """
    y, sr = librosa.load(file_path, sr=None, mono=True)
    if y.size == 0:
        return []

    y = librosa.util.normalize(y)
    y_harmonic, _ = librosa.effects.hpss(y)

    onset_frames = librosa.onset.onset_detect(
        y=y_harmonic,
        sr=sr,
        backtrack=True,
        units="frames"
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    duration = float(librosa.get_duration(y=y, sr=sr))
    if duration <= 0:
        return []

    if len(onset_times) == 0:
        onset_times = np.array([0.0], dtype=float)

    boundaries = list(onset_times) + [duration]

    hop_length = 256
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y_harmonic,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
        frame_length=2048,
        hop_length=hop_length
    )

    raw_sequence = []
    for i in range(len(boundaries) - 1):
        start = float(boundaries[i])
        end = float(boundaries[i + 1])
        if end - start < 0.03:
            continue

        start_frame = librosa.time_to_frames(start, sr=sr, hop_length=hop_length)
        end_frame = min(len(f0), librosa.time_to_frames(end, sr=sr, hop_length=hop_length))
        if end_frame <= start_frame:
            continue

        midi_note = _select_pitch_from_segment(
            f0[start_frame:end_frame],
            voiced_prob[start_frame:end_frame]
        )
        if midi_note is None:
            continue

        raw_sequence.append({
            "start_time_seconds": start,
            "end_time_seconds": end,
            "pitch_midi": int(midi_note)
        })

    if not raw_sequence:
        return []

    merged_sequence = [raw_sequence[0]]
    for note in raw_sequence[1:]:
        previous = merged_sequence[-1]
        gap = note["start_time_seconds"] - previous["end_time_seconds"]
        if note["pitch_midi"] == previous["pitch_midi"] and gap < 0.05:
            previous["end_time_seconds"] = note["end_time_seconds"]
        else:
            merged_sequence.append(note)

    return merged_sequence