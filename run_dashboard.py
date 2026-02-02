#!/usr/bin/env python3
"""
Script para iniciar o Dashboard de Criptomoedas.
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.dashboard import CryptoDashboard

if __name__ == "__main__":
    print("🚀 Iniciando Dashboard...")
    print("📊 Acesse em: http://127.0.0.1:8051")

    dashboard = CryptoDashboard()
    # Debug=True permite hot-reload mas não é ideal para produção.
    # Para teste user, debug=False é mais limpo no terminal.
    dashboard.run(debug=False, port=8051)
