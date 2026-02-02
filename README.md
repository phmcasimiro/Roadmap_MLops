# Sistema de Coleta de Dados de Criptomoedas

Sistema completo para coleta, processamento e armazenamento de dados de criptomoedas usando Python, Pandas e SQLite.

## Descrição

Este projeto demonstra os **fundamentos de programação** aplicados a um caso real de MLOps:

- **Lógica de programação**: Fluxo sequencial de coleta → processamento → persistência
- **Estruturas de dados**: Listas, dicionários, DataFrames
- **Paradigmas**: OOP (classes) e Funcional (métodos estáticos)
- **Boas práticas**: PEP 8, docstrings, tratamento de erros
- **Versionamento**: Git com commits semânticos

## Arquitetura

```text
projeto_cripto/
├── .gitignore              # Arquivos ignorados pelo Git
├── README.md               # Este arquivo
├── requirements.txt        # Dependências Python
├── main.py                 # Script principal
├── src/                    # Código fonte
│   ├── __init__.py
│   ├── api_client.py       # Cliente API CoinGecko
│   ├── data_processor.py   # Processamento com Pandas
│   └── database.py         # Persistência SQLite
└── data/                   # Banco de dados (criado automaticamente)
    └── cripto.db
```

## Instalação

### 1. Clonar o repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd projeto_cripto
```

### 2. Criar ambiente virtual (recomendado)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## Uso

### Execução básica

```bash
python main.py
```

### Opções disponíveis

```bash
# Coletar 20 criptomoedas (Padrão: 30)
python main.py --limit 20

# Coleta em Tempo Real de TODAS as criptomoedas (Top 250)
python main.py --all

# Coleta de DADOS HISTÓRICOS (último ano, Top 50 moedas)
python main.py --historical --all

# Personalizar histórico (ex: 30 dias, Top 10 moedas)
python main.py --historical --days 30 --limit 10

# Modo verboso (mais informações)
python main.py --verbose

# Especificar caminho do banco
python main.py --db-path meu_banco.db

# Ajuda
python main.py --help
```

## Funcionalidades

### 1. Coleta de Dados (API Client)

- Consome API pública CoinGecko
- Tratamento robusto de erros
- Context manager para gerenciamento de sessão

### 2. Processamento (Pandas)

- Conversão de tipos de dados
- Tratamento de valores nulos
- Métricas calculadas:
  - Volatilidade 24h
  - Distância do ATH/ATL
  - Ratio Volume/Market Cap

### 3. Persistência (SQLite)

- Banco de dados relacional
- Índices otimizados
- Queries para análise histórica
- Operações CRUD completas

## Exemplos de Queries

```python
from src.database import CryptoDatabase

db = CryptoDatabase()

# Top 10 por market cap
top10 = db.get_top_by_market_cap(limit=10)

# Histórico do Bitcoin (7 dias)
btc_history = db.get_coin_history('bitcoin', days=7)

# Moedas com mudança > 5%
volatile = db.get_price_changes(min_change_pct=5.0)

# Estatísticas gerais
stats = db.get_statistics()
```

## Conceitos Demonstrados

### Lógica de Programação

- Sequência: Fluxo linear de execução
- Condição: Validações e tratamento de erros
- Repetição: Loops para processar múltiplos registros

### Estruturas de Dados

- **Listas**: Armazenamento de múltiplas criptomoedas
- **Dicionários**: Dados estruturados da API
- **DataFrames**: Processamento eficiente com Pandas

### Paradigmas

- **OOP**: Classes `CoinGeckoClient`, `CryptoDataProcessor`, `CryptoDatabase`
- **Funcional**: Métodos estáticos para transformações de dados

### Boas Práticas

- Nomenclatura PEP 8
- Docstrings completas
- Type hints
- Tratamento de exceções
- Context managers
- Separação de responsabilidades

## Workflow Git

### Inicializar repositório

```bash
git init
git add .
git commit -m "feat: implementa sistema de coleta de dados de criptomoedas"
```

### Commits semânticos

```bash
# Nova funcionalidade
git commit -m "feat(api): adiciona suporte para múltiplas moedas"

# Correção de bug
git commit -m "fix(database): corrige inserção de dados duplicados"

# Documentação
git commit -m "docs(readme): adiciona exemplos de uso"

# Refatoração
git commit -m "refactor(processor): simplifica cálculo de métricas"
```

### Conectar ao GitHub

```bash
# Criar repositório no GitHub primeiro, depois:
git remote add origin https://github.com/seu-usuario/projeto-cripto.git
git branch -M main
git push -u origin main
```

## Testes

### Testar módulos individualmente

```bash
# Testar API client
python -m src.api_client

# Testar processador
python -m src.data_processor

# Testar database
python -m src.database
```

## Próximos Passos

- [ ] Adicionar testes unitários (pytest)
- [ ] Implementar logging estruturado
- [ ] Criar dashboard de visualização
- [ ] Adicionar cache de requisições
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Adicionar análise de sentimento de notícias

## Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## Licença

Este projeto é open source e está disponível sob a licença MIT.

## Autor

**Pedro Casimiro**: <phmcasimiro@gmail.com>

**Data**: Janeiro 2026

## Links

[Linkedin](https://www.linkedin.com/in/phmcasimiro/)

[GitHub](https://github.com/phmcasimiro)

## Recursos

- [API CoinGecko](https://www.coingecko.com/en/api)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

Se este projeto foi útil, considere dar uma estrela no GitHub!
