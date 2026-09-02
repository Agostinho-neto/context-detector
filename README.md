# Context Detector

![CI/CD](https://github.com/Agostinho-neto/context-detector/actions/workflows/ci.yml/badge.svg)

Ferramenta que extrai o áudio de vídeos e transcreve automaticamente usando **faster-whisper**. Pode rodar localmente ou em um container no Google Cloud Run.

Construí esse projeto pra exercitar conceitos de SRE na prática: containerização, CI/CD, infraestrutura como código, observabilidade e tratamento de erros, tudo num projeto funcional de ponta a ponta.

## O que faz

- Recebe vídeos (`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.flv`, `.wmv`)
- Extrai o áudio via FFmpeg
- Transcreve usando Whisper dentro do próprio container, sem API de transcrição
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

## Como executar

### Google Cloud Run

O caminho principal do projeto usa uma imagem Docker no Artifact Registry e infraestrutura gerenciada com Terraform:

```text
GitHub Actions
    -> cria a imagem Docker
    -> envia ao Artifact Registry
    -> aplica o Terraform
    -> disponibiliza a aplicação no Cloud Run
```

A infraestrutura em `infra/` configura:

- APIs necessárias do Google Cloud
- Repositório Docker no Artifact Registry
- Conta de serviço da aplicação
- Serviço público no Cloud Run
- Limites de CPU, memória, concorrência e número de instâncias

Quando alguém acessa a URL pública, o Cloud Run inicia uma instância com o container. O vídeo é processado pelo FFmpeg e pelo faster-whisper dentro dessa instância. Sem requisições, o serviço pode reduzir para zero instâncias.

A imagem padrão inclui o modelo Whisper `base`. O modelo é baixado durante o `docker build` e carregado de `/opt/whisper-model` durante a execução. Isso evita downloads do Hugging Face em cada nova instância e torna o cold start independente dos limites de requisição do Hub.

```text
Navegador
    -> Cloud Run
    -> container Streamlit
    -> FFmpeg extrai o áudio
    -> faster-whisper transcreve
    -> usuário recebe TXT, SRT ou JSON
```

Os arquivos gerados dentro do container são temporários. O usuário deve baixar o resultado antes que a instância seja encerrada.

#### Preparação do ambiente

Para implantar na própria conta são necessários:

- Projeto Google Cloud com faturamento habilitado
- Google Cloud SDK e Terraform para o bootstrap inicial
- Bucket GCS para o estado remoto
- Fork ou cópia do projeto em um repositório GitHub

O diretório `infra/bootstrap/` cria a integração segura entre GitHub Actions e Google Cloud usando Workload Identity Federation. Cada usuário informa o próprio projeto, repositório e bucket em `infra/bootstrap/terraform.tfvars`, a partir do arquivo de exemplo.

```bash
cd infra/bootstrap
terraform init -reconfigure \
  -backend-config="bucket=SEU_BUCKET" \
  -backend-config="prefix=context-detector/bootstrap"
terraform apply
```

Depois do bootstrap, os outputs são cadastrados nas variáveis do repositório junto com projeto, região e bucket:

```text
GCP_PROJECT_ID
GCP_REGION
GCP_TF_STATE_BUCKET
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_SERVICE_ACCOUNT
```

#### Deploy

O deploy não acontece automaticamente após um merge. Ele é iniciado manualmente em:

```text
GitHub -> Actions -> Cloud Run CD -> Run workflow -> deploy
```

O workflow autentica sem chave JSON, prepara o Artifact Registry, constrói uma imagem identificada pelo SHA do commit e com o modelo `base` incluído, envia a imagem e aplica o Terraform. Ao final, exibe a URL pública do Cloud Run.

O estado da aplicação usa o mesmo bucket com outro prefixo:

```bash
terraform init -reconfigure \
  -backend-config="bucket=SEU_BUCKET" \
  -backend-config="prefix=context-detector/terraform"
```

#### Destroy

Como o ambiente de demonstração é temporário, ele pode ser removido pelo mesmo workflow:

```text
GitHub -> Actions -> Cloud Run CD -> Run workflow -> destroy
```

O destroy remove a infraestrutura da aplicação gerenciada em `infra/`, mas mantém o bootstrap e o bucket do state. Assim, a autenticação continua pronta para um novo deploy.

Cada pessoa que implantar o projeto utiliza a própria conta Google Cloud e assume os eventuais custos dos recursos criados.

### Execução local com Docker

Para testar sem criar recursos na nuvem:

```bash
git clone https://github.com/Agostinho-neto/context-detector.git
cd context-detector
docker compose up --build
```

O Compose constrói a imagem a partir do `Dockerfile` e sobe:

- Aplicação em `http://localhost:8501`
- Prometheus em `http://localhost:9091`
- Métricas em `http://localhost:9090/metrics`

Por padrão, a imagem oferece somente o modelo `base`, já armazenado nela. Para construir uma imagem com outro modelo:

```bash
docker compose build --build-arg WHISPER_MODEL=small
docker compose up
```

Cada imagem contém um único modelo para evitar downloads durante a execução e limitar seu tamanho.

## CLI — Opções

| Argumento | Descrição | Padrão |
|---|---|---|
| `-i`, `--input` | Caminho do vídeo ou pasta | `input/` |
| `-o`, `--output` | Pasta de saída | `output/` |
| `-m`, `--model` | Modelo Whisper | `base` |

### Modelos disponíveis

O modelo padrão da imagem é `base`. Os demais podem ser usados em uma imagem construída com `--build-arg WHISPER_MODEL=<modelo>` ou na execução direta com Python, que mantém o download e o cache tradicionais do faster-whisper.

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

O CI é executado em Pull Requests e pushes na `main`:

1. **lint** -> Ruff e actionlint
2. **test** -> pytest
3. **docker** -> Build da imagem
4. **terraform** -> Validação de `infra/` e `infra/bootstrap/`
5. **publish** -> Push pro GHCR, somente na `main`

O CD é separado e manual. O workflow `Cloud Run CD` usa Workload Identity Federation para obter credenciais temporárias, publica uma imagem com a tag do commit no Artifact Registry e aplica o Terraform. O mesmo workflow oferece a ação `destroy` para remover o ambiente de demonstração.

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
│   ├── terraform.tfvars.example
│   └── bootstrap/
│       ├── main.tf         # Workload Identity e permissões do CD
│       ├── variables.tf
│       ├── outputs.tf
│       ├── versions.tf
│       └── terraform.tfvars.example
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
        ├── ci.yml          # Qualidade, testes, build e publicação no GHCR
        └── cd.yaml         # Deploy e destroy manuais no Cloud Run
```

## Saídas

Pra cada vídeo processado:

| Arquivo | Conteúdo |
|---|---|
| `video.txt` | Texto corrido |
| `video.srt` | Legendas com timestamps |
| `video.json` | Dados completos (segmentos, idioma, probabilidade) |
