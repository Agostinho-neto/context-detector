from dataclasses import dataclass, field
from pathlib import Path

from faster_whisper import WhisperModel


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class Transcription:
    language: str
    language_probability: float
    segments: list[Segment] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return " ".join(seg.text.strip() for seg in self.segments)


def transcribe_audio(audio_path: Path, model_size: str = "base") -> Transcription:
    """Transcreve um arquivo de áudio usando faster-whisper."""
    print(f"  Carregando modelo Whisper ({model_size})...")
    model = WhisperModel(model_size, device="auto", compute_type="auto")

    print(f"  Transcrevendo: {audio_path.name}")
    segments_gen, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        vad_filter=True,
    )

    segments = []
    for seg in segments_gen:
        segments.append(Segment(start=seg.start, end=seg.end, text=seg.text))

    transcription = Transcription(
        language=info.language,
        language_probability=info.language_probability,
        segments=segments,
    )

    print(f"  Idioma detectado: {info.language} ({info.language_probability:.0%})")
    print(f"  Segmentos transcritos: {len(segments)}")

    return transcription
