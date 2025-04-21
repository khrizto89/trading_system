# Plantilla de implementación para nuevos traders

from traders.trader_base import TraderBase

class TemplateTrader(TraderBase):
    """
    Plantilla base para implementar nuevos traders.
    Extiende TraderBase e incluye lógica genérica y ejemplos de personalización.
    """

    def __init__(self, config):
        """
        Inicializa el trader con la configuración proporcionada.
        :param config: Configuración específica para el trader.
        """
        super().__init__(config)
        self.strategy_params = config.get("strategy_params", {})
        self.position_size = config.get("position_size", 0.01)

    def analyze_market(self, market_data):
        """
        Analiza el mercado y genera señales de trading.
        :param market_data: Datos de mercado (DataFrame).
        :return: Señal de trading (compra, venta, mantener).
        """
        # Lógica genérica: ejemplo de cruce de medias móviles
        sma_short = market_data['close'].rolling(window=5).mean()
        sma_long = market_data['close'].rolling(window=20).mean()

        if sma_short.iloc[-1] > sma_long.iloc[-1]:
            return "buy"
        elif sma_short.iloc[-1] < sma_long.iloc[-1]:
            return "sell"
        else:
            return "hold"

    def execute_trade(self, signal):
        """
        Ejecuta una operación basada en la señal generada.
        :param signal: Señal de trading (buy, sell, hold).
        """
        if signal == "buy":
            self.buy(self.position_size)
        elif signal == "sell":
            self.sell(self.position_size)
        else:
            self.log("Manteniendo posición actual.")

    def customize_behavior(self, hook_name, *args, **kwargs):
        """
        Hook para personalizar el comportamiento del trader.
        :param hook_name: Nombre del hook.
        :param args: Argumentos adicionales.
        :param kwargs: Argumentos clave adicionales.
        """
        if hook_name == "on_market_open":
            self.log("Mercado abierto. Preparando estrategias.")
        elif hook_name == "on_market_close":
            self.log("Mercado cerrado. Evaluando rendimiento.")
        else:
            self.log(f"Hook no reconocido: {hook_name}")

    def example_strategy(self, market_data):
        """
        Ejemplo de estrategia pre-implementada.
        :param market_data: Datos de mercado (DataFrame).
        :return: Señal de trading.
        """
        rsi = self.calculate_rsi(market_data['close'], window=14)
        if rsi.iloc[-1] < 30:
            return "buy"
        elif rsi.iloc[-1] > 70:
            return "sell"
        else:
            return "hold"

    @staticmethod
    def calculate_rsi(data, window):
        """
        Calcula el Índice de Fuerza Relativa (RSI).
        :param data: Serie de precios de cierre.
        :param window: Ventana de cálculo.
        :return: Serie con valores de RSI.
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def best_practices_guide(self):
        """
        Guía de mejores prácticas para implementar nuevos traders.
        """
        self.log("1. Mantenga la lógica de análisis separada de la ejecución.")
        self.log("2. Use hooks para personalizar comportamiento sin modificar la base.")
        self.log("3. Pruebe estrategias con datos históricos antes de usarlas en producción.")
        self.log("4. Documente cada método y su propósito para facilitar el mantenimiento.")
