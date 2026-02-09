"""
Testes Unitários para o Sistema de Alerta (email_alert.py).

Este módulo verifica a resiliência do envio de notificações. Como não queremos
enviar e-mails reais durante os testes, utilizamos 'mocks' para simular
o servidor SMTP e verificar se as chamadas de método (login, sendmail) ocorrem.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.email_alert import send_alert


@patch("src.email_alert.smtplib.SMTP")
@patch.dict("os.environ", {"EMAIL_USER": "user@test.com", "EMAIL_PASSWORD": "password"})
def test_send_alert_success(mock_smtp):
    """
    Cenário de Sucesso: Credenciais presentes e servidor SMTP online.
    Verifica se o fluxo de conexão (starttls -> login -> sendmail -> quit) é respeitado.
    """
    # Configura o mock do servidor SMTP
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    result = send_alert("Teste", "Corpo", "dest@test.com")

    # Deve retornar True indicando sucesso no envio
    assert result is True

    # Verificações de chamada de método
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_with("user@test.com", "password")
    mock_server.sendmail.assert_called_once()
    mock_server.quit.assert_called_once()


@patch("src.email_alert.logger")
@patch.dict("os.environ", {}, clear=True)  # Remove todas as credenciais do env
def test_send_alert_missing_credentials(mock_logger):
    """
    Cenário de Erro de Configuração: Variáveis de ambiente ausentes.
    A função deve falhar graciosamente (False) e registrar o erro no warning/info do logger.
    """
    result = send_alert("Teste", "Corpo", "dest@test.com")

    assert result is False
    # Garante que warning foi chamado (credenciais ausentes)
    mock_logger.warning.assert_called()
    # Garante que o fallback (info) foi chamado
    mock_logger.info.assert_called()


@patch("src.email_alert.smtplib.SMTP")
@patch("src.email_alert.logger")
@patch.dict("os.environ", {"EMAIL_USER": "user", "EMAIL_PASSWORD": "pass"})
def test_send_alert_smtp_error(mock_logger, mock_smtp):
    """
    Cenário de Erro de Rede: Servidor SMTP indisponível ou erro de autenticação.
    Simula uma exceção genérica no construtor do SMTP.
    """
    mock_smtp.side_effect = Exception("Connection Error")

    result = send_alert("Teste", "Corpo", "dest@test.com")

    assert result is False
    # Mesmo com erro de rede, devemos logar o erro
    mock_logger.error.assert_called_once()
