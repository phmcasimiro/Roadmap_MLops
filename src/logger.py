import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Configura e retorna um logger nomeado com handlers para arquivo e console.

    O arquivo de log é rotacionado automaticamente (5MB x 5 backups).

    Args:
        name (str): Nome do módulo (geralmente __name__).

    Returns:
        logging.Logger: Instância configurada do logger.
    """
    # Cria diretório de logs se não existir
    log_dir = Path(__file__).parent.parent / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "pipeline.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evita duplicação de handlers se get_logger for chamado múltiplas vezes
    if not logger.handlers:
        # Formatter: [DATA] [MODULO] [NIVEL] Mensagem
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Handler 1: Arquivo Rotativo (Persistência)
        # MaxBytes=5MB, BackupCount=5 arquivos
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # Handler 2: Console (Visualização em tempo real)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
