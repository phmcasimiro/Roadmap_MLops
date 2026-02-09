import pytest
import pandas as pd
from datetime import datetime


@pytest.fixture
def mock_api_data():
    """Retorna dados simulados da API CoinGecko."""
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 50000.0,
            "market_cap": 1000000000.0,
            "market_cap_rank": 1,
            "total_volume": 50000000.0,
            "high_24h": 51000.0,
            "low_24h": 49000.0,
            "price_change_24h": 1000.0,
            "price_change_percentage_24h": 2.0,
            "circulating_supply": 19000000.0,
            "total_supply": 21000000.0,
            "max_supply": 21000000.0,
            "ath": 69000.0,
            "ath_date": "2021-11-10T00:00:00.000Z",
            "atl": 67.0,
            "atl_date": "2013-07-06T00:00:00.000Z",
            "last_updated": "2023-01-01T00:00:00.000Z",
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 3000.0,
            "market_cap": 500000000.0,
            "market_cap_rank": 2,
            "total_volume": 20000000.0,
            "high_24h": 3100.0,
            "low_24h": 2900.0,
            "price_change_24h": 100.0,
            "price_change_percentage_24h": 3.3,
            "circulating_supply": 120000000.0,
            "total_supply": 120000000.0,
            "max_supply": None,
            "ath": 4800.0,
            "ath_date": "2021-11-10T00:00:00.000Z",
            "atl": 0.4,
            "atl_date": "2015-10-20T00:00:00.000Z",
            "last_updated": "2023-01-01T00:00:00.000Z",
        },
    ]


@pytest.fixture
def mock_dataframe(mock_api_data):
    """Retorna um DataFrame processado para testes."""
    df = pd.DataFrame(mock_api_data)
    df["collected_at"] = datetime.now()
    return df
