import json
from pathlib import Path

from src.transcriber import Transcription


def _format_timestamp(seconds: float) -> str:
    """Converte segundos para formato HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def save_transcription(
    transcription: Transcription, name: str, output_dir: Path
) -> None:
    """Salva a transcrição em múltiplos formatos (.txt, .srt, .json)."""

    # Texto simples
    txt_path = output_dir / f"{name}.txt"
    txt_path.write_text(transcription.full_text, encoding="utf-8")
    print(f"  Salvo: {txt_path.name}")

    # SRT (legendas com timestamps)
    srt_path = output_dir / f"{name}.srt"
    srt_lines = []
    for i, seg in enumerate(transcription.segments, 1):
        start = _format_srt_time(seg.start)
        end = _format_srt_time(seg.end)
        srt_lines.append(f"{i}")
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(seg.text.strip())
        srt_lines.append("")
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"  Salvo: {srt_path.name}")

    # JSON (dados completos)
    json_path = output_dir / f"{name}.json"
    data = {
        "language": transcription.language,
        "language_probability": transcription.language_probability,
        "full_text": transcription.full_text,
        "segments": [
            {
                "start": seg.start,
                "end": seg.end,
                "start_formatted": _format_timestamp(seg.start),
                "end_formatted": _format_timestamp(seg.end),
                "text": seg.text.strip(),
            }
            for seg in transcription.segments
        ],
    }
    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Salvo: {json_path.name}")


def _format_srt_time(seconds: float) -> str:
    """Converte segundos para formato SRT (HH:MM:SS,mmm)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
