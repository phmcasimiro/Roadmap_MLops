"""
Módulo de Alerta por E-mail.

Este módulo é responsável por enviar notificações de falha crítica na ingestão de dados.
Ele implementa um sistema de resiliência: tenta enviar via SMTP (Gmail, etc),
mas se falhar (ex: sem internet ou credenciais inválidas), faz fallback
para um log local em arquivo, garantindo que o erro não passe despercebido.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from src.logger import get_logger

logger = get_logger(__name__)


def send_alert(subject: str, body: str, to_email: str) -> bool:
    """
    Envia um alerta por e-mail utilizando servidor SMTP (Gmail).

    Em caso de falha, registra o erro no logger.

    Args:
        subject (str): Assunto do e-mail.
        body (str): Corpo da mensagem.
        to_email (str): E-mail do destinatário.

    Returns:
        bool: True se enviado com sucesso, False caso contrário.
    """
    # Obtém credenciais das variáveis de ambiente
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASSWORD")

    # Validação simples de credenciais
    if not email_user or not email_pass:
        logger.warning(
            "Credenciais de e-mail não configuradas (EMAIL_USER/EMAIL_PASSWORD). Alerta ignorado."
        )
        # Logamos o alerta no arquivo local como fallback
        logger.info(f"[ALERTA LOCAL] {subject}: {body}")
        return False

    try:
        # Configura a mensagem MIME (Multipurpose Internet Mail Extensions)
        msg = MIMEMultipart()
        msg["From"] = email_user
        msg["To"] = to_email
        msg["Subject"] = f"[ALERTA MLOps] {subject}"

        msg.attach(MIMEText(body, "plain"))

        # Conexão com servidor SMTP (Configuração para Gmail)
        # Porta 587 é padrão para TLS (Transport Layer Security)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Inicia criptografia
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, to_email, text)
        server.quit()

        logger.info(f"Alerta enviado com sucesso para {to_email}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}. Assunto: {subject}")
        return False


if __name__ == "__main__":
    # Teste manual para verificar se o envio está funcionando
    print("Testando envio de alerta...")
    send_alert(
        "Teste Manual", "Isso é um teste de alerta do sistema.", "phmcasimiro@gmail.com"
    )
