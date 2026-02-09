"""
Testes Unitários para o Módulo de Versionamento DVC (dvc_versioning.py).

Este arquivo testa a lógica de chamada de subprocessos para o DVC, garantindo
que os comandos 'dvc add' e 'dvc push' sejam invocados corretamente,
sem executar as operações reais de versionamento durante os testes.
"""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
from src.dvc_versioning import run_dvc_snapshot


# Mock do Path para evitar erro de 'file not found' no binário do DVC
@patch("src.dvc_versioning.DVC_CMD")
@patch("src.dvc_versioning.subprocess.run")
def test_run_dvc_snapshot_success(mock_run, mock_dvc_cmd):
    """
    Testa o cenário de sucesso onde 'dvc add' e 'dvc push' são executados sem erros.
    """
    # Configura o mock do Path para existir
    mock_dvc_cmd.exists.return_value = True
    # O str(DVC_CMD) deve retornar um caminho string válido
    mock_dvc_cmd.__str__.return_value = "/mock/path/to/dvc"

    # Executa a função
    success = run_dvc_snapshot()

    # Verificações
    assert success is True

    # Verifica se subprocess.run foi chamado 2 vezes (add e push)
    assert mock_run.call_count == 2

    # Verifica argumentos da primeira chamada (add)
    args_add, _ = mock_run.call_args_list[0]
    assert args_add[0] == ["/mock/path/to/dvc", "add", "data/cripto.db"]

    # Verifica argumentos da segunda chamada (push)
    args_push, _ = mock_run.call_args_list[1]
    assert args_push[0] == ["/mock/path/to/dvc", "push"]


@patch("src.dvc_versioning.DVC_CMD")
def test_dvc_binary_not_found(mock_dvc_cmd):
    """
    Testa o cenário onde o binário do DVC não é encontrado.
    """
    mock_dvc_cmd.exists.return_value = False

    success = run_dvc_snapshot()

    assert success is False


@patch("src.dvc_versioning.DVC_CMD")
@patch("src.dvc_versioning.subprocess.run")
def test_dvc_subprocess_error(mock_run, mock_dvc_cmd):
    """
    Testa o cenário de erro na execução do comando (ex: falha de rede ou permissão).
    """
    mock_dvc_cmd.exists.return_value = True
    mock_dvc_cmd.__str__.return_value = "/mock/path/to/dvc"

    # Simula erro no subprocesso (exit code != 0)
    mock_run.side_effect = subprocess.CalledProcessError(1, "dvc")

    success = run_dvc_snapshot()

    assert success is False
