import os
import logging
from binance.client import Client  # Correct import for Binance API client

logger = logging.getLogger("BinanceConnector")

class BinanceConnector:
    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = True):
        """
        Inicializa el conector a Binance.
        
        Args:
            api_key: API Key de Binance
            api_secret: API Secret de Binance
            testnet: Si es True, utiliza el testnet de Binance
        """
        # Usar variables de entorno si no se proporcionan credenciales
        self.api_key = api_key or os.environ.get("BINANCE_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("BINANCE_API_SECRET", "")
        
        # Determinar si usar testnet
        self.testnet = testnet
        
        # URLs base
        self.base_url = "https://testnet.binance.vision/api" if self.testnet else "https://api.binance.com/api"
        logger.info(f"Usando Binance {'Testnet' if self.testnet else 'Producción'}")
        
        # Validar credenciales
        if not self.api_key or not self.api_secret:
            logger.warning("Credenciales de Binance no configuradas. Algunas funcionalidades pueden no estar disponibles.")
        
        # Inicializar cliente de Binance
        self.client = Client(self.api_key, self.api_secret, testnet=self.testnet)

    def connect(self):
        """Prueba la conexión a la API de Binance."""
        try:
            server_time = self.client.get_server_time()
            logger.info(f"Conexión a Binance exitosa. Hora del servidor: {server_time}")
            return True
        except Exception as e:
            logger.error(f"Error al conectar a Binance: {e}")
            return False

    def get_historical_data(self, symbol, interval, start_time, end_time):
        """
        Obtiene datos históricos de Binance.
        
        Args:
            symbol: Par de trading (e.g., "BTC/USDT")
            interval: Intervalo de tiempo (e.g., "1h")
            start_time: Timestamp de inicio en milisegundos
            end_time: Timestamp de fin en milisegundos
        
        Returns:
            Lista de datos históricos.
        """
        try:
            klines = self.client.get_historical_klines(symbol, interval, start_time, end_time)
            data = []
            for kline in klines:
                data.append({
                    "open_time": kline[0],
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5]),
                    "close_time": kline[6]
                })
            return data
        except Exception as e:
            logger.error(f"Error al obtener datos históricos de Binance: {e}")
            return []
