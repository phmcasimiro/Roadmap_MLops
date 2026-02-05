# Plataforma de Análise de Dados de Criptomoedas (MLOps)

## Visão Geral

Este projeto foi desenvolvido visando aplicar **conhecimentos de Engenharia de Dados e MLOps** no contexto do mercado de criptomoedas. Esta solução buscou integrar o início de um Pipeline de Dados: iniciando pela ingestão de dados (Real-time & Batch), passando pelo processamento estruturado, armazenamento persistente, e chegando ao versionamento de dados.

Automatizado para rodar 24/7, ele fornece dados contínuos sobre o mercado cripto, servindo como fundação para futuros modelos de Machine Learning e dashboards de visualização.

## Arquitetura da Solução

A arquitetura segue o padrão **ETL (Extract, Transform, Load)** focado em robustez e auditabilidade.

```text
├── Ingestão (Extract)
│   ├── Client API CoinGecko (Resiliente a Rate Limits e Retries)
│   ├── Coleta Tempo Real (Top 250 assets)
│   └── Coleta Histórica (Backfill de 1+ ano)
│
├── Processamento (Transform)
│   ├── Limpeza e Tipagem (Pandas)
│   ├── Enriquecimento (Cálculo de OHLC, Volatilidade, SMA)
│   └── Normalização Temporal
│
├── Armazenamento (Load)
│   └── SQLite (Relacional, indexado por CoinID e Timestamp)
│
└── Governança & Resiliência
    ├── Versionamento de Dados (DVC + Snapshots Semanais)
    └── Monitoramento (Alertas de Falha via E-mail)
```

## Funcionalidades Principais

### 1. Ingestão Híbrida Inteligente (`main.py`)
- **Modo Real-Time**: Captura o estado atual do mercado (Top 250 moedas) via `crontab` (3x/dia).
- **Modo Histórico**: Capacidade de *backfill* de dados passados (configurável, ex: 365 dias) com controle inteligente de limites da API.

### 2. Resiliência e Monitoramento (`src/email_alert.py`)
- **Alerta de Falha**: O pipeline monitora sua própria execução. Caso a coleta retorne 0 registros, um alerta crítico é disparado por e-mail para o administrador.

### 3. Versionamento de Dados (`src/dvc_versioning.py`)
- **DVC (Data Version Control)**: Implementação profissional de versionamento em substituição a backups manuais.
    - O banco de dados `cripto.db` é rastreado como um artefato.
    - Scripts automatizados geram snapshots semanais.
    - Histórico armazenado em remote local (`dvc_store/`).

## Estrutura do Projeto

```text
/
├── main.py                 # Orquestrador do ETL (CLI Entrypoint)
├── pyproject.toml          # Configuração do Projeto e Dependências
├── requirements.txt        # Dependências (Legado/Compatibilidade)
├── data/                   # Dados: cripto.db, logs e dvc_store/
├── .dvc/                   # Configurações do DVC
└── src/
    ├── api_client.py       # Wrapper da API
    ├── data_processor.py   # Lógica MLOps
    ├── database.py         # Persistência
    ├── dvc_versioning.py   # Script de Snapshot (DVC)
    └── email_alert.py      # Alertas
```

## Guia de Instalação e Execução

### Pré-requisitos
- Python 3.10+
- Ambiente Virtual
- DVC

### 1. Configuração

```bash
git clone <URL_REPO>
cd Roadmap_MLops
python3 -m venv .venv
source .venv/bin/activate
# Instale as dependências (via pyproject.toml)
pip install -e .

# Ou via legacy requirement:
# pip install -r requirements.txt

# Inicialize o DVC (caso esteja clonando pela primeira vez sem os dados)
dvc pull
```

### 2. Pipeline e Alertas (Opcional)

Para receber alertas por e-mail:
```bash
export EMAIL_USER="seu_email@gmail.com"
export EMAIL_PASSWORD="sua_senha_de_app"
```

**Execução:**
```bash
# Histórico
python main.py --historical --days 365 --all

# Tempo Real
python main.py --all
```

**Versionamento:**
```bash
python src/dvc_versioning.py
```

## Próximos Passos (Roadmap)
- [ ] **Dockerização**: Containerizar a aplicação.
- [ ] **Data Quality**: Great Expectations.
- [ ] **Cloud**: S3 Remote e Postgres.
