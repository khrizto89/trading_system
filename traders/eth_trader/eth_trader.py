import logging
from traders.trader_base import TraderBase

class ETHTrader(TraderBase):
    """Trader específico para Ethereum"""
    
    def __init__(self, data_service, signal_generator, position_manager, notification_service, **kwargs):
        """Inicializa el trader con los servicios necesarios"""
        super().__init__(
            symbol="ETH/USDT",
            name="ETHTrader",
            data_service=data_service,
            signal_generator=signal_generator,
            position_manager=position_manager,
            notification_service=notification_service,
            **kwargs
        )
        self.logger = logging.getLogger(self.name)
        self.volatility_threshold = 0.03  # Ejemplo: 3% de volatilidad diaria
        self.max_position_size = 10.0  # Tamaño máximo de posición en ETH
        self.risk_per_trade = 0.02  # Riesgo del 2% del capital por operación
        self.market_conditions = "neutral"  # Condición de mercado predeterminada

    def configure(self, config):
        """
        Configura el trader con parámetros específicos para ETH.
        :param config: Diccionario con parámetros de configuración.
        """
        self.volatility_threshold = config.get("volatility_threshold", self.volatility_threshold)
        self.max_position_size = config.get("max_position_size", self.max_position_size)
        self.risk_per_trade = config.get("risk_per_trade", self.risk_per_trade)
        self.logger.info(f"ETHTrader configurado con: {config}")

    def on_error(self, error):
        """
        Manejo de errores específico para ETH.
        :param error: Mensaje de error o excepción.
        """
        self.logger.error(f"Error en ETHTrader: {error}")
        if self.notification_service:
            self.notification_service.send_message(f"Error en ETHTrader: {error}")
