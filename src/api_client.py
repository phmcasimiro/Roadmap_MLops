"""
API Client para coleta de dados de criptomoedas.

Este módulo implementa a comunicação com a API CoinGecko
para obter dados de preços de criptomoedas em tempo real.
"""

import requests
from typing import Dict, List, Optional
import time


class CoinGeckoClient:
    """Cliente para interação com a API CoinGecko."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, timeout: int = 10):
        """
        Inicializa o cliente da API.
        
        Args:
            timeout (int): Tempo máximo de espera por requisição em segundos
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'CryptoDataCollector/1.0'
        })
    
    def get_top_cryptocurrencies(
        self, 
        limit: int = 10, 
        vs_currency: str = 'usd'
    ) -> Optional[List[Dict]]:
        """
        Obtém as principais criptomoedas por capitalização de mercado.
        
        Args:
            limit (int): Número de criptomoedas a retornar
            vs_currency (str): Moeda de referência para preços
        
        Returns:
            List[Dict]: Lista de dicionários com dados das criptomoedas
            None: Em caso de erro
        
        Example:
            >>> client = CoinGeckoClient()
            >>> dados = client.get_top_cryptocurrencies(limit=5)
            >>> print(dados[0]['symbol'])
            'btc'
        """
        endpoint = f"{self.BASE_URL}/coins/markets"
        
        params = {
            'vs_currency': vs_currency,
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        
        try:
            print(f"🔄 Buscando top {limit} criptomoedas...")
            response = self.session.get(
                endpoint, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ {len(data)} criptomoedas obtidas com sucesso!")
            return data
        
        except requests.exceptions.Timeout:
            print(f"❌ Erro: Timeout após {self.timeout} segundos")
            return None
        
        except requests.exceptions.HTTPError as e:
            print(f"❌ Erro HTTP: {e}")
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return None
        
        except ValueError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            return None
    
    def get_cryptocurrency_by_id(
        self, 
        coin_id: str, 
        vs_currency: str = 'usd'
    ) -> Optional[Dict]:
        """
        Obtém dados detalhados de uma criptomoeda específica.
        
        Args:
            coin_id (str): ID da criptomoeda (ex: 'bitcoin', 'ethereum')
            vs_currency (str): Moeda de referência
        
        Returns:
            Dict: Dados da criptomoeda
            None: Em caso de erro
        """
        endpoint = f"{self.BASE_URL}/coins/{coin_id}"
        
        params = {
            'localization': False,
            'tickers': False,
            'market_data': True,
            'community_data': False,
            'developer_data': False
        }
        
        try:
            print(f"🔄 Buscando dados de {coin_id}...")
            response = self.session.get(
                endpoint, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Dados de {coin_id} obtidos!")
            return data
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar {coin_id}: {e}")
            return None
    
    def close(self):
        """Fecha a sessão HTTP."""
        self.session.close()
    
    def __enter__(self):
        """Suporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha sessão ao sair do context manager."""
        self.close()


def main():
    """Função de teste do módulo."""
    with CoinGeckoClient() as client:
        # Teste: buscar top 5 criptomoedas
        dados = client.get_top_cryptocurrencies(limit=5)
        
        if dados:
            print("\n📊 Top 5 Criptomoedas:")
            print("-" * 60)
            for cripto in dados:
                print(f"{cripto['symbol'].upper():6} | "
                      f"${cripto['current_price']:>12,.2f} | "
                      f"Cap: ${cripto['market_cap']:>15,.0f}")


if __name__ == "__main__":
    main()
