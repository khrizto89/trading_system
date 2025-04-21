# Gestión de posiciones

from ..services.data_service.binance_connector import BinanceConnector
from .risk_manager import RiskManager
import time

class PositionManager:
    def __init__(self, binance_connector: BinanceConnector, risk_manager: RiskManager):
        """
        Initialize the position manager.
        :param binance_connector: Instance of BinanceConnector for order execution.
        :param risk_manager: Instance of RiskManager for risk parameters.
        """
        self.binance_connector = binance_connector
        self.risk_manager = risk_manager
        self.positions = {}  # Track open positions
        self.last_trade_time = {}  # Track last trade time for each symbol
        self.min_trade_interval = 60  # Minimum time (in seconds) between trades per symbol

    def execute(self, signal):
        """
        Execute orders based on trading signals.
        :param signal: Dictionary containing 'signal', 'confidence', 'stop_loss', and 'take_profit'.
        """
        symbol = "BTCUSDT"  # Example symbol, can be dynamic
        if signal['signal'] == 0:
            print(f"No action for {symbol} (Hold).")
            return

        # Avoid over-trading
        if not self._can_trade(symbol):
            print(f"Skipping trade for {symbol} due to minimum trade interval.")
            return

        # Calculate position size
        volatility = self._get_volatility(symbol)
        position_size = self.risk_manager.calculate_position_size(
            risk_per_trade=0.01,  # Example: 1% risk per trade
            volatility=volatility,
            method="volatility"
        )

        # Execute order
        if signal['signal'] == 1:  # Buy
            self._open_position(symbol, "BUY", position_size, signal['stop_loss'], signal['take_profit'])
        elif signal['signal'] == -1:  # Sell
            self._open_position(symbol, "SELL", position_size, signal['stop_loss'], signal['take_profit'])

    def _open_position(self, symbol, side, quantity, stop_loss, take_profit):
        """
        Open a new position with stop-loss and take-profit levels.
        :param symbol: Trading pair (e.g., BTCUSDT).
        :param side: "BUY" or "SELL".
        :param quantity: Quantity to trade.
        :param stop_loss: Stop-loss price.
        :param take_profit: Take-profit price.
        """
        order_type = "MARKET"
        print(f"Placing {side} order for {symbol} with quantity {quantity}.")
        order = self.binance_connector.create_order(symbol, side, order_type, quantity)

        if order:
            self.positions[symbol] = {
                "side": side,
                "quantity": quantity,
                "entry_price": float(order['fills'][0]['price']),
                "stop_loss": stop_loss,
                "take_profit": take_profit
            }
            self.last_trade_time[symbol] = time.time()
            print(f"Position opened for {symbol}: {self.positions[symbol]}")

    def _can_trade(self, symbol):
        """
        Check if the symbol can be traded based on the minimum trade interval.
        :param symbol: Trading pair.
        :return: Boolean indicating if trading is allowed.
        """
        last_time = self.last_trade_time.get(symbol, 0)
        return (time.time() - last_time) >= self.min_trade_interval

    def _get_volatility(self, symbol):
        """
        Fetch the current market volatility for the symbol.
        :param symbol: Trading pair.
        :return: Volatility value.
        """
        ohlcv = self.binance_connector.get_ohlcv(symbol, interval="1h", limit=14)
        if ohlcv:
            closes = [float(candle[4]) for candle in ohlcv]
            return pd.Series(closes).pct_change().std()
        return 0.01  # Default volatility if data is unavailable

    def monitor_positions(self):
        """
        Monitor and adjust open positions based on market conditions.
        """
        for symbol, position in list(self.positions.items()):
            current_price = float(self.binance_connector.get_ohlcv(symbol, interval="1m", limit=1)[-1][4])

            # Check stop-loss
            if position["side"] == "BUY" and current_price <= position["stop_loss"]:
                print(f"Stop-loss triggered for {symbol}. Closing position.")
                self._close_position(symbol)
            elif position["side"] == "SELL" and current_price >= position["stop_loss"]:
                print(f"Stop-loss triggered for {symbol}. Closing position.")
                self._close_position(symbol)

            # Check take-profit
            if position["side"] == "BUY" and current_price >= position["take_profit"]:
                print(f"Take-profit reached for {symbol}. Closing position.")
                self._close_position(symbol)
            elif position["side"] == "SELL" and current_price <= position["take_profit"]:
                print(f"Take-profit reached for {symbol}. Closing position.")
                self._close_position(symbol)

    def _close_position(self, symbol):
        """
        Close an open position.
        :param symbol: Trading pair.
        """
        position = self.positions.pop(symbol, None)
        if position:
            side = "SELL" if position["side"] == "BUY" else "BUY"
            print(f"Closing position for {symbol}: {position}")
            self.binance_connector.create_order(symbol, side, "MARKET", position["quantity"])
