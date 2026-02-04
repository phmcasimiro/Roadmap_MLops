"""
Módulo de Alerta por E-mail.

Este módulo é responsável por enviar notificações de falha critica na ingestão de dados.
Utiliza SMTP para envio e logs locais como fallback caso as credenciais não estejam configuradas.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Tenta carregar variáveis de ambiente (caso python-dotenv esteja carregado no main)
# Se não, confia no os.getenv nativo do sistema


def send_alert(subject: str, body: str, to_email: str) -> bool:
    """
    Envia um alerta por e-mail ou registra no log se falhar.

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
        _log_fallback(
            f"⚠️ Alerta NÃO enviado (Credenciais ausentes). Assunto: {subject} | Mensagem: {body}"
        )
        return False

    try:
        # Configura a mensagem
        msg = MIMEMultipart()
        msg["From"] = email_user
        msg["To"] = to_email
        msg["Subject"] = f"[ALERTA MLOps] {subject}"

        msg.attach(MIMEText(body, "plain"))

        # Conexão com servidor SMTP (Gmail Exemplo)
        # Nota: Pode precisar liberar "App Password" na conta Google
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, to_email, text)
        server.quit()

        print(f"📧 Alerta enviado com sucesso para {to_email}")
        return True

    except Exception as e:
        _log_fallback(f"❌ Erro ao enviar e-mail: {e}. Assunto: {subject}")
        return False


def _log_fallback(message: str, log_file: str = "data/cron.log"):
    """
    Função auxiliar para registrar alertas no arquivo de log quando o envio falha.

    Args:
        message (str): Mensagem a ser logada.
        log_file (str): Caminho do arquivo de log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"

    print(log_entry)  # Imprime no stdout para o cron capturar também

    try:
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"CRÍTICO: Falha ao escrever no log de fallback: {e}")


if __name__ == "__main__":
    # Teste manual
    send_alert("Teste Manual", "Isso é um teste de alerta.", "phmcasimiro@gmail.com")
