#!/usr/bin/env python3
"""
Script principal para coleta de dados de criptomoedas.

Este script integra todos os módulos para:
1. Coletar dados da API CoinGecko
2. Processar com Pandas
3. Salvar em banco SQLite

Uso:
    python main.py [--limit N] [--verbose]
"""

import argparse
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api_client import CoinGeckoClient
from src.data_processor import CryptoDataProcessor
from src.database import CryptoDatabase


def parse_arguments():
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Coleta dados de criptomoedas da API CoinGecko"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Número de criptomoedas a coletar (padrão: 10)",
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="data/cripto.db",
        help="Caminho para o banco de dados (padrão: data/cripto.db)",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Modo verboso com mais informações"
    )

    return parser.parse_args()


def main():
    """Função principal do script."""
    # Parse argumentos
    args = parse_arguments()

    print("=" * 70)
    print("🚀 SISTEMA DE COLETA DE DADOS DE CRIPTOMOEDAS")
    print("=" * 70)
    print(f"📊 Configuração:")
    print(f"   - Limite: {args.limit} criptomoedas")
    print(f"   - Banco: {args.db_path}")
    print(f"   - Modo verboso: {'Sim' if args.verbose else 'Não'}")
    print("=" * 70)

    try:
        # Etapa 1: Coletar dados da API
        print("\n📡 ETAPA 1: Coletando dados da API CoinGecko...")
        print("-" * 70)

        with CoinGeckoClient() as client:
            raw_data = client.get_top_cryptocurrencies(limit=args.limit)

        if not raw_data:
            print("❌ Falha ao coletar dados da API")
            return 1

        if args.verbose:
            print(f"   Exemplo de dado bruto: {raw_data[0]['symbol']}")

        # Etapa 2: Processar dados com Pandas
        print("\n🔄 ETAPA 2: Processando dados com Pandas...")
        print("-" * 70)

        processor = CryptoDataProcessor()
        df = processor.process_market_data(raw_data)

        if args.verbose:
            print(f"\n   Colunas do DataFrame:")
            for col in df.columns:
                print(f"      - {col}")

            print(f"\n   Primeiras 3 linhas:")
            print(df[["symbol", "name", "current_price", "market_cap"]].head(3))

        # Etapa 3: Salvar no banco SQLite
        print("\n💾 ETAPA 3: Salvando no banco de dados SQLite...")
        print("-" * 70)

        db = CryptoDatabase(db_path=args.db_path)
        rows_inserted = db.insert_dataframe(df)

        # Estatísticas do banco
        print("\n📊 ESTATÍSTICAS DO BANCO DE DADOS:")
        print("-" * 70)

        stats = db.get_statistics()
        print(f"   Total de registros: {stats['total_records']['count']}")
        print(f"   Moedas únicas: {stats['unique_coins']['count']}")
        print(f"   Primeira coleta: {stats['date_range']['first_collection']}")
        print(f"   Última coleta: {stats['date_range']['last_collection']}")

        # Top 5 por market cap
        print("\n🏆 TOP 5 CRIPTOMOEDAS (Market Cap):")
        print("-" * 70)

        top5 = db.get_top_by_market_cap(limit=5)
        for idx, row in top5.iterrows():
            print(
                f"   {row['market_cap_rank']}. {row['symbol']:6} | "
                f"${row['current_price']:>12,.2f} | "
                f"Cap: ${row['market_cap']:>15,.0f}"
            )

        print("\n" + "=" * 70)
        print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário")
        return 130

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
