"""Pacote para coleta e processamento de dados de criptomoedas."""

__version__ = "1.0.0"
__author__ = "Professor de Programação e ML"

from .api_client import CoinGeckoClient
from .data_processor import CryptoDataProcessor
from .database import CryptoDatabase

__all__ = ["CoinGeckoClient", "CryptoDataProcessor", "CryptoDatabase"]
