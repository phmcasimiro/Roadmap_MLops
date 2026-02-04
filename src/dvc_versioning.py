"""
Gerenciador de Versionamento de Dados (DVC).

Este módulo substitui o sistema de backup anterior.
Responsável por criar snapshots semanais do banco de dados utilizando DVC.
Executa: dvc add -> dvc push.
"""

import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Caminho do executável do DVC no venv
DVC_CMD = Path(__file__).parent.parent / ".venv" / "bin" / "dvc"


def run_dvc_snapshot():
    """
    Executa o fluxo de versionamento do banco de dados.
    1. dvc add data/cripto.db
    2. dvc push
    """
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print(f"🔄 Iniciando Snapshot DVC: {datetime.now()}")

    if not DVC_CMD.exists():
        print(f"❌ Executável DVC não encontrado em: {DVC_CMD}")
        return False

    try:
        # 1. Adicionar nova versão do banco
        print("📦 Adicionando alterações (dvc add)...")
        subprocess.run([str(DVC_CMD), "add", "data/cripto.db"], check=True)

        # 2. Enviar para armazenamento remoto (dvc push)
        print("☁️  Enviando para remote local (dvc push)...")
        subprocess.run([str(DVC_CMD), "push"], check=True)

        print("✅ Snapshot concluído com sucesso!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando DVC: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    run_dvc_snapshot()
