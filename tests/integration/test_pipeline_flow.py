"""
Teste de Integração do Pipeline de Dados (End-to-End).

Este teste simula o fluxo completo de ingestão, processamento e carga,
garantindo que os componentes funcionem bem juntos.
Diferente dos testes unitários (que usam mocks pesados), aqui usamos
componentes reais onde possível (Processador, SQLite) e mock apenas onde
necessário (API Externa) para validar a persistência final dos dados.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.data_processor import CryptoDataProcessor
from src.database import CryptoDatabase
from datetime import datetime


# Fixture para setup de banco de dados isolado para este teste
@pytest.fixture
def db_integration(tmp_path):
    """Cria um banco SQLite real em uma pasta temporária."""
    return CryptoDatabase(db_path=str(tmp_path / "integration.db"))


def test_full_pipeline_flow(db_integration):
    """
    Fluxo: API (Mock) -> Processor (Real) -> Database (Real SQLite)

    Objetivo: Garantir que um dado JSON recebido da 'API' percorra
    todo o caminho, seja transformado, validado e salvo no disco corretamente.
    """

    # 1. ETAPA DE INGESTÃO (Simulada)
    # Criamos um payload como se viesse do request.json() da API CoinGecko
    raw_api_data = [
        {
            "id": "bitcoin-flow-test",
            "symbol": "btc",
            "name": "Bitcoin Test",
            "current_price": 55000.0,
            "market_cap": 1000000.0,
            "total_volume": 50000.0,
            "high_24h": 56000.0,
            "low_24h": 54000.0,
            "collected_at": "IGNORE - será substituído pelo código",
        }
    ]

    # 2. ETAPA DE PROCESSAMENTO (Real)
    processor = CryptoDataProcessor()

    try:
        # A função process_market_data aplica validações (Pandera) e transformações (Pandas)
        df_processed = processor.process_market_data(raw_api_data)
    except Exception as e:
        pytest.fail(f"Falha crítica no processamento de dados do pipeline: {e}")

    # Verificação Intermediária: Dados foram processados?
    assert not df_processed.empty
    assert (
        "volatility_24h" in df_processed.columns
    )  # Garante que feature engineering rodou

    # 3. ETAPA DE CARGA (Real)
    # Persiste o DataFrame no SQLite temporário
    rows = db_integration.insert_dataframe(df_processed)
    assert rows == 1

    # 4. ETAPA DE VERIFICAÇÃO (Consulta Real)
    # Lê do banco para garantir que o dado 'voltou' do disco corretamente
    saved_data = db_integration.get_latest_data(limit=1)

    assert saved_data.iloc[0]["coin_id"] == "bitcoin-flow-test"
    assert saved_data.iloc[0]["current_price"] == 55000.0
