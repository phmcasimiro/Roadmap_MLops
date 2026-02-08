"""
Gerenciador de Versionamento de Dados (DVC).

Este módulo substitui o sistema de backup anterior.
Responsável por criar snapshots (versões) semanais do banco de dados utilizando DVC.
Ele automatiza o fluxo: 'dvc add' -> 'dvc push' para garantir que os dados
estejam seguros e versionados em sincronia com o código.
"""

import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Caminho absoluto do executável do DVC dentro do ambiente virtual (.venv)
# Isso garante que o script funcione mesmo se rodado fora do venv ativado
DVC_CMD = Path(__file__).parent.parent / ".venv" / "bin" / "dvc"


def run_dvc_snapshot():
    """
    Executa o fluxo de versionamento do banco de dados.

    Passos executados:
    1. Verifica se o DVC está instalado/acessível.
    2. Adiciona o estado atual do banco ('dvc add').
    3. Envia os dados para o remote configurado ('dvc push').

    Returns:
        bool: True se o snapshot foi criado e enviado com sucesso, False caso contrário.
    """
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print(f"[INFO] Iniciando Snapshot DVC: {datetime.now()}")

    if not DVC_CMD.exists():
        print(f"[ERRO] Executável DVC não encontrado em: {DVC_CMD}")
        return False

    try:
        # 1. Adicionar nova versão do banco (Track changes)
        print("[PROCESSANDO] Adicionando alterações (dvc add)...")
        subprocess.run([str(DVC_CMD), "add", "data/cripto.db"], check=True)

        # 2. Enviar para armazenamento remoto (Push to cloud/remote storage)
        print("[UPLOAD] Enviando para remote local (dvc push)...")
        subprocess.run([str(DVC_CMD), "push"], check=True)

        print("[SUCESSO] Snapshot concluído com sucesso!")
        return True

    except subprocess.CalledProcessError as e:
        # Captura erros retornados pelo comando DVC (exit code != 0)
        print(f"[ERRO] Erro ao executar comando DVC: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    run_dvc_snapshot()
