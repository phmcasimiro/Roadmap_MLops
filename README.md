# Plataforma de Análise de Dados de Criptomoedas (MLOps)

## Visão Geral

Este projeto é uma **plataforma de Engenharia de Dados** para o mercado de criptomoedas. Focada na robustez e automação, a solução gerencia todo o ciclo de vida do dado: desde a ingestão (Real-time & Batch) até o armazenamento estruturado, pronto para consumo por modelos de Machine Learning.

Automatizado para rodar 24/7, ele captura variações de mercado com granularidade fina (3x ao dia), criando um dataset histórico valioso.

## Arquitetura da Solução

A arquitetura segue o padrão **ETL (Extract, Transform, Load)**.

```text
├── Ingestão (Extract)
│   ├── Client API CoinGecko (Resiliente a Rate Limits e Retries)
│   ├── Coleta Tempo Real (Top 250 assets)
│   └── Coleta Histórica (Backfill de 1+ ano)
│
├── Processamento (Transform)
│   ├── Limpeza e Tipagem (Pandas)
│   ├── Enriquecimento (Cálculo de OHLC, Volatilidade)
│   └── Normalização Temporal
│
└── Armazenamento (Load)
    └── SQLite (Relacional, indexado por CoinID e Timestamp)
```

## Funcionalidades Principais

### 1. Ingestão Híbrida Inteligente (`main.py`)
- **Modo Real-Time**: Captura o estado atual do mercado (Top 250 moedas) via `crontab` (3x/dia).
- **Modo Histórico**: Capacidade de *backfill* de dados passados (configurável, ex: 365 dias) com controle automático de pausas para respeitar limites da API gratuita.

- **Modo Real-Time**: Captura o estado atual do mercado (Top 250 moedas).
- **Modo Histórico**: Realiza *backfill* de dados passados (configurável, ex: 365 dias) com gestão inteligente de limites da API.
- **Automação**: Agendamento via CRON para execução frequente.

### 2. Camada de Dados (`src/database.py`)

- **Schema Otimizado**: Tabelas indexadas para consultas rápidas de séries temporais.
- **Enriquecimento On-the-fly**: Capacidade de gerar agregação OHLC (Open, High, Low, Close) e indicadores técnicos (SMA) diretamente na consulta.

### 3. Resiliência e Monitoramento (`src/backup_manager.py`, `src/email_alert.py`)

- **Backup Estruturado**: Snapshots semanais do banco `cripto.db` salvos em `data/backups/`. Política de ratenção automática (mantém os últimos 4).
- **Alerta de Falha**: Monitoramento ativo da ingestão. Se zero registros forem capturados, um e-mail é disparado para o admin.

## Guia de Instalação e Execução

### Pré-requisitos
- Python 3.10+
- Ambiente Virtual (recomendado)
- (Opcional) Conta Gmail para alertas

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

# Configuração de Alertas (Opcional)
# Crie um arquivo .env ou exporte as variáveis:
export EMAIL_USER="seu_email@gmail.com"
export EMAIL_PASSWORD="sua_senha_de_app"
```

### 2. Configuração de Variáveis (Opcional)
Para receber alertas de falha por e-mail:
```bash
export EMAIL_USER="seu_email@gmail.com"
export EMAIL_PASSWORD="sua_senha_de_app"
```

**Carga Inicial (Histórico - Recomendado):**

**Carga Inicial (Histórico):**
```bash
# Coleta 1 ano de histórico para as Top 50 moedas
python main.py --historical --days 365
```

**Coleta Tempo Real (Manual):**
```bash
python main.py --all
```

**Agendamento Automático (Linux):**
O pipeline está configurado para rodar 3x ao dia (09:00, 13:00, 18:00).
Verifique com: `crontab -l`

## Estrutura do Projeto

```text
/
├── main.py                 # Orquestrador do ETL (CLI)
├── requirements.txt        # Dependências (Pandas, Requests)
├── data/                   # Armazenamento (SQLite + Logs)
└── src/
    ├── api_client.py       # Wrapper da API (Request Caching & Retry)
    ├── data_processor.py   # Lógica de Negócio e Tratamento de Dados
    └── database.py         # Camada de Persistência (SQLAlchemy/SQLite)
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
