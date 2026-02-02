import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from src.database import CryptoDatabase
from datetime import datetime


class CryptoDashboard:
    """Dashboard V3: Layout com Sidebar e Comparativo."""

    def __init__(self, db_path="data/cripto.db"):
        self.db = CryptoDatabase(db_path)
        self.app = dash.Dash(
            __name__, title="Crypto App V3", suppress_callback_exceptions=True
        )
        # Carregar lista de moedas inicial (Top 50 com histórico)
        self.available_coins = self._get_available_coins()
        self._setup_layout()
        self._setup_callbacks()

    def _get_available_coins(self):
        """Retorna lista de moedas que possuem histórico no banco."""
        # Query para pegar moedas distintas na tabela (assumindo que as que tem histórico estão lá)
        # Ideal seria filtrar aquelas que tem count > 1
        query = """
        SELECT coin_id, name, symbol, count(*) as cnt 
        FROM cryptocurrency_data 
        GROUP BY coin_id 
        HAVING cnt > 1
        ORDER BY cnt DESC, coin_id ASC
        LIMIT 50
        """
        with self.db._get_connection() as conn:
            df = pd.read_sql_query(query, conn)

        if df.empty:
            return []

        return [
            {"label": f"{row['name']} ({row['symbol']})", "value": row["coin_id"]}
            for _, row in df.iterrows()
        ]

    def _setup_layout(self):
        """Define o layout Sidebar + Content."""

        # Estilos
        SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "20rem",
            "padding": "2rem 1rem",
            "backgroundColor": "#2c3e50",
            "color": "#ecf0f1",
            "overflowY": "auto",
        }

        CONTENT_STYLE = {
            "marginLeft": "22rem",
            "marginRight": "2rem",
            "padding": "2rem 1rem",
        }

        sidebar = html.Div(
            [
                html.H2("Crypto V3", className="display-4"),
                html.Hr(),
                html.P("Selecione as moedas para destacar:", className="lead"),
                # Checklist com scroll se tiver muitas opções
                html.Div(
                    [
                        dcc.Checklist(
                            id="coin-selector",
                            options=self.available_coins,
                            value=[
                                c["value"] for c in self.available_coins[:3]
                            ],  # Default first 3 selected
                            style={
                                "label": {"display": "block", "marginBottom": "5px"},
                                "cursor": "pointer",
                            },
                            inputStyle={"marginRight": "10px"},
                        )
                    ],
                    style={"maxHeight": "80vh", "overflowY": "auto"},
                ),
            ],
            style=SIDEBAR_STYLE,
        )

        content = html.Div(
            [
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="📈 Comparativo (Linhas)",
                            children=[
                                html.Div(
                                    [
                                        html.H3(
                                            "Série Temporal Comparativa",
                                            style={"marginTop": "20px"},
                                        ),
                                        dcc.Graph(
                                            id="comparison-chart",
                                            style={"height": "80vh"},
                                        ),
                                    ]
                                )
                            ],
                        ),
                        dcc.Tab(
                            label="🕯️ Candlesticks (Detalhado)",
                            children=[
                                html.Div(
                                    id="candles-container", style={"marginTop": "20px"}
                                )
                            ],
                        ),
                    ]
                )
            ],
            style=CONTENT_STYLE,
        )

        self.app.layout = html.Div([sidebar, content])

    def _setup_callbacks(self):

        @self.app.callback(
            [
                Output("comparison-chart", "figure"),
                Output("candles-container", "children"),
            ],
            [Input("coin-selector", "value")],
        )
        def update_dashboard(selected_coins):
            # Se nada selecionado, tratamos como lista vazia
            selected_coins = selected_coins or []

            # --- TAB 1: Comparison Logic ---
            fig_comp = go.Figure()

            # Precisamos de dados de TODAS as moedas disponíveis para desenhar o "fundo" esmaecido
            # Mas buscar data de todas no loop é lento.
            # Vamos buscar dados apenas das 50 lists.

            # Otimização: Buscar tudo em uma query se possível?
            # `get_coin_history` pega uma por uma.
            # Vamos iterar sobre self.available_coins (Top 50)

            # Para performance, limitaremos o "background" às Top 10 ou Top 20 se não estiverem selecionadas,
            # ou desenhamos todas se o user aguentar. Vamos tentar todas as 50.

            for coin_opt in self.available_coins:
                coin_id = coin_opt["value"]
                is_selected = coin_id in selected_coins

                # Buscar dados (Limitando a 365 dias)
                # Cachear isso seria bom, mas por enquanto direto do DB
                df = self.db.get_coin_history(coin_id, days=365)

                if df.empty:
                    continue

                # Ordenar
                df = df.sort_values("collected_at")

                # Definir Estilo
                if is_selected:
                    opacity = 1.0
                    width = 3
                    # Cor automática do Plotly
                    color = None
                    legend_group = "Selecionadas"
                else:
                    opacity = 0.1
                    width = 1
                    color = "gray"
                    legend_group = "Outras"

                fig_comp.add_trace(
                    go.Scatter(
                        x=df["collected_at"],
                        y=df["current_price"],
                        mode="lines",
                        name=coin_opt["label"],
                        line=dict(width=width, color=color),
                        opacity=opacity,
                        legendgroup=legend_group,
                    )
                )

            fig_comp.update_layout(
                title="Preços Normalizados (Escala Log recomendada para comparativos drasticos)",
                yaxis_type="log",  # Log scale fica melhor para comparar BTC com Altcoins baratas
                template="plotly_white",
                height=800,
                legend=dict(title="Moedas"),
            )

            # --- TAB 2: Candle Logic ---
            # Apenas moedas SELECIONADAS
            candle_graphs = []

            if not selected_coins:
                candle_graphs.append(
                    html.H4("Nenhuma moeda selecionada para visualização de velas.")
                )
            else:
                for coin_id in selected_coins:
                    df = self.db.get_coin_history(coin_id, days=365)
                    if df.empty:
                        continue

                    # Resampling logic (igual à V2)
                    df.set_index("collected_at", inplace=True)
                    time_span = df.index.max() - df.index.min()
                    freq = "h" if time_span.days < 30 else "D"

                    df_res = df.resample(freq).agg(
                        {
                            "current_price": ["first", "max", "min", "last"],
                            "total_volume": "sum",
                        }
                    )
                    df_res.columns = ["open", "high", "low", "close", "volume"]
                    df_res.dropna(inplace=True)

                    # Graph Object Candle
                    fig_candle = go.Figure(
                        data=[
                            go.Candlestick(
                                x=df_res.index,
                                open=df_res["open"],
                                high=df_res["high"],
                                low=df_res["low"],
                                close=df_res["close"],
                            )
                        ]
                    )

                    fig_candle.update_layout(
                        title=f"{coin_id.upper()} ({freq})",
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis_rangeslider_visible=False,
                    )

                    candle_graphs.append(
                        html.Div(
                            [dcc.Graph(figure=fig_candle)],
                            style={
                                "marginBottom": "40px",
                                "border": "1px solid #ddd",
                                "padding": "10px",
                            },
                        )
                    )

            return fig_comp, candle_graphs

    def run(self, debug=True, port=8050):
        self.app.run(debug=debug, port=port)
