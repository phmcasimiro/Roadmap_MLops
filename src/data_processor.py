"""
Processador de dados de criptomoedas.

Este módulo transforma dados brutos da API em DataFrames
estruturados e prontos para análise e persistência.
"""

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime


class CryptoDataProcessor:
    """Processador de dados de criptomoedas."""

    @staticmethod
    def process_market_data(raw_data: List[Dict]) -> pd.DataFrame:
        """
        Processa dados de mercado em DataFrame estruturado.

        Args:
            raw_data (List[Dict]): Dados brutos da API

        Returns:
            pd.DataFrame: DataFrame processado e limpo

        Raises:
            ValueError: Se raw_data estiver vazio

        Example:
            >>> processor = CryptoDataProcessor()
            >>> df = processor.process_market_data(api_data)
            >>> print(df.columns)
        """
        if not raw_data:
            raise ValueError("raw_data não pode estar vazio")

        print(f"🔄 Processando {len(raw_data)} registros...")

        # Selecionar campos relevantes
        processed_data = []

        for item in raw_data:
            record = {
                "id": item.get("id"),
                "symbol": item.get("symbol", "").upper(),
                "name": item.get("name"),
                "current_price": item.get("current_price"),
                "market_cap": item.get("market_cap"),
                "market_cap_rank": item.get("market_cap_rank"),
                "total_volume": item.get("total_volume"),
                "high_24h": item.get("high_24h"),
                "low_24h": item.get("low_24h"),
                "price_change_24h": item.get("price_change_24h"),
                "price_change_percentage_24h": item.get("price_change_percentage_24h"),
                "circulating_supply": item.get("circulating_supply"),
                "total_supply": item.get("total_supply"),
                "max_supply": item.get("max_supply"),
                "ath": item.get("ath"),  # All-time high
                "ath_date": item.get("ath_date"),
                "atl": item.get("atl"),  # All-time low
                "atl_date": item.get("atl_date"),
                "last_updated": item.get("last_updated"),
            }
            processed_data.append(record)

        # Criar DataFrame
        df = pd.DataFrame(processed_data)

        # Adicionar timestamp de coleta
        df["collected_at"] = datetime.now()

        # Converter tipos de dados
        df = CryptoDataProcessor._convert_datatypes(df)

        # Tratar valores nulos
        df = CryptoDataProcessor._handle_missing_values(df)

        # Adicionar métricas calculadas
        df = CryptoDataProcessor._add_calculated_metrics(df)

        # Validação de Contrato de Dados (Pandera)
        try:
            from src.schemas import MarketDataSchema

            print("🛡️ Validando contrato de dados...")
            MarketDataSchema.validate(df, lazy=True)
            print("✅ Contrato de dados validado com sucesso!")
        except Exception as e:
            # Re-raise para ser capturado no main
            print(f"❌ Violação de contrato de dados detectada: {e}")
            raise e

        print(f"✅ Processamento concluído! Shape: {df.shape}")
        return df

    @staticmethod
    def _convert_datatypes(df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte tipos de dados para formatos apropriados.

        Args:
            df (pd.DataFrame): DataFrame original

        Returns:
            pd.DataFrame: DataFrame com tipos convertidos
        """
        # Converter colunas de data
        date_columns = ["ath_date", "atl_date", "last_updated"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Garantir tipos numéricos
        numeric_columns = [
            "current_price",
            "market_cap",
            "total_volume",
            "high_24h",
            "low_24h",
            "price_change_24h",
            "price_change_percentage_24h",
            "circulating_supply",
            "total_supply",
            "max_supply",
            "ath",
            "atl",
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    @staticmethod
    def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        Trata valores nulos de forma apropriada.

        Args:
            df (pd.DataFrame): DataFrame original

        Returns:
            pd.DataFrame: DataFrame com valores nulos tratados
        """
        # Para max_supply, None é válido (algumas moedas não têm limite)
        # Não preencher com zero

        # Para outros campos numéricos, manter None
        # Não usar fillna indiscriminadamente

        return df

    @staticmethod
    def _add_calculated_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona métricas calculadas ao DataFrame.

        Args:
            df (pd.DataFrame): DataFrame original

        Returns:
            pd.DataFrame: DataFrame com métricas adicionais
        """
        # Volatilidade 24h (range / preço atual)
        if all(col in df.columns for col in ["high_24h", "low_24h", "current_price"]):
            df["volatility_24h"] = (
                (df["high_24h"] - df["low_24h"]) / df["current_price"] * 100
            )

        # Distância do ATH (%)
        if all(col in df.columns for col in ["ath", "current_price"]):
            df["distance_from_ath"] = (
                (df["current_price"] - df["ath"]) / df["ath"] * 100
            )

        # Distância do ATL (%)
        if all(col in df.columns for col in ["atl", "current_price"]):
            df["distance_from_atl"] = (
                (df["current_price"] - df["atl"]) / df["atl"] * 100
            )

        # Volume/Market Cap ratio
        if all(col in df.columns for col in ["total_volume", "market_cap"]):
            df["volume_to_mcap_ratio"] = df["total_volume"] / df["market_cap"]

        return df

    @staticmethod
    def get_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Gera estatísticas descritivas do dataset.

        Args:
            df (pd.DataFrame): DataFrame processado

        Returns:
            pd.DataFrame: Estatísticas descritivas
        """
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        return df[numeric_cols].describe()

    @staticmethod
    def filter_by_market_cap(df: pd.DataFrame, min_market_cap: float) -> pd.DataFrame:
        """
        Filtra criptomoedas por capitalização mínima de mercado.

        Args:
            df (pd.DataFrame): DataFrame original
            min_market_cap (float): Capitalização mínima

        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        return df[df["market_cap"] >= min_market_cap].copy()

    @staticmethod
    def sort_by_metric(
        df: pd.DataFrame, metric: str, ascending: bool = False
    ) -> pd.DataFrame:
        """
        Ordena DataFrame por métrica específica.

        Args:
            df (pd.DataFrame): DataFrame original
            metric (str): Nome da coluna para ordenação
            ascending (bool): Ordem crescente se True

        Returns:
            pd.DataFrame: DataFrame ordenado
        """
        if metric not in df.columns:
            raise ValueError(f"Métrica '{metric}' não encontrada no DataFrame")

        return df.sort_values(by=metric, ascending=ascending).copy()

    @staticmethod
    def process_historical_data(coin_id: str, raw_history: Dict) -> pd.DataFrame:
        """
        Processa dados históricos de uma moeda especifica.

        Args:
            coin_id (str): ID da moeda
            raw_history (Dict): Dados retornados por market_chart/range

        Returns:
            pd.DataFrame: DataFrame processado
        """
        if not raw_history or "prices" not in raw_history:
            return pd.DataFrame()

        # Extrair dados
        # raw_history['prices'] = [[timestamp, price], ...]
        prices = raw_history.get("prices", [])
        market_caps = raw_history.get("market_caps", [])
        total_volumes = raw_history.get("total_volumes", [])

        # Criar dicionário indexado pelo timestamp para fusão
        data_dict = {}

        for ts, price in prices:
            data_dict[ts] = {"collected_at": ts, "current_price": price}

        for ts, mcap in market_caps:
            if ts in data_dict:
                data_dict[ts]["market_cap"] = mcap

        for ts, vol in total_volumes:
            if ts in data_dict:
                data_dict[ts]["total_volume"] = vol

        # Converter para lista
        records = []
        for ts, values in data_dict.items():
            # Converter timestamp ms para datetime
            dt_obj = datetime.fromtimestamp(ts / 1000)

            record = {
                "coin_id": coin_id,
                "symbol": "",  # Será preenchido externamente se possível ou ignorado (é NOT NULL no DB, atenção)
                # Como o DB exige symbol e name (NOT NULL), precisamos pegá-los de algum lugar.
                # O endpoint de histórico NÂO retorna symbol/name.
                # Assumiremos que o chamador vai complementar ou usaremos placeholders.
                "collected_at": dt_obj,
                "current_price": values.get("current_price"),
                "market_cap": values.get("market_cap"),
                "total_volume": values.get("total_volume"),
                # Campos obrigatórios no DB que não temos no histórico:
                # symbol, name.
                # Vamos preencher com placeholder aqui e o chamador corrige.
            }
            records.append(record)

        df = pd.DataFrame(records)
        return df


def main():
    """Função de teste do módulo."""
    # Dados de exemplo
    sample_data = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 45000,
            "market_cap": 880000000000,
            "market_cap_rank": 1,
            "total_volume": 28000000000,
            "high_24h": 46000,
            "low_24h": 44000,
            "price_change_24h": 500,
            "price_change_percentage_24h": 1.12,
            "circulating_supply": 19500000,
            "total_supply": 21000000,
            "max_supply": 21000000,
            "ath": 69000,
            "ath_date": "2021-11-10T14:24:11.849Z",
            "atl": 67.81,
            "atl_date": "2013-07-06T00:00:00.000Z",
            "last_updated": "2024-01-31T12:00:00.000Z",
        }
    ]

    processor = CryptoDataProcessor()
    df = processor.process_market_data(sample_data)

    print("\n📊 DataFrame Processado:")
    print(df.info())

    print("\n📈 Primeiras linhas:")
    print(df.head())

    print("\n📉 Estatísticas:")
    print(processor.get_summary_statistics(df))


if __name__ == "__main__":
    main()
