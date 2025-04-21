# Sistema de backtesting

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
import logging

logger = logging.getLogger(__name__)

class Backtesting:
    def __init__(self, results_path="backtesting_results"):
        """
        Inicializa el módulo de backtesting.

        Args:
            results_path (str): Ruta donde se guardarán los resultados.
        """
        self.results_path = results_path
        os.makedirs(self.results_path, exist_ok=True)

    def run_backtest(self, symbol, start_date, end_date, initial_capital, strategy_params, market_data):
        """
        Ejecuta un backtest para un símbolo y período específico.

        Args:
            symbol (str): Símbolo a testear.
            start_date (str): Fecha de inicio.
            end_date (str): Fecha de fin.
            initial_capital (float): Capital inicial.
            strategy_params (dict): Parámetros de la estrategia.
            market_data (pd.DataFrame): Datos de mercado históricos.

        Returns:
            dict: Resultados del backtest.
        """
        logger.info(f"Iniciando backtest para {symbol} desde {start_date} hasta {end_date}")
        
        # Inicializar variables
        balance = initial_capital
        position = None
        trades = []
        equity_curve = []

        # Parámetros de la estrategia
        sl_pct = strategy_params.get('stop_loss_pct', 2)
        tp_pct = strategy_params.get('take_profit_pct', 4)
        fee_percentage = strategy_params.get('fee_pct', 0.1)
        position_size_pct = strategy_params.get('position_size_pct', 10)

        # Filtrar datos de mercado
        market_data = market_data[(market_data['timestamp'] >= start_date) & (market_data['timestamp'] <= end_date)]

        for index, row in market_data.iterrows():
            current_time = row['timestamp']
            current_price = row['price']
            signal = row['signal']  # Señal generada previamente

            # Actualizar equity curve
            equity_curve.append({'timestamp': current_time, 'balance': balance})

            # Lógica de trading
            balance, position, new_trades = self._process_signal(
                signal, current_price, current_time, balance, position, trades, sl_pct, tp_pct, fee_percentage, position_size_pct
            )
            trades.extend(new_trades)

        # Calcular métricas de rendimiento
        performance_metrics = self._calculate_performance_metrics(initial_capital, balance, trades, equity_curve)

        # Generar reporte
        report = self._generate_report(symbol, start_date, end_date, initial_capital, performance_metrics, trades, equity_curve)

        return report

    def _process_signal(self, signal, current_price, current_time, balance, position, trades, sl_pct, tp_pct, fee_percentage, position_size_pct):
        """
        Procesa una señal de trading y actualiza el balance y las posiciones.

        Args:
            signal (dict): Señal de trading.
            current_price (float): Precio actual.
            current_time (datetime): Tiempo actual.
            balance (float): Balance actual.
            position (dict): Posición abierta.
            trades (list): Lista de trades realizados.
            sl_pct (float): Porcentaje de stop loss.
            tp_pct (float): Porcentaje de take profit.
            fee_percentage (float): Porcentaje de comisión.
            position_size_pct (float): Porcentaje del balance para la posición.

        Returns:
            tuple: Balance actualizado, posición actualizada, nuevos trades.
        """
        new_trades = []

        # Si no hay posición abierta y la señal es BUY
        if position is None and signal['action'] == 'BUY':
            position_size = (balance * position_size_pct / 100)
            position_amount = position_size / current_price
            commission = position_size * fee_percentage / 100

            position = {
                'entry_time': current_time,
                'entry_price': current_price,
                'amount': position_amount,
                'direction': 'long',
                'stop_loss': current_price * (1 - sl_pct / 100),
                'take_profit': current_price * (1 + tp_pct / 100)
            }

            balance -= commission

        # Si hay posición abierta
        elif position is not None:
            closed = False

            if position['direction'] == 'long':
                # Verificar stop loss
                if current_price <= position['stop_loss']:
                    pnl = ((current_price / position['entry_price']) - 1) * 100
                    amount_value = position['amount'] * current_price
                    commission = amount_value * fee_percentage / 100

                    new_trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'amount': position['amount'],
                        'direction': 'long',
                        'pnl_pct': pnl,
                        'reason': 'stop_loss'
                    })

                    balance += amount_value - commission
                    position = None
                    closed = True

                # Verificar take profit
                elif current_price >= position['take_profit']:
                    pnl = ((current_price / position['entry_price']) - 1) * 100
                    amount_value = position['amount'] * current_price
                    commission = amount_value * fee_percentage / 100

                    new_trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'amount': position['amount'],
                        'direction': 'long',
                        'pnl_pct': pnl,
                        'reason': 'take_profit'
                    })

                    balance += amount_value - commission
                    position = None
                    closed = True

        return balance, position, new_trades

    def _calculate_performance_metrics(self, initial_capital, final_balance, trades, equity_curve):
        """
        Calcula métricas de rendimiento del backtest.

        Args:
            initial_capital (float): Capital inicial.
            final_balance (float): Balance final.
            trades (list): Lista de trades realizados.
            equity_curve (list): Curva de equity.

        Returns:
            dict: Métricas de rendimiento.
        """
        if not trades:
            return {
                'total_return_pct': 0,
                'profit_factor': 0,
                'win_rate': 0,
                'max_drawdown_pct': 0,
                'sharpe_ratio': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0
            }

        equity_df = pd.DataFrame(equity_curve)
        total_return = (final_balance - initial_capital) / initial_capital * 100
        winning_trades = [t for t in trades if t['pnl_pct'] > 0]
        losing_trades = [t for t in trades if t['pnl_pct'] <= 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0
        total_profit = sum(t['pnl_pct'] for t in winning_trades)
        total_loss = abs(sum(t['pnl_pct'] for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        equity_df['peak'] = equity_df['balance'].cummax()
        equity_df['drawdown'] = (equity_df['balance'] - equity_df['peak']) / equity_df['peak'] * 100
        max_drawdown_pct = abs(equity_df['drawdown'].min())
        equity_df['daily_return'] = equity_df['balance'].pct_change()
        mean_return = equity_df['daily_return'].mean()
        std_return = equity_df['daily_return'].std()
        sharpe_ratio = (mean_return / std_return) * (252 ** 0.5) if std_return > 0 else 0

        return {
            'total_return_pct': total_return,
            'profit_factor': profit_factor,
            'win_rate': win_rate,
            'max_drawdown_pct': max_drawdown_pct,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades)
        }
