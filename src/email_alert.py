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

# As credenciais são carregadas das variáveis de ambiente para segurança.
# Nunca commite senhas diretamente no código!


def send_alert(subject: str, body: str, to_email: str) -> bool:
    """
    Tenta enviar um alerta por e-mail e faz fallback para log em caso de erro.

    Args:
        subject (str): Assunto do e-mail. Será prefixado com [ALERTA MLOps].
        body (str): Corpo da mensagem (texto plano).
        to_email (str): Endereço de e-mail do destinatário.

    Returns:
        bool: True se enviado com sucesso via SMTP, False se falhou (mesmo que logado).
    """
    # Obtém credenciais das variáveis de ambiente
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASSWORD")

    # Validação simples de credenciais
    if not email_user or not email_pass:
        _log_fallback(
            f"[ALERTA LOGAL] E-mail NÃO enviado (Credenciais ausentes). Assunto: {subject} | Mensagem: {body}"
        )
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

        print(f"[SUCESSO] Alerta enviado com sucesso para {to_email}")
        return True

    except Exception as e:
        # Em caso de qualquer erro (rede, auth, etc), registra no disco
        _log_fallback(f"[ERRO] Falha ao enviar e-mail: {e}. Assunto: {subject}")
        return False


def _log_fallback(message: str, log_file: str = "data/cron.log"):
    """
    Função auxiliar (privada) para registrar alertas em arquivo local.

    Isso garante que se o sistema de e-mail falhar, ainda teremos um rastro
    do problema nos logs do servidor/container.

    Args:
        message (str): Mensagem a ser logada.
        log_file (str): Caminho do arquivo de log. Padrão: 'data/cron.log'.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"

    print(log_entry)  # Imprime no stdout para o cron capturar também

    try:
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        # Se até o log falhar (disco cheio/permissão), imprimimos na tela como último recurso
        print(f"[CRITICO] Falha ao escrever no log de fallback: {e}")


if __name__ == "__main__":
    # Teste manual para verificar se o envio está funcionando
    print("Testando envio de alerta...")
    send_alert(
        "Teste Manual", "Isso é um teste de alerta do sistema.", "phmcasimiro@gmail.com"
    )
