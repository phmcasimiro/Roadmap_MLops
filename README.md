# Plataforma de Análise de Dados de Criptomoedas (MLOps)

## Visão Geral

Este projeto é uma **plataforma completa de Engenharia de Dados e MLOps** para o mercado de criptomoedas. Diferente de scripts isolados, esta solução integra todo o ciclo de vida do dado: desde a ingestão (Real-time & Batch), passando pelo processamento estruturado, armazenamento persistente e versionamento de dados.

Automatizado para rodar 24/7, ele fornece insights contínuos sobre o mercado cripto, servindo como fundação confiável para experimentação e futuros modelos de Machine Learning.

## Arquitetura da Solução

A arquitetura segue o padrão **ETL (Extract, Transform, Load)** focado em robustez e auditabilidade.

```text
├── Ingestão (Extract)
│   ├── Client API CoinGecko (Resiliente a Rate Limits e Retries)
│   ├── Coleta Tempo Real (Top 250 assets)
│   └── Coleta Histórica (Backfill de 1 ano)
│
├── Processamento (Transform)
│   ├── Limpeza e Tipagem (Pandas)
│   ├── Enriquecimento (Cálculo de OHLC on-the-fly)
│   └── Normalização Temporal
│
├── Armazenamento (Load)
│   └── SQLite (Relacional, indexado por CoinID e Timestamp)
│
└── Governança (Data Ops)
    ├── Versionamento de Dados (DVC + Snapshots Semanais)
    └── Monitoramento (Alertas de Falha via E-mail)
```

## Funcionalidades Principais

### 1. Ingestão Híbrida Inteligente (`main.py`)
- **Modo Real-Time**: Captura o estado atual do mercado (Top 250 moedas) via `crontab` (3x/dia).
- **Modo Histórico**: Capacidade de *backfill* de dados passados (configurável, ex: 365 dias) com controle automático de pausas para respeitar limites da API gratuita.

### 2. Resiliência e Monitoramento (`src/email_alert.py`)
- **Alerta de Falha**: O pipeline monitora sua própria execução. Caso a coleta retorne 0 registros, um alerta crítico é disparado por e-mail para o administrador, permitindo reação rápida.

### 3. Versionamento de Dados (`src/dvc_versioning.py`)
- **DVC (Data Version Control)**: Implementação profissional de versionamento.
    - O banco de dados `cripto.db` é rastreado como um artefato.
    - Scripts automatizados geram snapshots semanais (Segunda-feira 18:00).
    - Histórico armazenado em remote local (`dvc_store/`), garantindo reprodutibilidade dos dados de treino.

## Estrutura do Projeto

A organização reflete um pipeline de produção enxuto:

```text
/
├── main.py                 # Orquestrador do ETL (CLI Entrypoint)
├── requirements.txt        # Dependências (Pandas, DVC, Requests)
├── data/                   # Dados: cripto.db, logs e dvc_store/
├── .dvc/                   # Configurações do Data Version Control
└── src/
    ├── api_client.py       # Wrapper da API (Request Caching & Retry)
    ├── data_processor.py   # Lógica de Negócio e Tratamento
    ├── database.py         # Camada de Persistência (SQLAlchemy/SQLite)
    ├── dvc_versioning.py   # Script de Snapshot Semanal
    └── email_alert.py      # Módulo de Notificação de Falhas
```

## Guia de Instalação e Execução

### Pré-requisitos
- Python 3.10+
- Ambiente Virtual (recomendado)

### 1. Configuração do Ambiente

```bash
# Clone o repositório
git clone <URL_REPO>
cd Roadmap_MLops

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Inicialize o DVC (caso esteja clonando pela primeira vez sem os dados)
dvc pull
```

### 2. Configuração de Variáveis (Opcional)
Para receber alertas de falha por e-mail:
```bash
export EMAIL_USER="seu_email@gmail.com"
export EMAIL_PASSWORD="sua_senha_de_app"
```

### 3. Executando o Pipeline (ETL)

**Carga Inicial (Histórico):**
```bash
# Coleta 1 ano de histórico para as Top 50 moedas
python main.py --historical --days 365
```

**Coleta Tempo Real (Manual):**
```bash
python main.py --all
```

**Verificar Versionamento:**
```bash
dvc status
```

## Próximos Passos (Roadmap)

- [ ] **Data Quality**: Implementar testes de expectativa sobre os dados (Great Expectations).
- [ ] **Machine Learning**: Treinar modelos de previsão de séries temporais usando os dados versionados.
- [ ] **Cloud Storage**: Migrar o remote do DVC para AWS S3 ou Google Drive.
- [ ] **Docker**: Containerizar o pipeline para deploy em orquestradores (Airflow/K8s).

---
**Autor:** Pedro Casimiro
[Projeto Roadmap MLOps](https://github.com/pedrocasimiro1/Roadmap_MLops)
[Linkedin](https://www.linkedin.com/in/phmcasimiro/)
