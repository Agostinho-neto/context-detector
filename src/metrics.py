from prometheus_client import Counter, Histogram, Info

# Contadores
VIDEOS_PROCESSED = Counter(
    "videos_processed_total",
    "Total de vídeos processados",
    ["status"],  # labels: success, error
)

# Histogramas (latência)
EXTRACTION_DURATION = Histogram(
    "extraction_duration_seconds",
    "Tempo de extração de áudio via FFmpeg",
)

TRANSCRIPTION_DURATION = Histogram(
    "transcription_duration_seconds",
    "Tempo de transcrição via Whisper",
    ["model_size"],
)

MODEL_LOAD_DURATION = Histogram(
    "model_load_duration_seconds",
    "Tempo de carregamento do modelo Whisper",
    ["model_size"],
)

# Info
APP_INFO = Info("context_detector", "Informações da aplicação")
APP_INFO.info({"version": "1.0.0"})
