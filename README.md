# Context Detector

![CI/CD](https://github.com/Agostinho-neto/context-detector/actions/workflows/ci.yml/badge.svg)

Ferramenta que extrai o áudio de vídeos e transcreve automaticamente usando **faster-whisper**, tudo rodando local, sem enviar nada pra nuvem.

Construí esse projeto pra exercitar conceitos de SRE na prática: containerização, CI/CD, observabilidade, tratamento de erros, tudo num projeto funcional de ponta a ponta.

## O que faz

- Recebe vídeos (`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.flv`, `.wmv`)
- Extrai o áudio via FFmpeg
- Transcreve usando Whisper (local, sem API externa)
- Detecta o idioma automaticamente
- Gera saída em 3 formatos: `.txt`, `.srt` (legendas) e `.json`
- Suporta processamento em lote (pasta inteira)

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.13 |
| Transcrição | faster-whisper |
| Interface web | Streamlit |
| Extração de áudio | FFmpeg |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions (lint, test, build, publish) |
| Registry | GitHub Container Registry (GHCR) |
| Métricas | Prometheus + prometheus-client |
| Logging | logging (console + arquivo) |
| Lint/Format | Ruff |
| Testes | pytest |

## Como rodar

### Local

```bash
git clone https://github.com/Agostinho-neto/context-detector.git
cd context-detector

python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

Interface web:
```bash
streamlit run app.py
```

CLI:
```bash
# Processar todos os vídeos da pasta input/
python main.py

# Vídeo específico com modelo maior
python main.py -i "video.mp4" -m medium
```

### Docker

```bash
docker compose up --build
```

Sobe a aplicação em `http://localhost:8501` e o Prometheus em `http://localhost:9091`.

## CLI — Opções

| Argumento | Descrição | Padrão |
|---|---|---|
| `-i`, `--input` | Caminho do vídeo ou pasta | `input/` |
| `-o`, `--output` | Pasta de saída | `output/` |
| `-m`, `--model` | Modelo Whisper | `base` |

### Modelos disponíveis

| Modelo | VRAM | Velocidade | Qualidade |
|---|---|---|---|
| `tiny` | ~1 GB | Muito rápido | Básica |
| `base` | ~1 GB | Rápido | Boa |
| `small` | ~2 GB | Médio | Muito boa |
| `medium` | ~5 GB | Lento | Ótima |
| `large-v3` | ~10 GB | Muito lento | Máxima |

## Observabilidade

### Logging

Logs estruturados com dois destinos:
- **Console** -> nível INFO
- **Arquivo** -> nível DEBUG em `logs/app.log`

Formato: `2026-05-11 14:30:00 [INFO] transcriber — Modelo carregado em 2.35s`

### Métricas (Prometheus)

Endpoint exposto em `:9090/metrics`. Métricas coletadas:

| Métrica | Tipo | O que mede |
|---|---|---|
| `videos_processed_total` | Counter | Total de vídeos (por status: success/error) |
| `extraction_duration_seconds` | Histogram | Tempo de extração do áudio |
| `transcription_duration_seconds` | Histogram | Tempo de transcrição (por modelo) |
| `model_load_duration_seconds` | Histogram | Tempo de carregamento do Whisper |

### Health check

O container tem health check configurado via `/_stcore/health` do Streamlit, com retry a cada 30s.

## CI/CD

Pipeline no GitHub Actions com 4 jobs:

1. **lint** -> Ruff (check + format)
2. **test** -> pytest
3. **docker** -> Build da imagem
4. **publish** -> Push pro GHCR (só na main, depois dos 3 anteriores passarem)

## Estrutura

```
context-detector/
├── app.py                  # Interface web (Streamlit)
├── main.py                 # CLI
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── requirements.txt
├── pyproject.toml
├── input/                  # Vídeos pra processar
├── output/                 # Transcrições geradas
├── logs/                   # Logs da aplicação
├── src/
│   ├── extractor.py        # Extração de áudio (FFmpeg)
│   ├── transcriber.py      # Transcrição (faster-whisper)
│   ├── processor.py        # Salva .txt, .srt, .json
│   ├── logger.py           # Configuração de logging
│   └── metrics.py          # Métricas Prometheus
├── tests/
│   └── test_processor.py
└── .github/
    └── workflows/
        └── ci.yml          # Pipeline CI/CD
```

## Saídas

Pra cada vídeo processado:

| Arquivo | Conteúdo |
|---|---|
| `video.txt` | Texto corrido |
| `video.srt` | Legendas com timestamps |
| `video.json` | Dados completos (segmentos, idioma, probabilidade) |
