"""
Testes Unitários para a Camada de Banco de Dados (database.py).

Este módulo utiliza um banco SQLite temporário (criado via fixture) para validar:
1. Criação correta (DDL) de tabelas e índices.
2. Inserção de DataFrames (Persistência).
3. Restrições de integridade (Unicidade de registros).
"""

import pytest
import sqlite3
import pandas as pd
from src.database import CryptoDatabase
from datetime import datetime


@pytest.fixture
def db_path(tmp_path):
    """
    Fixture que define um caminho temporário para o arquivo .db.
    O 'tmp_path' é fornecido pelo pytest e é limpo após a execução.
    """
    return str(tmp_path / "test_cripto.db")


@pytest.fixture
def db(db_path):
    """Fixture que retorna uma instância inicializada do CryptoDatabase."""
    return CryptoDatabase(db_path=db_path)


def test_create_tables(db, db_path):
    """
    Verifica se a tabela principal 'cryptocurrency_data' foi criada
    automaticamente durante a inicialização da classe.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Consulta o catálogo do SQLite (sqlite_master)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cryptocurrency_data';"
        )
        table = cursor.fetchone()
        assert table is not None


def test_insert_dataframe(db):
    """
    Testa a inserção de um DataFrame Pandas no banco.
    Verifica se 1 registro inserido resulta em 1 linha no banco.
    """
    data = [
        {
            "id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "current_price": 50000.0,
            "market_cap": 1e9,
            "market_cap_rank": 1,
            "collected_at": datetime.now(),
        }
    ]
    df = pd.DataFrame(data)

    inserted = db.insert_dataframe(df)
    assert inserted == 1

    # Valida se os dados inseridos podem ser lidos corretamente
    latest = db.get_latest_data()
    assert len(latest) == 1
    assert latest.iloc[0]["coin_id"] == "bitcoin"


def test_insert_duplicate_data(db):
    """
    Testa a restrição UNIQUE (coin_id, collected_at).
    Tentar inserir o mesmo dado com o mesmo timestamp deve falhar silenciosamente
    (tratado pelo código para retornar 0 inserções) e não gerar duplicidade.
    """
    now = datetime.now()
    data = [
        {
            "id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "collected_at": now,  # Timestamp fixo para gerar colisão
        }
    ]
    df = pd.DataFrame(data)

    # Primeira inserção: Deve ocorrer com sucesso
    assert db.insert_dataframe(df) == 1

    # Segunda inserção (cópia exata): Deve ser ignorada pelo INSERT OR IGNORE (ou lógica similar)
    # O método retorna 0 para indicar que nada novo foi persistido.
    assert db.insert_dataframe(df) == 0
