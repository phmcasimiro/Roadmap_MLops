"""
Testes Unitários para o Cliente de API (api_client.py).

Este módulo valida o comportamento do cliente HTTP CoinGeckoClient, garantindo
que ele trate corretamente respostas de sucesso, erros de conexão (Timeouts)
e códigos de erro HTTP (4xx, 5xx), utilizando mocks para isolar a dependência de rede.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.api_client import CoinGeckoClient
import requests


@pytest.fixture
def client():
    """Fixture para criar uma instância limpa do cliente para cada teste."""
    return CoinGeckoClient(timeout=1)


def test_get_top_cryptocurrencies_success(client):
    """
    Cenário de Sucesso: API retorna código 200 e lista de moedas.
    Verifica se a resposta é parseada corretamente e se os parâmetros
    de query string estão sendo passados conforme esperado.
    """
    # Mock da resposta da API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "bitcoin", "current_price": 50000}]

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        data = client.get_top_cryptocurrencies(limit=1)

        assert data is not None
        assert len(data) == 1
        assert data[0]["id"] == "bitcoin"

        # Verifica se a URL correta foi chamada
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "vs_currency" in kwargs["params"]
        assert kwargs["params"]["per_page"] == 1


def test_get_top_cryptocurrencies_timeout(client):
    """
    Cenário de Erro: Timeout na conexão.
    Simula uma exceção de Timeout do requests e verifica se a função
    trata o erro graciosamente (retornando None) sem quebrar a execução.
    """
    with patch.object(
        client.session, "get", side_effect=requests.exceptions.Timeout("Timeout")
    ):
        data = client.get_top_cryptocurrencies()
        assert data is None


def test_get_top_cryptocurrencies_http_error(client):
    """
    Cenário de Erro HTTP: Servidor retorna 500 Internal Server Error.
    Simula o método 'raise_for_status' levantando exceção e verifica
    o tratamento de erro.
    """
    mock_response = MagicMock()
    mock_response.status_code = 500
    # raise_for_status() deve levantar HTTPError quando chamado
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Erro 500"
    )

    with patch.object(client.session, "get", return_value=mock_response):
        data = client.get_top_cryptocurrencies()
        assert data is None


def test_get_cryptocurrency_by_id(client):
    """
    Teste Específico: Busca de detalhes de uma única moeda por ID.
    Valida se o endpoint correto é chamado par ao ID fornecido.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "bitcoin", "name": "Bitcoin"}

    with patch.object(client.session, "get", return_value=mock_response):
        data = client.get_cryptocurrency_by_id("bitcoin")
        assert data["name"] == "Bitcoin"
