import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import pandas as pd

# Clase base para todos los traders
class TraderBase(ABC):
    """
    Clase base para todos los traders.
    """
    def __init__(self, symbol, name, data_service, signal_generator, position_manager, notification_service, **kwargs):
        """
        Initialize the base trader.
        :param symbol: Trading symbol for the trader.
        :param name: Name of the trader.
        :param data_service: Service for fetching market data.
        :param signal_generator: Signal generator for trading decisions.
        :param position_manager: Manager for handling positions and orders.
        :param notification_service: Service for sending notifications.
        :param kwargs: Additional keyword arguments.
        """
        self.symbol = symbol
        self.name = name
        self.data_service = data_service
        self.signal_generator = signal_generator
        self.position_manager = position_manager
        self.notification_service = notification_service
        self.logger = kwargs.get('logger', None) or logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.timeframe = 60
        self.state = "inactive"  # Possible states: active, inactive, error
        self.lock = threading.Lock()
        self.thread = None

    def get_symbol(self):
        """
        Obtiene el símbolo de trading del trader.
        """
        return self.symbol

    def get_name(self):
        """Obtiene el nombre del trader"""
        return self.name

    def start(self):
        """Start the trading loop in a separate thread."""
        with self.lock:
            if self.state == "active":
                self.logger.warning(f"{self.name} is already running.")
                return
            self.state = "active"
            self.thread = threading.Thread(target=self._trading_loop, daemon=True)
            self.thread.start()
            self.logger.info(f"{self.name} started.")

    def stop(self):
        """Stop the trading loop."""
        with self.lock:
            if self.state != "active":
                self.logger.warning(f"{self.name} is not running.")
                return
            self.state = "inactive"
            self.logger.info(f"{self.name} stopped.")

    def pause(self):
        """Pause the trading loop."""
        with self.lock:
            if self.state != "active":
                self.logger.warning(f"{self.name} is not running.")
                return
            self.state = "paused"
            self.logger.info(f"{self.name} paused.")

    def resume(self):
        """Resume the trading loop."""
        with self.lock:
            if self.state != "paused":
                self.logger.warning(f"{self.name} is not paused.")
                return
            self.state = "active"
            self.logger.info(f"{self.name} resumed.")

    def _trading_loop(self):
        """Main trading loop."""
        while self.state == "active":
            try:
                self.logger.info(f"{self.name} executing trading cycle at {datetime.now()}.")
                self._execute_cycle()
            except Exception as e:
                self.logger.error(f"Error in {self.name}: {e}")
                self.notification_service.send(f"Error in {self.name}: {e}")
                self.state = "error"
                break
            time.sleep(self.timeframe)

    def _execute_cycle(self):
        """Execute a single trading cycle."""
        # Step 1: Fetch market data
        data = self._fetch_data()

        # Step 2: Process data and generate signals
        signal = self._analyze_data(data)

        # Step 3: Make trading decisions and execute orders
        self._execute_orders(signal)

        # Step 4: Monitor positions
        self._monitor_positions()

    def _fetch_data(self):
        """Fetch market data."""
        self.logger.info(f"{self.name} fetching market data.")
        return self.data_service.get_market_data()

    def _analyze_data(self, data):
        """Analyze data and generate trading signals."""
        self.logger.info(f"{self.name} analyzing data.")
        return self.signal_generator.generate_signals(data)

    def _execute_orders(self, signal):
        """Execute trading orders based on signals."""
        self.logger.info(f"{self.name} executing orders with signal: {signal}.")
        self.position_manager.execute(signal)

    def _monitor_positions(self):
        """Monitor open positions."""
        self.logger.info(f"{self.name} monitoring positions.")
        positions = self.position_manager.get_open_positions()
        self.logger.info(f"{self.name} open positions: {positions}.")

    def analyze_market(self, market_data):
        """Analiza el mercado y genera señales de trading"""
        if self.symbol not in market_data:
            return None
            
        # Generar señal usando el generador de señales
        return self.signal_generator.generate_signal(self.symbol, market_data)
    
    def execute_paper_trade(self, signal):
        """Ejecuta una operación simulada basada en la señal"""
        if not signal:
            return None
            
        # Implementación básica
        result = {
            'symbol': self.symbol,
            'action': signal.get('action', 'HOLD'),
            'price': signal.get('price', 0),
            'timestamp': pd.Timestamp.now(),
            'type': 'paper'
        }
        
        # Notificar si está habilitado
        if self.notification_service:
            self.notification_service.send_trade_notification(result)
            
        return result
        
    def execute_live_trade(self, signal):
        """Ejecuta una operación real basada en la señal"""
        if not signal:
            return None
            
        # Usar el position_manager para ejecutar la operación
        result = self.position_manager.execute_trade(
            symbol=self.symbol,
            action=signal.get('action', 'HOLD'),
            price=signal.get('price', 0),
            confidence=signal.get('confidence', 0)
        )
        
        # Notificar si está habilitado
        if result and self.notification_service:
            self.notification_service.send_trade_notification(result)
            
        return result

    @abstractmethod
    def configure(self, config):
        """Configure the trader with specific settings."""
        pass

    @abstractmethod
    def on_error(self, error):
        """Handle errors specific to the trader."""
        pass
