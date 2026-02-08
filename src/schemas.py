"""
Definição de Contratos de Dados (Schemas) usando Pandera.

Este módulo centraliza as regras de validação para garantir a integridade
dos dados antes que eles sejam persistidos no banco de dados. Funciona como
um "Firewall de Dados", impedindo que lixo ou dados corrompidos entrem no Data Lake/Warehouse.
"""

import pandera as pa
from pandera import Column, DataFrameSchema, Check
from datetime import datetime

# Definição do Schema usando API Funcional (DataFrameSchema)
# Escolhemos DataFrameSchema ao invés de SchemaModel por ser mais flexível
# e compatível com diferentes versões do Python/Pandas em ambientes de produção.

MarketDataSchema = DataFrameSchema(
    {
        # --- Identificadores ---
        # Garantem que sabemos qual é a moeda. Não podem ser nulos.
        "id": Column(str, nullable=False, coerce=True),
        "symbol": Column(str, nullable=False, coerce=True),
        "name": Column(str, nullable=False, coerce=True),
        # --- Métricas Financeiras ---
        # Devem ser números positivos (ge=0).
        # Nullable=True porque moedas muito novas podem não ter market_cap definido ainda.
        "current_price": Column(float, checks=Check.ge(0), nullable=True, coerce=True),
        "market_cap": Column(float, checks=Check.ge(0), nullable=True, coerce=True),
        "total_volume": Column(float, checks=Check.ge(0), nullable=True, coerce=True),
        # --- Variações de Preço ---
        # Podem ser negativas, então sem verificação de >= 0.
        "price_change_24h": Column(float, nullable=True, coerce=True),
        "price_change_percentage_24h": Column(float, nullable=True, coerce=True),
        # --- Metadados de Ingestão ---
        # Data da coleta é crucial para séries temporais.
        "collected_at": Column(datetime, nullable=False),
    },
    # Configurações do Schema
    strict=False,  # Permite colunas extras no DataFrame (ex: colunas calculadas posteriormente)
    coerce=True,  # Tenta converter tipos automaticamente (ex: "100.5" virar float 100.5)
)
