"""
Gerenciador de banco de dados SQLite para criptomoedas.

Este módulo é responsável por toda a camada de persistência de dados do projeto.
Ele implementa o padrão DAO (Data Access Object) simplificado para interagir
com o banco SQLite, oferecendo métodos para inserir, consultar e gerenciar
os dados financeiros coletados.
"""

import sqlite3
import pandas as pd
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from src.logger import get_logger

logger = get_logger(__name__)


class CryptoDatabase:
    """
    Gerenciador de Banco de Dados SQLite.

    Responsável por criar a estrutura de tabelas, inserir dados e
    realizar consultas. Utiliza o padrão Context Manager para
    gerenciar conexões com segurança.
    """

    def __init__(self, db_path: str = "data/cripto.db"):
        """
        Inicializa a conexão com o banco de dados.

        Ao instanciar, verificamos se o diretório existe e garantimos
        que a estrutura de tabelas esteja criada.

        Args:
            db_path (str): Caminho relativo ou absoluto para o arquivo .db.
                           Padrão: 'data/cripto.db'.
        """
        self.db_path = Path(db_path)

        # Garante que o diretório pai exista (ex: 'data/')
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Inicializa o schema do banco (tabelas e índices)
        self._create_tables()

    @contextmanager
    def _get_connection(self):
        """
        Context Manager para gerenciar conexões com o banco de forma segura.

        Garanti que a conexão seja fechada automaticamente e que transações
        sejam commitadas em caso de sucesso ou revertidas (rollback) em caso de erro.

        Yields:
            sqlite3.Connection: Objeto de conexão ativa.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()  # Persiste as mudanças se não houver erro
        except Exception as e:
            conn.rollback()  # Desfaz mudanças se ocorrer erro
            raise e
        finally:
            conn.close()  # Fecha a conexão sempre

    def _create_tables(self):
        """
        Cria a estrutura do banco de dados (DDL) se ela não existir.

        Define a tabela 'cryptocurrency_data' e seus índices para performance.
        A restrição UNIQUE(coin_id, collected_at) impede duplicidade de registros
        para a mesma moeda no mesmo timestamp.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS cryptocurrency_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            current_price REAL,
            market_cap REAL,
            market_cap_rank INTEGER,
            total_volume REAL,
            high_24h REAL,
            low_24h REAL,
            price_change_24h REAL,
            price_change_percentage_24h REAL,
            circulating_supply REAL,
            total_supply REAL,
            max_supply REAL,
            ath REAL,
            ath_date TEXT,
            atl REAL,
            atl_date TEXT,
            volatility_24h REAL,
            distance_from_ath REAL,
            distance_from_atl REAL,
            volume_to_mcap_ratio REAL,
            last_updated TEXT,
            collected_at TEXT NOT NULL,
            UNIQUE(coin_id, collected_at)
        );
        
        -- Índices para acelerar consultas comuns
        CREATE INDEX IF NOT EXISTS idx_coin_id 
        ON cryptocurrency_data(coin_id);
        
        CREATE INDEX IF NOT EXISTS idx_collected_at 
        ON cryptocurrency_data(collected_at);
        
        CREATE INDEX IF NOT EXISTS idx_market_cap_rank 
        ON cryptocurrency_data(market_cap_rank);
        """

        with self._get_connection() as conn:
            conn.executescript(create_table_sql)
        logger.info("Tabelas verificadas/criadas com sucesso.")

    def insert_dataframe(self, df: pd.DataFrame) -> int:
        """
        Insere um DataFrame do Pandas diretamente no banco de dados.

        Realiza o mapeamento de colunas e tratamento de tipos antes da inserção.

        Args:
            df (pd.DataFrame): DataFrame contendo os dados processados.

        Returns:
            int: Número de registros efetivamente inseridos.
        """
        if df.empty:
            logger.warning("DataFrame vazio, nada a inserir.")
            return 0

        # Prepara o DataFrame para inserção (cópia para não alterar o original)
        df_to_insert = df.copy()

        # Mapeia 'id' da API para 'coin_id' do banco
        if "id" in df_to_insert.columns:
            df_to_insert.rename(columns={"id": "coin_id"}, inplace=True)

        # Converte datas para string (SQLite não tem tipo DATE nativo)
        for col in df_to_insert.select_dtypes(include=["datetime64"]).columns:
            df_to_insert[col] = df_to_insert[col].astype(str)

        try:
            with self._get_connection() as conn:
                # 'if_exists="append"' adiciona aos dados existentes
                rows_inserted = df_to_insert.to_sql(
                    "cryptocurrency_data", conn, if_exists="append", index=False
                )

            logger.info(f"{rows_inserted} registros inseridos no banco")
            return rows_inserted

        except sqlite3.IntegrityError as e:
            # Captura violação da constraint UNIQUE (dados duplicados)
            logger.warning(f"Alguns registros já existem (ignorados): {e}")
            return 0

        except Exception as e:
            logger.error(f"Erro ao inserir dados no banco: {e}")
            return 0

    def get_latest_data(self, limit: int = 10) -> pd.DataFrame:
        """
        Recupera os registros mais recentes inseridos no banco.

        Útil para inspeção rápida ou para alimentar dashboards em tempo real.

        Args:
            limit (int): Quantidade máxima de registros a retornar.

        Returns:
            pd.DataFrame: Tabela contendo os últimos registros, ordenados por data.
        """
        query = """
        SELECT * FROM cryptocurrency_data
        ORDER BY collected_at DESC, market_cap_rank ASC
        LIMIT ?
        """

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(limit,))

        return df

    def get_coin_history(
        self, coin_id: str, days: int = 7, enrich_data: bool = False
    ) -> pd.DataFrame:
        """
        Busca o histórico de preços de uma moeda específica.

        Args:
            coin_id (str): ID da criptomoeda (ex: 'bitcoin').
            days (int): Quantos dias atrás buscar.
            enrich_data (bool): Se True, aplica reamostragem diária (OHLC) e
                                calcula médias móveis (SMA).

        Returns:
            pd.DataFrame: Histórico filtrado e opcionalmente enriquecido.
        """
        query = """
        SELECT * FROM cryptocurrency_data
        WHERE coin_id = ?
        AND collected_at >= datetime('now', '-' || ? || ' days')
        ORDER BY collected_at ASC
        """

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(coin_id, days))

        if df.empty:
            return df

        # Garante que a coluna de data seja datetime (não string)
        df["collected_at"] = pd.to_datetime(df["collected_at"])

        if enrich_data:
            # --- Lógica de Enriquecimento de Dados (Feature Engineering) ---

            df.set_index("collected_at", inplace=True)

            # Resampling: Transforma dados irregulares em barras diárias (Day Candles)
            # 'D' = Frequência Diária
            df_enriched = df.resample("D").agg(
                {
                    "current_price": [
                        "first",  # Open
                        "max",  # High
                        "min",  # Low
                        "last",  # Close
                    ],
                    "total_volume": "max",
                }
            )

            # Renomeia colunas para padrão financeiro (OHLC)
            df_enriched.columns = ["open", "high", "low", "close", "volume"]

            # Preenchimento de falhas (Forward Fill): Copia o valor do dia anterior
            # se houver um dia sem coleta dados.
            df_enriched.fillna(method="ffill", inplace=True)

            # Médias Móveis Simples (SMA)
            df_enriched["sma_50"] = df_enriched["close"].rolling(window=50).mean()
            df_enriched["sma_200"] = df_enriched["close"].rolling(window=200).mean()

            df_enriched.reset_index(inplace=True)
            return df_enriched

        return df

    def get_statistics(self) -> dict:
        """
        Calcula estatísticas gerais sobre o estado do banco de dados.

        Returns:
            dict: Dicionário contendo contagens, datas e médias.
        """
        # Dicionário de queries SQL analíticas
        queries = {
            "total_records": "SELECT COUNT(*) as count FROM cryptocurrency_data",
            "unique_coins": "SELECT COUNT(DISTINCT coin_id) as count FROM cryptocurrency_data",
            "date_range": """
                SELECT 
                    MIN(collected_at) as first_collection,
                    MAX(collected_at) as last_collection
                FROM cryptocurrency_data
            """,
            "avg_market_cap": """
                SELECT AVG(market_cap) as avg_mcap 
                FROM cryptocurrency_data
                WHERE market_cap IS NOT NULL
            """,
        }

        stats = {}
        with self._get_connection() as conn:
            for key, query in queries.items():
                result = pd.read_sql_query(query, conn)
                # Converte o resultado (Series) para dicionário simples
                stats[key] = result.iloc[0].to_dict()

        return stats

    def delete_old_data(self, days_to_keep: int = 30) -> int:
        """
        Rotina de limpeza: Remove registros mais antigos que X dias.

        Args:
            days_to_keep (int): Horizonte de tempo para manter os dados.

        Returns:
            int: Quantidade de linhas deletadas.
        """
        query = """
        DELETE FROM cryptocurrency_data
        WHERE collected_at < datetime('now', '-' || ? || ' days')
        """

        with self._get_connection() as conn:
            cursor = conn.execute(query, (days_to_keep,))
            rows_deleted = cursor.rowcount

        print(f"[INFO] {rows_deleted} registros antigos removidos")
        return rows_deleted


def main():
    """Função para teste unitário manual da classe."""
    print("Iniciando teste de banco de dados...")

    # Usa um banco temporário para não sujar o principal
    db = CryptoDatabase("data/test_cripto.db")

    # Criação de dados fictícios (Mock)
    sample_df = pd.DataFrame(
        [
            {
                "id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "current_price": 45000,
                "market_cap": 880000000000,
                "market_cap_rank": 1,
                "collected_at": datetime.now(),
            }
        ]
    )

    # Teste de Inserção
    db.insert_dataframe(sample_df)

    # Teste de Leitura
    latest = db.get_latest_data(limit=5)
    print("\nDados mais recentes:")
    print(latest)

    # Teste de Estatísticas
    stats = db.get_statistics()
    print("\nEstatísticas do banco:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
