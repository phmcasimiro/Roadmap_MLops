# Plataforma de Análise de Dados de Criptomoedas (MLOps)

## Visão Geral

Este projeto é uma **plataforma completa de Engenharia de Dados e MLOps** para o mercado de criptomoedas. Diferente de scripts isolados, esta solução integra todo o ciclo de vida do dado: desde a ingestão (Real-time & Batch), passando pelo processamento estruturado, armazenamento persistente, até a visualização analítica interativa.

Automatizado para rodar 24/7, ele fornece insights contínuos sobre o mercado cripto, servindo como fundação para futuros modelos de Machine Learning.

## Arquitetura da Solução

A arquitetura segue o padrão **ETL (Extract, Transform, Load)** desacoplado, com uma camada de visualização segregada.

```text
├── Ingestão (Extract)
│   ├── Client API CoinGecko (Resiliente a Rate Limits)
│   ├── Coleta Tempo Real (Top 250 assets)
│   └── Coleta Histórica (Backfill de 1 ano)
│
├── Processamento (Transform)
│   ├── Limpeza e Tipagem (Pandas)
│   ├── Enriquecimento (Calculo de Volatilidade, SMA, MACD)
│   └── Resampling Temporal (Horário/Diário)
│
├── Armazenamento (Load)
│   └── SQLite (Relacional, indexado por CoinID e Timestamp)
│
└── Apresentação (Dashboard)
    ├── Plotly Dash (Web Framework)
    ├── Análise Comparativa (Séries Temporais)
    └── Análise Técnica (Candlesticks, Indicadores)
```

## Funcionalidades Principais

### 1. Motor de Coleta Híbrida (`main.py`)

- **Modo Real-Time**: Captura o estado atual do mercado (Top 250 moedas).
- **Modo Histórico**: Realiza *backfill* de dados passados (configurável, ex: 365 dias) com gestão inteligente de limites da API.
- **Automação**: Agendamento via CRON para execução diária (Data Pipeline automatizado).

### 2. Dashboard Analítico V3 (`src/dashboard.py`)

Interface web profissional para exploração de dados:

- **Sidebar Global**: Controle unificado para seleção de ativos.
- **Aba Comparativa**: Análise de séries temporais normalizadas, permitindo comparar a performance relativa de múltiplos ativos (Highlight vs Background).
- **Aba Análise Técnica**: Gráficos de Velas (Candlesticks) com indicadores financeiros (SMA, EMA, MACD) e subplots de Volume.
- **Responsividade**: Adaptação dinâmica da granulosidade dos dados (Horário vs Diário) baseado no zoom.

## Guia de Instalação e Execução

### Pré-requisitos

- Python 3.10+
- Ambiente Virtual (recomendado)

### 1. Configuração do Ambiente

```bash
# Clone e entre na pasta
git clone <URL_REPO>
cd Roadmap_MLops

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2. Coleta de Dados (ETL)

**Carga Inicial (Histórico - Recomendado para Demo):**

```bash
# Coleta 1 ano de histórico para as Top 50 moedas
# (Atenção: Pode levar alguns minutos devido aos limites da API)

python main.py --historical --days 365 --all
```

**Coleta Tempo Real:**

```bash
# Atualiza os dados das Top 250 moedas
python main.py --all
```

**Agendamento Automático (Linux):**
O pipeline está configurado para rodar 3x ao dia (09:00, 13:00, 18:00).
Verifique com: `crontab -l`

### 3. Executando o Dashboard

Para iniciar a interface de visualização:

```bash
python run_dashboard.py
```

Acesse no seu navegador: **http://127.0.0.1:8051**

## Estrutura do Projeto

```text
/
├── main.py                 # Orquestrador do ETL (CLI)
├── run_dashboard.py        # Entrypoint do Dashboard
├── requirements.txt        # Dependências (Pandas, Requests, Dash)
├── data/                   # Armazenamento (SQLite + Logs)
└── src/
    ├── api_client.py       # Wrapper da API (Request Caching & Retry)
    ├── data_processor.py   # Lógica de Negócio e Tratamento de Dados
    ├── database.py         # Camada de Persistência (SQLAlchemy/SQLite)
    └── dashboard.py        # Aplicação Dash (Callbacks & Layout)
```

## Próximos Passos (Roadmap)

- [ ] **Dockerização**: Containerizar a aplicação para deploy simplificado.
- [ ] **Data Quality**: Implementar testes de qualidade de dados (Great Expectations).
- [ ] **Machine Learning**: Treinar modelos de previsão de séries temporais (Prophet/ARIMA).
- [ ] **Cloud Deploy**: Migração para AWS/GCP e banco Postgres.

---
**Autor:** Pedro Casimiro  

[Projeto Roadmap MLOps](https://github.com/pedrocasimiro1/Roadmap_MLops)

[Linkedin](https://www.linkedin.com/in/phmcasimiro/)
