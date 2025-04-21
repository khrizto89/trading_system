import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import psutil
import torch
import pandas as pd
import threading
import time
import os

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Trading System Dashboard"

# Global variables for shared data
system_status = {"cpu": 0, "memory": 0, "gpu": 0, "gpu_memory": 0}
trading_data = {"open_positions": [], "signals": [], "pnl": []}
lock = threading.Lock()

def load_backtesting_data():
    """
    Carga los datos de resultados del backtesting desde un archivo CSV.
    """
    file_path = os.path.join("reports", "backtesting_results.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=["date", "equity"])

# Layout of the dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Trading System Dashboard", className="text-center"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.H4("System Status"),
            dcc.Graph(id="system-status-graph"),
            dcc.Interval(id="system-status-interval", interval=2000, n_intervals=0)
        ], width=6),
        dbc.Col([
            html.H4("Open Positions"),
            dcc.Graph(id="open-positions-graph"),
            dcc.Interval(id="open-positions-interval", interval=2000, n_intervals=0)
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            html.H4("PnL Performance"),
            dcc.Graph(id="pnl-graph"),
            dcc.Interval(id="pnl-interval", interval=5000, n_intervals=0)
        ], width=6),
        dbc.Col([
            html.H4("Trading Signals"),
            dcc.Graph(id="signals-graph"),
            dcc.Interval(id="signals-interval", interval=2000, n_intervals=0)
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            html.H4("Control Panel"),
            dbc.Button("Start Trader", id="start-trader-btn", color="success", className="me-2"),
            dbc.Button("Stop Trader", id="stop-trader-btn", color="danger"),
            html.Div(id="trader-status", className="mt-2")
        ], width=6),
        dbc.Col([
            html.H4("Logs"),
            dcc.Textarea(id="logs", style={"width": "100%", "height": "200px"}, readOnly=True)
        ], width=6)
    ])
], fluid=True)

# Callbacks for system status
@app.callback(
    Output("system-status-graph", "figure"),
    Input("system-status-interval", "n_intervals")
)
def update_system_status(n):
    with lock:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"
        gpu_memory = torch.cuda.memory_allocated() / 1e6 if torch.cuda.is_available() else 0
        system_status.update({"cpu": cpu, "memory": memory, "gpu": gpu, "gpu_memory": gpu_memory})

    figure = go.Figure(data=[
        go.Bar(name="CPU Usage (%)", x=["CPU"], y=[system_status["cpu"]]),
        go.Bar(name="Memory Usage (%)", x=["Memory"], y=[system_status["memory"]]),
        go.Bar(name="GPU Memory (MB)", x=["GPU"], y=[system_status["gpu_memory"]])
    ])
    figure.update_layout(title="System Status", barmode="group")
    return figure

# Callbacks for open positions
@app.callback(
    Output("open-positions-graph", "figure"),
    Input("open-positions-interval", "n_intervals")
)
def update_open_positions(n):
    with lock:
        positions = trading_data["open_positions"]

    figure = go.Figure(data=[
        go.Table(
            header=dict(values=["Symbol", "Quantity", "Entry Price", "Current Price", "PnL"]),
            cells=dict(values=list(zip(*positions)) if positions else [[]])
        )
    ])
    figure.update_layout(title="Open Positions")
    return figure

# Callbacks for PnL performance
@app.callback(
    Output("pnl-graph", "figure"),
    Input("pnl-interval", "n_intervals")
)
def update_pnl(n):
    with lock:
        pnl_data = trading_data["pnl"]

    figure = go.Figure(data=[
        go.Scatter(x=[p["time"] for p in pnl_data], y=[p["value"] for p in pnl_data], mode="lines+markers")
    ])
    figure.update_layout(title="PnL Performance", xaxis_title="Time", yaxis_title="PnL")
    return figure

# Callbacks for trading signals
@app.callback(
    Output("signals-graph", "figure"),
    Input("signals-interval", "n_intervals")
)
def update_signals(n):
    with lock:
        signals = trading_data["signals"]

    figure = go.Figure(data=[
        go.Scatter(x=[s["time"] for s in signals], y=[s["value"] for s in signals], mode="lines+markers")
    ])
    figure.update_layout(title="Trading Signals", xaxis_title="Time", yaxis_title="Signal Strength")
    return figure

# Callbacks for trader control
@app.callback(
    Output("trader-status", "children"),
    [Input("start-trader-btn", "n_clicks"), Input("stop-trader-btn", "n_clicks")]
)
def control_trader(start_clicks, stop_clicks):
    if start_clicks and (not stop_clicks or start_clicks > stop_clicks):
        return "Trader started."
    elif stop_clicks and (not start_clicks or stop_clicks > start_clicks):
        return "Trader stopped."
    return "Trader is idle."

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
