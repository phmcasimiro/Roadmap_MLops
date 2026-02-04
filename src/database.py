"""
Gerenciador de banco de dados SQLite para criptomoedas.

Este módulo implementa a persistência de dados em banco SQLite
com operações CRUD e queries otimizadas.
"""

import sqlite3
import pandas as pd
from typing import Optional, List
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager


class CryptoDatabase:
    """Gerenciador de banco de dados para criptomoedas."""

    def __init__(self, db_path: str = "data/cripto.db"):
        """
        Inicializa conexão com banco de dados.

        Args:
            db_path (str): Caminho para o arquivo do banco SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()

    @contextmanager
    def _get_connection(self):
        """Context manager para conexão com banco."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _create_tables(self):
        """Cria tabelas se não existirem."""
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
        
        CREATE INDEX IF NOT EXISTS idx_coin_id 
        ON cryptocurrency_data(coin_id);
        
        CREATE INDEX IF NOT EXISTS idx_collected_at 
        ON cryptocurrency_data(collected_at);
        
        CREATE INDEX IF NOT EXISTS idx_market_cap_rank 
        ON cryptocurrency_data(market_cap_rank);
        """

        with self._get_connection() as conn:
            conn.executescript(create_table_sql)

        print(f"✅ Banco de dados inicializado: {self.db_path}")

    def insert_dataframe(self, df: pd.DataFrame) -> int:
        """
        Insere DataFrame no banco de dados.

        Args:
            df (pd.DataFrame): DataFrame com dados processados

        Returns:
            int: Número de registros inseridos

        Example:
            >>> db = CryptoDatabase()
            >>> rows_inserted = db.insert_dataframe(df)
        """
        if df.empty:
            print("⚠️  DataFrame vazio, nada a inserir")
            return 0

        # Renomear coluna 'id' para 'coin_id' para evitar conflito
        df_to_insert = df.copy()
        if "id" in df_to_insert.columns:
            df_to_insert.rename(columns={"id": "coin_id"}, inplace=True)

        # Converter timestamps para string
        for col in df_to_insert.select_dtypes(include=["datetime64"]).columns:
            df_to_insert[col] = df_to_insert[col].astype(str)

        try:
            with self._get_connection() as conn:
                rows_inserted = df_to_insert.to_sql(
                    "cryptocurrency_data", conn, if_exists="append", index=False
                )

            print(f"✅ {rows_inserted} registros inseridos no banco")
            return rows_inserted

        except sqlite3.IntegrityError as e:
            print(f"⚠️  Alguns registros já existem: {e}")
            return 0

        except Exception as e:
            print(f"❌ Erro ao inserir dados: {e}")
            raise

    def get_latest_data(self, limit: int = 10) -> pd.DataFrame:
        """
        Obtém os dados mais recentes do banco.

        Args:
            limit (int): Número máximo de registros

        Returns:
            pd.DataFrame: DataFrame com dados mais recentes
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
        Obtém histórico de uma criptomoeda específica.

        Args:
            coin_id (str): ID da criptomoeda
            days (int): Número de dias de histórico
            enrich_data (bool): Se True, resurn OHLC diário e médias móveis

        Returns:
            pd.DataFrame: Histórico da criptomoeda
        """
        query = """
        SELECT * FROM cryptocurrency_data
        WHERE coin_id = ?
        AND collected_at >= datetime('now', '-' || ? || ' days')
        ORDER BY collected_at ASC
        """
        # Nota: ORDER BY ASC é importante para cálculo de rolling window e candles

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(coin_id, days))

        if df.empty:
            return df

        # Converter string para datetime
        df["collected_at"] = pd.to_datetime(df["collected_at"])

        if enrich_data:
            # Configurar index
            df.set_index("collected_at", inplace=True)

            # Resampling Diário (OHLCV)
            # Como a coleta pode variar, o resample garante consistência diária
            df_enriched = df.resample("D").agg(
                {
                    "current_price": [
                        "first",
                        "max",
                        "min",
                        "last",
                    ],  # Open, High, Low, Close
                    "total_volume": "max",  # Volume do dia
                }
            )

            # Aplanar colunas MultiIndex
            df_enriched.columns = ["open", "high", "low", "close", "volume"]

            # Preencher dias sem coleta (se houver buracos, usa ffill para não quebrar gráfico)
            df_enriched.fillna(method="ffill", inplace=True)

            # Calcular Indicadores Técnicos
            df_enriched["sma_50"] = df_enriched["close"].rolling(window=50).mean()
            df_enriched["sma_200"] = df_enriched["close"].rolling(window=200).mean()

            # Resetar index para retornar coluna de data
            df_enriched.reset_index(inplace=True)

            return df_enriched

        return df

    def get_top_by_market_cap(
        self, limit: int = 10, date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Obtém top criptomoedas por capitalização de mercado.

        Args:
            limit (int): Número de criptomoedas
            date (str): Data específica (formato ISO) ou None para mais recente

        Returns:
            pd.DataFrame: Top criptomoedas
        """
        if date:
            query = """
            SELECT * FROM cryptocurrency_data
            WHERE DATE(collected_at) = DATE(?)
            ORDER BY market_cap_rank ASC
            LIMIT ?
            """
            params = (date, limit)
        else:
            query = """
            SELECT * FROM (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY coin_id 
                    ORDER BY collected_at DESC
                ) as rn
                FROM cryptocurrency_data
            )
            WHERE rn = 1
            ORDER BY market_cap_rank ASC
            LIMIT ?
            """
            params = (limit,)

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)

        return df

    def get_price_changes(self, min_change_pct: float = 5.0) -> pd.DataFrame:
        """
        Obtém criptomoedas com mudança de preço significativa.

        Args:
            min_change_pct (float): Mudança mínima percentual (absoluta)

        Returns:
            pd.DataFrame: Criptomoedas com mudanças significativas
        """
        query = """
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY coin_id 
                ORDER BY collected_at DESC
            ) as rn
            FROM cryptocurrency_data
        )
        WHERE rn = 1
        AND ABS(price_change_percentage_24h) >= ?
        ORDER BY ABS(price_change_percentage_24h) DESC
        """

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(min_change_pct,))

        return df

    def get_statistics(self) -> dict:
        """
        Obtém estatísticas gerais do banco de dados.

        Returns:
            dict: Estatísticas do banco
        """
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
                stats[key] = result.iloc[0].to_dict()

        return stats

    def delete_old_data(self, days_to_keep: int = 30) -> int:
        """
        Remove dados antigos do banco.

        Args:
            days_to_keep (int): Número de dias a manter

        Returns:
            int: Número de registros removidos
        """
        query = """
        DELETE FROM cryptocurrency_data
        WHERE collected_at < datetime('now', '-' || ? || ' days')
        """

        with self._get_connection() as conn:
            cursor = conn.execute(query, (days_to_keep,))
            rows_deleted = cursor.rowcount

        print(f"🗑️  {rows_deleted} registros antigos removidos")
        return rows_deleted


def main():
    """Função de teste do módulo."""
    # Criar banco de teste
    db = CryptoDatabase("data/test_cripto.db")

    # Dados de exemplo
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

    # Inserir dados
    db.insert_dataframe(sample_df)

    # Buscar dados
    latest = db.get_latest_data(limit=5)
    print("\n📊 Dados mais recentes:")
    print(latest)

    # Estatísticas
    stats = db.get_statistics()
    print("\n📈 Estatísticas do banco:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
