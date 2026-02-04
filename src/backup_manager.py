"""
Gerenciador de Backups do Banco de Dados.

Este módulo é responsável por criar cópias de segurança (snapshots) do banco de dados SQLite.
Implementa uma política de retenção para evitar o consumo excessivo de disco.
"""

import shutil
import os
from datetime import datetime
from pathlib import Path
import glob


class BackupManager:
    """Classe para gerenciamento de backups do banco de dados."""

    def __init__(
        self, db_path: str = "data/cripto.db", backup_dir: str = "data/backups"
    ):
        """
        Inicializa o gerenciador de backup.

        Args:
            db_path (str): Caminho para o arquivo de banco de dados original.
            backup_dir (str): Diretório onde os backups serão armazenados.
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def perform_backup(self) -> bool:
        """
        Realiza a cópia de segurança se o banco de dados existir.

        Returns:
            bool: True se o backup foi bem-sucedido, False caso contrário.
        """
        if not self.db_path.exists():
            print(f"❌ Erro: Banco de dados não encontrado em {self.db_path}")
            return False

        # Gera nome do arquivo com timestamp: cripto_backup_YYYYMMDD_HHMM.db
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        backup_filename = f"cripto_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename

        try:
            # Copia o arquivo
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup criado com sucesso: {backup_path}")

            # Aplica política de retenção (limpeza)
            self._rotate_backups()
            return True

        except Exception as e:
            print(f"❌ Falha ao criar backup: {e}")
            return False

    def _rotate_backups(self, max_backups: int = 4):
        """
        Mantém apenas os N backups mais recentes e remove os antigos.

        Args:
            max_backups (int): Número máximo de arquivos de backup a manter.
        """
        # Lista todos os arquivos .db no diretório de backup
        files = list(self.backup_dir.glob("cripto_backup_*.db"))

        # Ordena por data de modificação (mais recente por último)
        files.sort(key=os.path.getmtime)

        # Se houver mais arquivos que o limite, remove os mais antigos
        if len(files) > max_backups:
            files_to_delete = files[:-max_backups]
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"🗑️ Backup antigo removido: {file_path.name}")
                except Exception as e:
                    print(f"⚠️ Erro ao remover backup antigo {file_path.name}: {e}")


if __name__ == "__main__":
    # Teste manual do script
    backup = BackupManager()
    backup.perform_backup()
