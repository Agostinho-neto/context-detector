import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FFMPEG_PATH = PROJECT_ROOT / "bin" / "ffmpeg.exe"


def _get_ffmpeg() -> str:
    """Retorna o caminho do FFmpeg local ou do sistema."""
    if FFMPEG_PATH.exists():
        return str(FFMPEG_PATH)
    return "ffmpeg"


def extract_audio(video_path: Path, output_dir: Path) -> Path:
    """Extrai o áudio de um arquivo de vídeo usando FFmpeg."""
    audio_path = output_dir / f"{video_path.stem}.wav"

    print(f"  Extraindo áudio: {video_path.name} -> {audio_path.name}")

    cmd = [
        _get_ffmpeg(),
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

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg falhou ao extrair áudio de {video_path.name}:\n{result.stderr}"
        )

    print(f"  Áudio extraído com sucesso ({audio_path.stat().st_size / 1024:.0f} KB)")
    return audio_path
