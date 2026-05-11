import argparse
import sys
from pathlib import Path

from src.extractor import extract_audio
from src.transcriber import transcribe_audio
from src.processor import save_transcription
from src.metrics import VIDEOS_PROCESSED


VERSION = "1.0.0"

BANNER = r"""
   ___            _            _     ___       _            _
  / __\___  _ __ | |_ _____  _| |_  /   \  ___| |_ ___  ___| |_ ___  _ __
 / /  / _ \| '_ \| __/ _ \ \/ / __| / /\ \/ _ \ __/ _ \/ __| __/ _ \| '__|
/ /__| (_) | | | | ||  __/>  <| |_ / /_// |  __/ ||  __/ (__| || (_) | |
\____/\___/|_| |_|\__\___/_/\_\\__/___,'   \___|\__\___|\___|\__\___/|_|
"""

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv"}


def show_banner():
    print(BANNER)
    print(f"  v{VERSION} — Extração de áudio e transcrição de vídeos")
    print(f"{'─' * 60}")


def process_video(video_path: Path, output_dir: Path, model_size: str = "base") -> bool:
    print(f"\n{'=' * 60}")
    print(f"Processando: {video_path.name}")
    print(f"{'=' * 60}")

    try:
        # 1. Extrair áudio
        audio_path = extract_audio(video_path, output_dir)

        # 2. Transcrever áudio
        transcription = transcribe_audio(audio_path, model_size=model_size)

        # 3. Salvar transcrição
        save_transcription(transcription, video_path.stem, output_dir)

        # Remover áudio temporário
        audio_path.unlink(missing_ok=True)

        print(f"Concluído: {video_path.name}")
        VIDEOS_PROCESSED.labels(status="success").inc()
        return True
    except FileNotFoundError as e:
        print(f"Erro — arquivo não encontrado: {e}")
    except RuntimeError as e:
        print(f"Erro ao processar {video_path.name}: {e}")
    except OSError as e:
        print(f"Erro de I/O ao processar {video_path.name}: {e}")
    return False


def get_video_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() in VIDEO_EXTENSIONS:
            return [input_path]
        print(f"Arquivo não é um vídeo suportado: {input_path}")
        return []

    videos = [
        f
        for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ]
    return sorted(videos)


def main():
    parser = argparse.ArgumentParser(
        prog="Context Detector",
        description="Extrai áudio de vídeos e transcreve para texto.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path("input"),
        help="Caminho do vídeo ou pasta com vídeos (padrão: input/)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output"),
        help="Pasta de saída para transcrições (padrão: output/)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Tamanho do modelo Whisper (padrão: base)",
    )

    args = parser.parse_args()

    show_banner()

    if not args.input.exists():
        print(f"Erro: caminho de entrada não encontrado: {args.input}")
        sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True)

    videos = get_video_files(args.input)
    if not videos:
        print("Nenhum vídeo encontrado para processar.")
        sys.exit(0)

    print(f"Encontrados {len(videos)} vídeo(s) para processar.")

    success = 0
    for video in videos:
        if process_video(video, args.output, model_size=args.model):
            success += 1

    print(f"\n{success}/{len(videos)} vídeo(s) transcritos com sucesso.")
    print(f"Transcrições salvas em: {args.output.resolve()}")

    if success < len(videos):
        sys.exit(1)


if __name__ == "__main__":
    main()
