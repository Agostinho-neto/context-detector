# Context Detector

![CI/CD](https://github.com/Agostinho-neto/context-detector/actions/workflows/ci.yml/badge.svg)

Ferramenta que extrai o áudio de vídeos e transcreve automaticamente usando **faster-whisper**. Pode rodar localmente ou em um container no Google Cloud Run.

Construí esse projeto pra exercitar conceitos de SRE na prática: containerização, CI/CD, infraestrutura como código, observabilidade e tratamento de erros, tudo num projeto funcional de ponta a ponta.

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
| Infraestrutura como código | Terraform |
| Cloud | Google Cloud Run |
| Registry | Artifact Registry + GitHub Container Registry (GHCR) |
| Estado do Terraform | Google Cloud Storage |
| Métricas | Prometheus + prometheus-client |
| Logging | logging (console + arquivo) |
| Lint/Format | Ruff |
| Testes | pytest |

## Como rodar

O projeto pode ser usado de duas maneiras:

- **Localmente:** a aplicação e o Prometheus rodam em containers com Docker Compose.
- **Na nuvem:** um ambiente temporário de demonstração roda no Cloud Run enquanto os recursos estiverem provisionados.

O processo de recriar ou atualizar os recursos na nuvem é separado da execução local.

### Execução local com Docker

```bash
git clone https://github.com/Agostinho-neto/context-detector.git
cd context-detector
docker compose up --build
```

Sobe a aplicação em `http://localhost:8501` e o Prometheus em `http://localhost:9091`.

### Criação e atualização do ambiente na nuvem

A infraestrutura em `infra/` cria e configura:

- APIs necessárias do Google Cloud
- Repositório Docker no Artifact Registry
- Conta de serviço da aplicação
- Serviço público no Cloud Run
- Limites de CPU, memória, concorrência e número de instâncias

A imagem é construída com Docker, enviada ao Artifact Registry e usada pelo Cloud Run para iniciar as instâncias da aplicação sob demanda.

O estado do Terraform fica armazenado remotamente no bucket `context-detector-dev-tfstate`, com o prefixo `context-detector/terraform`. O backend remoto permite que a infraestrutura seja gerenciada fora de uma única máquina e mantém o bloqueio do estado durante alterações.

Para gerenciar esse ambiente são necessários Docker, Google Cloud SDK e Terraform, além de autenticação e acesso ao projeto no Google Cloud.

O fluxo atual de implantação é manual e dividido em duas responsabilidades:

```text
Docker: cria e envia a imagem da aplicação
Terraform: cria ou atualiza os recursos que executam essa imagem
```

Depois que a imagem esperada pelo `main.tf` estiver disponível no Artifact Registry, a infraestrutura pode ser validada e aplicada:

```bash
cd infra
terraform init
terraform plan -out=deploy.tfplan
terraform apply deploy.tfplan
terraform output -raw cloud_run_url
```

A URL retornada fica disponível somente enquanto o ambiente estiver provisionado. Como este é um projeto de portfólio, o ambiente pode ser criado para demonstrações e destruído depois do uso para evitar a permanência de recursos com potencial de cobrança:

```bash
terraform destroy
```

O bucket que armazena o estado remoto foi criado separadamente e não faz parte dos recursos destruídos por esse comando. Ele permanece disponível para guardar o estado das próximas execuções.

O arquivo `terraform.tfvars` contém os valores do ambiente e não é versionado. O arquivo `terraform.tfvars.example` serve como referência.

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

No ambiente local, o endpoint é exposto em `:9090/metrics` e o Prometheus fica disponível em `http://localhost:9091`. Métricas coletadas:

| Métrica | Tipo | O que mede |
|---|---|---|
| `videos_processed_total` | Counter | Total de vídeos (por status: success/error) |
| `extraction_duration_seconds` | Histogram | Tempo de extração do áudio |
| `transcription_duration_seconds` | Histogram | Tempo de transcrição (por modelo) |
| `model_load_duration_seconds` | Histogram | Tempo de carregamento do Whisper |

O `docker-compose.yml` não é usado pelo Cloud Run, portanto o container do Prometheus roda somente no ambiente local. Na nuvem, requisições, latência, instâncias, CPU e memória podem ser acompanhadas pelas métricas nativas do Cloud Run no Google Cloud Console.

### Health check

O container tem health check configurado via `/_stcore/health` do Streamlit, com retry a cada 30s.

## CI/CD

Pipeline no GitHub Actions com 5 jobs:

1. **lint** -> Ruff (check + format)
2. **test** -> pytest
3. **docker** -> Build da imagem
4. **terraform** -> Formatação e validação da infraestrutura
5. **publish** -> Push pro GHCR (só na main, depois dos 4 anteriores passarem)

O pipeline atual publica a imagem no GHCR. A automação do envio ao Artifact Registry e da atualização do Cloud Run será adicionada na etapa de CD.

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
├── infra/
│   ├── main.tf             # Recursos no Google Cloud
│   ├── variables.tf        # Variáveis da infraestrutura
│   ├── outputs.tf          # URL e identificadores dos recursos
│   ├── versions.tf         # Providers e backend remoto no GCS
│   └── terraform.tfvars.example
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
