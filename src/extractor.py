import subprocess
import time
from pathlib import Path

from src.logger import get_logger
from src.metrics import EXTRACTION_DURATION

logger = get_logger("extractor")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FFMPEG_PATH = PROJECT_ROOT / "bin" / "ffmpeg.exe"


def _get_ffmpeg() -> str:
    """Retorna o caminho do FFmpeg local ou do sistema."""
    if FFMPEG_PATH.exists():
        return str(FFMPEG_PATH)
    return "ffmpeg"


def extract_audio(video_path: Path, output_dir: Path) -> Path:
    """Extrai o áudio de um arquivo de vídeo usando FFmpeg."""
    if not video_path.exists():
        logger.error("Arquivo de vídeo não encontrado: %s", video_path)
        raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {video_path}")

    audio_path = output_dir / f"{video_path.stem}.wav"

    logger.info("Extraindo áudio: %s -> %s", video_path.name, audio_path.name)

    ffmpeg = _get_ffmpeg()
    cmd = [
        ffmpeg,
        "-i",
        str(video_path),
        "-vn",  # sem vídeo
        "-acodec",
        "pcm_s16le",  # codec WAV 16-bit
        "-ar",
        "16000",  # 16kHz (ideal para Whisper)
        "-ac",
        "1",  # mono
        "-y",  # sobrescrever se existir
        str(audio_path),
    ]

    t0 = time.time()
    with EXTRACTION_DURATION.time():
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            logger.error(
                "FFmpeg não encontrado. Instale o FFmpeg ou coloque-o em bin/ffmpeg.exe"
            )
            raise FileNotFoundError(
                "FFmpeg não encontrado. Instale o FFmpeg ou coloque-o em bin/ffmpeg.exe"
            )
    elapsed = time.time() - t0

    if result.returncode != 0:
        logger.error(
            "FFmpeg falhou ao extrair áudio de %s: %s", video_path.name, result.stderr
        )
        raise RuntimeError(
            f"FFmpeg falhou ao extrair áudio de {video_path.name}:\n{result.stderr}"
        )

    size_kb = audio_path.stat().st_size / 1024
    logger.info("Extração concluída em %.2fs | tamanho=%dKB", elapsed, size_kb)
    return audio_path
