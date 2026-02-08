#!/usr/bin/env python3
"""
Script principal para coleta de dados de criptomoedas.

Este script integra todos os módulos para:
1. Coletar dados da API CoinGecko (Tempo real ou Histórico)
2. Processar com Pandas
3. Salvar em banco SQLite

Uso:
    python main.py [--limit N] [--verbose] [--historical] [--days D] [--all]
"""

import argparse  # Para parsear argumentos da linha de comando
import sys  # Para adicionar src ao path
import time  # Para medir tempo de coleta
from datetime import datetime, timedelta  # Para calcular datas
from pathlib import Path  # Para lidar com caminhos de arquivos

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api_client import CoinGeckoClient  # Cliente para coletar dados da API
from src.data_processor import CryptoDataProcessor  # Processador de dados
from src.database import CryptoDatabase  # Banco de dados
from src.email_alert import send_alert  # Alertas
import pandera as pa  # Validação


def parse_arguments():
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Coleta dados de criptomoedas da API CoinGecko"
    )

    parser.add_argument(
        # Quantidade de criptomoedas a coletar
        "--limit",
        type=int,
        default=30,
        help="Número de criptomoedas a coletar (padrão: 30 se não usar --all)",
    )

    parser.add_argument(
        # Caminho para o banco de dados
        "--db-path",
        type=str,
        default="data/cripto.db",
        help="Caminho para o banco de dados (padrão: data/cripto.db)",
    )

    parser.add_argument(
        # Coleta dados históricos em vez de tempo real
        "--historical",
        action="store_true",
        help="Coletar dados históricos em vez de tempo real",
    )

    parser.add_argument(
        # Quantidade de dias de histórico a coletar
        "--days",
        type=int,
        default=365,
        help="Dias de histórico a coletar (padrão: 365)",
    )

    parser.add_argument(
        # Coleta dados de todas as criptomoedas, caso contrário, coleta apenas as 30 mais valorizadas
        "--all",
        action="store_true",
        help="Coletar dados de TODAS as criptomoedas (ALERTA: Isso pode levar horas)",
    )

    parser.add_argument(
        # Modo verboso com mais informações
        "--verbose",
        action="store_true",
        help="Modo verboso com mais informações",
    )

    return parser.parse_args()


def collect_realtime_data(args, client, db):
    """Executa fluxo de coleta em tempo real."""
    print("\n[ETAPA 1] Coletando dados em TEMPO REAL...")
    print("-" * 70)

    limit = args.limit
    if args.all:
        print(
            "[AVISO] Modo --all ativado. Limitando a 250 moedas (máximo por página) para demo rápida."
        )
        # Em tempo real, a paginação seria necessária para pegar TODOS.
        # Para simplificar, vamos pegar o max de uma página.
        limit = 250

    raw_data = client.get_top_cryptocurrencies(limit=limit)

    if not raw_data:
        print("[ERRO] Falha ao coletar dados da API")
        return False

    # Processamento
    try:
        processor = CryptoDataProcessor()
        df = processor.process_market_data(raw_data)

        # Armazenamento
        total_saved = db.insert_dataframe(df)

        print("-" * 70)
        print(
            f"[SUCESSO] Coleta em tempo real finalizada. Registros salvos: {total_saved}"
        )

        # Validação de Ingestão (Alerting)
        if total_saved == 0:
            print("[AVISO] Nenhum registro novo foi salvo.")
            send_alert(
                "Falha na Ingestão (0 Registros)",
                "O pipeline rodou mas nenhum dado foi salvo no banco. Verifique logs.",
                "phmcasimiro@gmail.com",
            )

        return True

    except Exception as e:
        print(f"[ERRO] Erro no processamento: {e}")
        raise e


def main():
    """Função principal do script."""
    args = parse_arguments()

    print("=" * 70)
    print("SISTEMA DE COLETA DE DADOS DE CRIPTOMOEDAS")
    print("=" * 70)
    print(f"Configuracao:")
    print(f"   - Modo: {'HISTÓRICO' if args.historical else 'TEMPO REAL'}")
    print(
        f"   - Limite moedas: {args.limit if not args.all else 'TODAS (Top 250 demo)'}"
    )
    print(f"   - Banco: {args.db_path}")
    if args.historical:
        print(f"   - Dias: {args.days}")
    print("=" * 70)

    try:
        db = CryptoDatabase(db_path=args.db_path)

        with CoinGeckoClient() as client:
            if args.historical:
                success = collect_historical_data(args, client, db)
            else:
                success = collect_realtime_data(args, client, db)

        if success:
            # Estatísticas finais
            print("\nESTATISTICAS DO BANCO DE DADOS:")
            print("-" * 70)
            stats = db.get_statistics()
            try:
                print(f"   Total de registros: {stats['total_records']['count']}")
                print(f"   Moedas únicas: {stats['unique_coins']['count']}")
                print(f"   Primeira coleta: {stats['date_range']['first_collection']}")
                print(f"   Última coleta: {stats['date_range']['last_collection']}")
            except KeyError:
                print("   Dados insuficientes para estatísticas.")

            print("\n" + "=" * 70)
            print("[SUCESSO] PROCESSO CONCLUIDO!")
            print("=" * 70)
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        print("\n\n[AVISO] Processo interrompido pelo usuário")
        return 130

    except pa.errors.SchemaErrors as e:
        error_msg = f"Violação de Contrato de Dados (Pandera):\n{e.failure_cases}"
        print(f"\n[ERRO DE VALIDACAO] {error_msg}")
        send_alert("Falha de Validação (Schema)", error_msg, "phmcasimiro@gmail.com")
        return 1

    except Exception as e:
        print(f"\n[ERRO CRITICO] {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        send_alert("Erro Crítico no Pipeline", str(e), "phmcasimiro@gmail.com")
        return 1


if __name__ == "__main__":
    sys.exit(main())
