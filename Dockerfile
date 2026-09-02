FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG WHISPER_MODEL=base

ENV WHISPER_MODEL_NAME=${WHISPER_MODEL}
ENV WHISPER_MODEL_PATH=/opt/whisper-model

RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Systran/faster-whisper-${WHISPER_MODEL}', local_dir='${WHISPER_MODEL_PATH}')"

ENV HF_HUB_OFFLINE=1

COPY . .

RUN mkdir -p input output

EXPOSE 8501 9090

CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.headless=true"]