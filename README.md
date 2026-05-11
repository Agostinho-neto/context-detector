# Context Detector

![CI/CD](https://github.com/Agostinho-neto/context-detector/actions/workflows/ci.yml/badge.svg)

Aplicação para extração de áudio de vídeos e transcrição automática usando **faster-whisper**.

## Funcionalidades

- Extração de áudio de múltiplos formatos de vídeo (`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.flv`, `.wmv`)
- Transcrição via modelo Whisper (execução local, sem envio de dados externos)
- Detecção automática de idioma
- Saída em 3 formatos: `.txt`, `.srt` (legendas) e `.json` (dados completos)
- Processamento em lote (pasta inteira de vídeos)

## Pré-requisitos

- **Python 3.10+**
- **FFmpeg** instalado e disponível no PATH → [Download](https://ffmpeg.org/download.html)

## Instalação

```bash
# Clone o repositório
git clone <repo-url> context-detector
cd context-detector

# Crie um ambiente virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

## Uso

```bash
# Processar todos os vídeos da pasta input/
python main.py

# Processar um vídeo específico
python main.py -i "caminho/do/video.mp4"

# Definir pasta de saída
python main.py -i input/ -o resultados/

# Usar modelo maior (mais preciso)
python main.py -m medium
```

### Opções

| Argumento | Descrição | Padrão |
|---|---|---|
| `-i`, `--input` | Caminho do vídeo ou pasta com vídeos | `input/` |
| `-o`, `--output` | Pasta de saída para transcrições | `output/` |
| `-m`, `--model` | Tamanho do modelo Whisper | `base` |

### Modelos disponíveis

| Modelo | VRAM | Velocidade | Qualidade |
|---|---|---|---|
| `tiny` | ~1 GB | Muito rápido | Básica |
| `base` | ~1 GB | Rápido | Boa |
| `small` | ~2 GB | Médio | Muito boa |
| `medium` | ~5 GB | Lento | Ótima |
| `large-v3` | ~10 GB | Muito lento | Máxima |

## Estrutura do Projeto

```
context-detector/
├── main.py              # Ponto de entrada (CLI)
├── requirements.txt     # Dependências
├── .gitignore
├── input/               # Colocar vídeos aqui
├── output/              # Transcrições geradas
└── src/
    ├── __init__.py
    ├── extractor.py     # Extração de áudio (FFmpeg)
    ├── transcriber.py   # Transcrição (faster-whisper)
    └── processor.py     # Salva em .txt, .srt e .json
```

## Saídas

Para cada vídeo processado, são gerados 3 arquivos na pasta de saída:

| Arquivo | Conteúdo |
|---|---|
| `video.txt` | Texto corrido da transcrição |
| `video.srt` | Legendas com timestamps (importável em players) |
| `video.json` | Dados completos (segmentos, idioma, probabilidade) |
