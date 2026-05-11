import time
from dataclasses import dataclass, field
from pathlib import Path

from faster_whisper import WhisperModel

from src.logger import get_logger

logger = get_logger("transcriber")


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
    if not audio_path.exists():
        logger.error("Arquivo de áudio não encontrado: %s", audio_path)
        raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")

    try:
        logger.info("Carregando modelo Whisper (%s)...", model_size)
        t0 = time.time()
        model = WhisperModel(model_size, device="auto", compute_type="auto")
        logger.info("Modelo carregado em %.2fs", time.time() - t0)
    except Exception as e:
        logger.error("Falha ao carregar modelo Whisper '%s': %s", model_size, e)
        raise RuntimeError(
            f"Falha ao carregar modelo Whisper '{model_size}': {e}"
        ) from e

    try:
        logger.info("Transcrevendo: %s", audio_path.name)
        t1 = time.time()
        segments_gen, info = model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True,
        )

        segments = []
        for seg in segments_gen:
            segments.append(Segment(start=seg.start, end=seg.end, text=seg.text))
    except Exception as e:
        logger.error("Falha ao transcrever %s: %s", audio_path.name, e)
        raise RuntimeError(f"Falha ao transcrever {audio_path.name}: {e}") from e

    elapsed = time.time() - t1
    transcription = Transcription(
        language=info.language,
        language_probability=info.language_probability,
        segments=segments,
    )

    logger.info(
        "Transcrição concluída em %.2fs | idioma=%s | confiança=%.0f%% | segmentos=%d",
        elapsed,
        info.language,
        info.language_probability * 100,
        len(segments),
    )

    return transcription
