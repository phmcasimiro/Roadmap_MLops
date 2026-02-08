"""
API Client para coleta de dados de criptomoedas.

Este módulo implementa a comunicação com a API CoinGecko para obter dados de
preços de criptomoedas em tempo real e históricos. Ele gerencia sessões HTTP,
timeouts, retries básicos e respeita os limites de requisição da API (Rate Limiting).
"""

import requests
from typing import Dict, List, Optional
import time


class CoinGeckoClient:
    """
    Cliente para interação com a API pública da CoinGecko.

    Gerencia a comunicação HTTP, incluindo configuração de headers,
    timeouts e tratamento básico de erros de conexão.
    """

    # URL base da versão 3 da API CoinGecko
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, timeout: int = 10):
        """
        Inicializa o cliente da API.

        Nesta etapa, criamos uma sessão HTTP persistente. Isso é uma boa prática
        pois reaproveita a conexão TCP (Keep-Alive), tornando múltiplas requisições
        mais rápidas do que criar uma nova conexão para cada chamada.

        Args:
            timeout (int): Tempo máximo (em segundos) que o cliente deve esperar
                           por uma resposta do servidor antes de desistir.
        """
        self.timeout = timeout

        # Cria uma sessão para persistir conexões e configurações entre requisições
        self.session = requests.Session()

        # Define headers padrão para simular um cliente legítimo e evitar bloqueios simples
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": "CryptoDataCollector/1.0"}
        )

    def get_top_cryptocurrencies(self, limit: int = 10, vs_currency: str = "usd") -> Optional[List[Dict]]:
        """
        Obtém uma lista das principais criptomoedas ordenadas por capitalização de mercado.

        Esta função consulta o endpoint '/coins/markets' da API.

        Args:
            limit (int): Número máximo de criptomoedas para retornar (ex: Top 10, Top 50).
            vs_currency (str): A moeda fiduciária de referência para os preços (ex: 'usd', 'brl').

        Returns:
            Optional[List[Dict]]:
                - Uma lista de dicionários contendo os dados de mercado se a chamada for bem-sucedida.
                - None se ocorrer qualquer erro de conexão ou decodificação.

        Exemplo de Retorno:
            [
                {'id': 'bitcoin', 'symbol': 'btc', 'current_price': 50000.0, ...},
                {'id': 'ethereum', 'symbol': 'eth', 'current_price': 3000.0, ...}
            ]
        """
        endpoint = f"{self.BASE_URL}/coins/markets"

        # Parâmetros da query string para filtrar e ordenar os resultados
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",  # Ordena da maior para a menor capitalização
            "per_page": limit,  # Limita a quantidade de resultados
            "page": 1,  # Pega apenas a primeira página
            "sparkline": False,  # Não traz dados simplificados do gráfico (economiza banda)
            "price_change_percentage": "24h",  # Inclui a variação percentual das últimas 24h
        }

        try:
            print(f"Buscando top {limit} criptomoedas...")

            # Realiza a requisição GET
            response = self.session.get(endpoint, params=params, timeout=self.timeout)

            # Levanta uma exceção (HTTPError) se o status code for 4xx ou 5xx
            response.raise_for_status()

            data = response.json()
            print(f"{len(data)} criptomoedas obtidas com sucesso!")
            return data

        except requests.exceptions.Timeout:
            print(f"Erro: Timeout apos {self.timeout} segundos. O servidor demorou muito para responder.")
            return None

        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP: {e}. Verifique se a URL ou parametros estao corretos.")
            return None

        except requests.exceptions.RequestException as e:
            # Captura qualquer outro erro relacionado a biblioteca requests (ex: erro de DNS, conexão recusada)
            print(f"Erro na requisicao: {e}")
            return None

        except ValueError as e:
            # Captura erros de decodificação JSON (ex: resposta vazia ou malformada)
            print(f"Erro ao decodificar JSON: {e}")
            return None

    def get_cryptocurrency_by_id(self, coin_id: str) -> Optional[Dict]:
        """
        Obtém dados detalhados de uma única criptomoeda específica pelo seu ID.

        Utiliza o endpoint '/coins/{id}'.

        Args:
            coin_id (str): O ID único da moeda na CoinGecko (ex: 'bitcoin', 'ethereum').
                           Nota: O ID pode ser diferente do símbolo (ex: 'binancecoin' vs 'BNB').

        Returns:
            Optional[Dict]: Dicionário com os dados detalhados ou None em caso de erro.
        """
        endpoint = f"{self.BASE_URL}/coins/{coin_id}"

        # Configura quais blocos de dados queremos receber para otimizar a resposta
        params = {
            "localization": False,  # Não trazer descrições traduzidas
            "tickers": False,  # Não trazer lista de todas as exchanges (payload muito grande)
            "market_data": True,  # Traz preços, volumes e market cap (essencial)
            "community_data": False,  # Dados sociais (Twitter, Reddit) - Desnecessário
            "developer_data": False,  # Dados de desenvolvimento (Github) - Desnecessário
        }

        try:
            print(f"Buscando dados de {coin_id}...")
            response = self.session.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            print(f"Dados de {coin_id} obtidos!")
            return data

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar detalhes de {coin_id}: {e}")
            return None

    def get_coin_market_chart_range(
        self,
        coin_id: str,
        from_timestamp: int,
        to_timestamp: int,
        vs_currency: str = "usd",
    ) -> Optional[Dict]:
        """
        Obtém o histórico de preços, market cap e volume dentro de um intervalo de datas.

        Args:
            coin_id (str): O ID da moeda.
            from_timestamp (int): Data de início em formato UNIX Timestamp.
            to_timestamp (int): Data de fim em formato UNIX Timestamp.
            vs_currency (str): Moeda de referência (padrão: 'usd').

        Returns:
            Optional[Dict]: Dicionário contendo listas de [timestamp, valor] para 'prices',
                            'market_caps' e 'total_volumes'.
        """
        endpoint = f"{self.BASE_URL}/coins/{coin_id}/market_chart/range"

        params = {
            "vs_currency": vs_currency,
            "from": from_timestamp,
            "to": to_timestamp,
        }

        try:
            # Implementação de Rate Limiting Manual
            # A API gratuita da CoinGecko tem um limite de requisições por minuto.
            # Adicionamos um delay preventivo para não sobrecarregar a API.
            time.sleep(1.5)

            response = self.session.get(endpoint, params=params, timeout=self.timeout)

            # Tratamento Específico para Rate Limit (HTTP 429 - Too Many Requests)
            if response.status_code == 429:
                print(
                    f"Aviso: Rate limit atingido para {coin_id}. Aguardando 60s para tentar novamente..."
                )
                time.sleep(
                    60
                )  # Espera passiva agressiva para garantir a recuperação do crédito de requisições
                # Recursão: Tenta chamar a mesma função novamente após a espera
                return self.get_coin_market_chart_range(
                    coin_id, from_timestamp, to_timestamp, vs_currency
                )

            response.raise_for_status()

            # Validação: Verifica se o JSON retornado tem a estrutura esperada
            data = response.json()
            if not data or "prices" not in data or not data["prices"]:
                # Pode acontecer se o range de datas for inválido ou muito antigo para a moeda
                return None

            return data

        except requests.exceptions.HTTPError as e:
            # Ignora erro 404 (Not Found) silenciosamente, pois significa apenas que
            # a moeda não existia naquela data, o que é um cenário de negócio válido.
            if e.response.status_code != 404:
                print(f"Erro HTTP ao buscar historico de {coin_id}: {e}")
            return None
        except Exception as e:
            print(f"Erro generico ao buscar historico de {coin_id}: {e}")
            return None

    def close(self):
        """
        Fecha a sessão HTTP explicitamente.
        Libera recursos do sistema (descritores de arquivo, sockets).
        """
        self.session.close()

    def __enter__(self):
        """
        Permite usar a classe com a declaração 'with'.
        Ex: with CoinGeckoClient() as client: ...
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Garante que a sessão seja fechada automaticamente ao sair do bloco 'with',
        mesmo se ocorrerem erros.
        """
        self.close()


def main():
    """Funcao principal para teste rapido do modulo."""
    with CoinGeckoClient() as client:
        # Teste: buscar top 5 criptomoedas
        dados = client.get_top_cryptocurrencies(limit=5)

        if dados:
            print("\nTop 5 Criptomoedas:")
            print("-" * 60)
            for cripto in dados:
                print(
                    f"{cripto['symbol'].upper():6} | "
                    f"${cripto['current_price']:>12,.2f} | "
                    f"Cap: ${cripto['market_cap']:>15,.0f}"
                )


if __name__ == "__main__":
    main()
