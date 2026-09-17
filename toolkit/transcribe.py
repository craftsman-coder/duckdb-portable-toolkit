"""Speech-to-text helper using openai-whisper (offline)."""

from __future__ import annotations

from pathlib import Path

import whisper

_model_cache: dict = {}


def _get_model(name: str = "small"):
    """Load and cache a Whisper model."""
    if name not in _model_cache:
        print(f"Loading Whisper '{name}' model (first call may take a moment)...")
        _model_cache[name] = whisper.load_model(name)
    return _model_cache[name]


def transcribe(audio_path: str | Path,
               model: str = "small",
               language: str | None = "fa") -> dict:
    """
    Transcribe an audio file to text.

    Parameters
    ----------
    audio_path : str or Path
        Path to a .wav, .mp3, .flac, .ogg, or .m4a file.
    model : str
        Whisper model: tiny, base, small, medium, large.
        'small' is recommended for Persian.
    language : str or None
        Language code (e.g. 'fa' for Persian, 'en' for English).
        Set to None for auto-detection.

    Returns
    -------
    dict with keys 'text', 'language', 'segments'.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    m = _get_model(model)
    result = m.transcribe(str(audio_path), language=language)
    return result


def transcribe_to_text(audio_path: str | Path,
                       model: str = "small",
                       language: str | None = "fa") -> str:
    """Return only the transcribed text."""
    return transcribe(audio_path, model=model, language=language)["text"].strip()


def transcribe_segments(audio_path: str | Path,
                        model: str = "small",
                        language: str | None = "fa") -> list[dict]:
    """Return segments with timestamps (start, end, text)."""
    result = transcribe(audio_path, model=model, language=language)
    return [
        {
            "start": s["start"],
            "end": s["end"],
            "text": s["text"].strip(),
        }
        for s in result["segments"]
    ]


def transcribe_to_srt(audio_path: str | Path,
                      output_srt: str | Path,
                      model: str = "small",
                      language: str | None = "fa") -> Path:
    """Transcribe and save as an SRT subtitle file."""
    segments = transcribe_segments(audio_path, model=model, language=language)
    output_srt = Path(output_srt)

    def fmt(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{fmt(seg['start'])} --> {fmt(seg['end'])}")
        lines.append(seg["text"])
        lines.append("")

    output_srt.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {len(segments)} segments to {output_srt}")
    return output_srt
