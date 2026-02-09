"""
Testes Unitários para Contratos de Dados (schemas.py using Pandera).

Este módulo garante que as regras de qualidade de dados definidas no Schema
estão sendo aplicadas corretamente. Testamos tanto casos positivos (dados válidos)
quanto negativos (dados corrompidos ou fora do esperado).
"""

import pytest
import pandas as pd
import pandera as pa
from src.schemas import MarketDataSchema
from datetime import datetime


def test_schema_valid_data():
    """
    Caso Positivo: Um DataFrame contendo todas as colunas obrigatórias
    e tipos corretos deve passar pela validação sem erros.
    """
    data = {
        "id": ["bitcoin"],
        "symbol": ["btc"],
        "name": ["Bitcoin"],
        "current_price": [50000.0],
        "market_cap": [1000.0],
        "total_volume": [500.0],
        "collected_at": [datetime.now()],
    }
    df = pd.DataFrame(data)

    # A validação retorna o próprio DF se bem-sucedida, ou levanta exceção se falhar
    validated_df = MarketDataSchema.validate(df)
    assert isinstance(validated_df, pd.DataFrame)


def test_schema_invalid_price():
    """
    Caso Negativo (Regra de Negócio): Preço não pode ser negativo.
    O teste garante que o Pandera levanta SchemaErrors ao encontrar violações.
    """
    data = {
        "id": ["bitcoin"],
        "symbol": ["btc"],
        "name": ["Bitcoin"],
        "current_price": [-100.0],  # Violação: Check.ge(0)
        "collected_at": [datetime.now()],
    }
    df = pd.DataFrame(data)

    # Esperamos que uma exceção específica do Pandera seja lançada
    with pytest.raises(pa.errors.SchemaErrors):
        MarketDataSchema.validate(df, lazy=True)


def test_schema_missing_column():
    """
    Caso Negativo (Estrutura): Colunas obrigatórias faltando.
    Garante que não aceitamos dados parciais que quebrariam o banco de dados.
    """
    data = {
        "id": ["bitcoin"],
        # Colunas 'symbol' e 'name' foram omitidas propositalmente
        "current_price": [50000.0],
        "collected_at": [datetime.now()],
    }
    df = pd.DataFrame(data)

    with pytest.raises(pa.errors.SchemaErrors):
        MarketDataSchema.validate(df, lazy=True)
