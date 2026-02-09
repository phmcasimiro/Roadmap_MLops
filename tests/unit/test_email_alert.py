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


@patch("src.email_alert._log_fallback")
@patch.dict("os.environ", {}, clear=True)  # Remove todas as credenciais do env
def test_send_alert_missing_credentials(mock_log):
    """
    Cenário de Erro de Configuração: Variáveis de ambiente ausentes.
    A função deve falhar graciosamente (False) e registrar o erro no log local.
    """
    result = send_alert("Teste", "Corpo", "dest@test.com")

    assert result is False
    mock_log.assert_called_once()  # Garante que o fallback foi acionado


@patch("src.email_alert.smtplib.SMTP")
@patch("src.email_alert._log_fallback")
@patch.dict("os.environ", {"EMAIL_USER": "user", "EMAIL_PASSWORD": "pass"})
def test_send_alert_smtp_error(mock_log, mock_smtp):
    """
    Cenário de Erro de Rede: Servidor SMTP indisponível ou erro de autenticação.
    Simula uma exceção genérica no construtor do SMTP.
    """
    mock_smtp.side_effect = Exception("Connection Error")

    result = send_alert("Teste", "Corpo", "dest@test.com")

    assert result is False
    # Mesmo com erro de rede, devemos logar a tentativa falha
    mock_log.assert_called_once()
