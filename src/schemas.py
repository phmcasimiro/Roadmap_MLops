"""
Definição de Contratos de Dados (Schemas) usando Pandera.

Este módulo centraliza as regras de validação para garantir a integridade
dos dados antes que eles sejam persistidos no banco de dados.
"""

import pandera as pa
from pandera import Column, DataFrameSchema, Check
from datetime import datetime

# Definição do Schema usando API Funcional (DataFrameSchema)
# Mais compatível que SchemaModel em algumas versões/ambientes
MarketDataSchema = DataFrameSchema(
    {
        # Identificação
        "id": Column(str, nullable=False, coerce=True),
        "symbol": Column(str, nullable=False, coerce=True),
        "name": Column(str, nullable=False, coerce=True),
        # Métricas Financeiras
        "current_price": Column(float, checks=Check.ge(0), nullable=True, coerce=True),
        "market_cap": Column(float, checks=Check.ge(0), nullable=True, coerce=True),
        "total_volume": Column(float, checks=Check.ge(0), nullable=True, coerce=True),
        # Variações
        "price_change_24h": Column(float, nullable=True, coerce=True),
        "price_change_percentage_24h": Column(float, nullable=True, coerce=True),
        # Metadados
        "collected_at": Column(datetime, nullable=False),
    },
    strict=False,
    coerce=True,
)
