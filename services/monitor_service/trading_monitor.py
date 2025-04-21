# Monitoreo de trading

import threading
import time
from datetime import datetime
import pandas as pd
import numpy as np

class TradingMonitor:
    def __init__(self, notification_service, log_file="trading_metrics.log"):
        """
        Initialize the trading monitor.
        :param notification_service: Service for sending notifications.
        :param log_file: File to log trading metrics.
        """
        self.notification_service = notification_service
        self.log_file = log_file
        self.trades = []
        self.metrics = {
            "pnl": [],
            "win_rate": 0.0,
            "max_drawdown": 0.0,
            "model_accuracy": 0.0
        }
        self.lock = threading.Lock()
        self.running = False

    def start_monitoring(self, interval=5):
        """
        Start monitoring trading operations.
        :param interval: Interval in seconds between updates.
        """
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.thread.start()

    def stop_monitoring(self):
        """Stop monitoring trading operations."""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def _monitor_loop(self, interval):
        """Main monitoring loop."""
        while self.running:
            self._update_metrics()
            self._log_metrics()
            time.sleep(interval)

    def record_trade(self, trade):
        """
        Record a trade for monitoring.
        :param trade: Dictionary containing trade details (e.g., symbol, side, size, pnl).
        """
        with self.lock:
            self.trades.append(trade)

    def _update_metrics(self):
        """Update performance metrics."""
        with self.lock:
            if not self.trades:
                return

            # Calculate P&L
            pnl = [trade["pnl"] for trade in self.trades]
            self.metrics["pnl"] = pnl

            # Calculate win rate
            wins = len([p for p in pnl if p > 0])
            self.metrics["win_rate"] = wins / len(pnl) if pnl else 0.0

            # Calculate max drawdown
            equity_curve = np.cumsum(pnl)
            drawdown = equity_curve - np.maximum.accumulate(equity_curve)
            self.metrics["max_drawdown"] = drawdown.min() if len(drawdown) > 0 else 0.0

            # Update model accuracy (placeholder logic)
            correct_predictions = len([trade for trade in self.trades if trade.get("correct_prediction", False)])
            self.metrics["model_accuracy"] = correct_predictions / len(self.trades) if self.trades else 0.0

    def _log_metrics(self):
        """Log metrics to a file."""
        with open(self.log_file, "a") as f:
            f.write(f"{datetime.now()} - Metrics: {self.metrics}\n")

    def detect_anomalies(self, market_data):
        """
        Detect anomalies in market data.
        :param market_data: DataFrame with market data.
        :return: Boolean indicating if anomalies are detected.
        """
        # Placeholder for anomaly detection logic
        volatility = market_data["close"].pct_change().rolling(window=14).std().iloc[-1]
        if volatility > 0.05:  # Example threshold
            self.notification_service.send("High market volatility detected!")
            return True
        return False

    def visualize_metrics(self):
        """
        Generate visualizations for trading metrics.
        """
        import matplotlib.pyplot as plt

        with self.lock:
            pnl = self.metrics["pnl"]
            if not pnl:
                print("No P&L data available for visualization.")
                return

            equity_curve = np.cumsum(pnl)

        plt.figure(figsize=(10, 6))
        plt.plot(equity_curve, label="Equity Curve")
        plt.title("Equity Curve")
        plt.xlabel("Trades")
        plt.ylabel("Cumulative P&L")
        plt.legend()
        plt.show()

    def compare_strategies(self, strategies):
        """
        Compare performance of different strategies.
        :param strategies: List of strategy performance metrics.
        :return: DataFrame with comparison results.
        """
        comparison = pd.DataFrame(strategies)
        return comparison.sort_values(by="sharpe_ratio", ascending=False)
