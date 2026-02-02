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
    print("\n📡 ETAPA 1: Coletando dados em TEMPO REAL...")
    print("-" * 70)

    limit = args.limit
    if args.all:
        print(
            "⚠️  Modo --all ativado. Limitando a 250 moedas (máximo por página) para demo rápida."
        )
        # Em tempo real, a paginação seria necessária para pegar TODOS.
        # Para simplificar, vamos pegar o max de uma página.
        limit = 250

    raw_data = client.get_top_cryptocurrencies(limit=limit)

    if not raw_data:
        print("❌ Falha ao coletar dados da API")
        return False

    # Etapa 2: Processar
    print("\n🔄 ETAPA 2: Processando dados...")
    processor = CryptoDataProcessor()
    df = processor.process_market_data(raw_data)

    # Etapa 3: Salvar
    print("\n💾 ETAPA 3: Salvando no banco...")
    rows = db.insert_dataframe(df)
    print(f"✅ {rows} registros salvos.")
    return True


def collect_historical_data(args, client, db):
    """Executa fluxo de coleta histórica."""
    print(f"\n🕰️  ETAPA 1: Iniciando coleta HISTÓRICA ({args.days} dias)...")
    print("-" * 70)

    # 1. Obter lista de moedas para iterar
    limit = args.limit
    if args.all:
        print(
            "⚠️  ALERTA: Coletando histórico para 50 moedas (demo) para evitar bloqueio."
        )
        print(
            "    Para pegar realmente TUDO (>10k), seria necessário implementar paginação na lista de moedas."
        )
        limit = (
            50  # Limitando forçadamente para não travar o teste do usuário por horas
        )

    print(f"📋 Obtendo lista das top {limit} moedas para referência...")
    top_coins = client.get_top_cryptocurrencies(limit=limit)

    if not top_coins:
        print("❌ Falha ao obter lista de moedas.")
        return False

    print(f"✅ Lista obtida. Iniciando coleta item a item ({len(top_coins)} moedas)...")

    # Datas
    end_ts = int(time.time())
    start_ts = int((datetime.now() - timedelta(days=args.days)).timestamp())

    processor = CryptoDataProcessor()
    total_saved = 0

    for i, coin in enumerate(top_coins):
        coin_id = coin["id"]
        symbol = coin["symbol"]
        name = coin["name"]

        print(
            f"[{i+1}/{len(top_coins)}] Buscando histórico de {name} ({symbol})...",
            end="",
            flush=True,
        )

        hist_data = client.get_coin_market_chart_range(
            coin_id=coin_id, from_timestamp=start_ts, to_timestamp=end_ts
        )

        if hist_data:
            df = processor.process_historical_data(coin_id, hist_data)

            if not df.empty:
                # Preencher campos obrigatórios que não vêm no histórico
                df["symbol"] = symbol
                df["name"] = name
                # Preencher outros campos com None/NaN para evitar erro no insert se colunas existirem no DB
                # O to_sql ignora colunas do DF que não batem com o DB se o schema for flexível,
                # mas aqui a tabela tem colunas fixas. O SQLite aceita NULL se não for NOT NULL.
                # symbol/name são NOT NULL, por isso preenchemos.

                saved = db.insert_dataframe(df)
                total_saved += saved
                print(f" ✅ Salvo ({saved} regs)")
            else:
                print(f" ⚠️  Vazio")
        else:
            print(f" ❌ Falha")

        # Pequeno delay extra entre loops para ser gentil com a API
        time.sleep(0.5)

    print("-" * 70)
    print(f"✅ Coleta histórica finalizada. Total de registros: {total_saved}")
    return True


def main():
    """Função principal do script."""
    args = parse_arguments()

    print("=" * 70)
    print("🚀 SISTEMA DE COLETA DE DADOS DE CRIPTOMOEDAS")
    print("=" * 70)
    print(f"📊 Configuração:")
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
            print("\n📊 ESTATÍSTICAS DO BANCO DE DADOS:")
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
            print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
            print("=" * 70)
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário")
        return 130

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
