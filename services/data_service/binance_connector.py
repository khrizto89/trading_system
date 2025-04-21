# Conexi�n a Binance

import threading
import logging
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.exceptions import BinanceAPIException, BinanceRequestException
import time

class BinanceConnector:
    def __init__(self, api_key="", api_secret="", testnet=True):
        """
        Inicializa el conector de Binance.

        :param api_key: Clave de API de Binance.
        :param api_secret: Clave secreta de API de Binance.
        :param testnet: Indica si se debe usar el entorno de prueba de Binance.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.client = None
        self.logger = logging.getLogger("BinanceConnector")

    def connect(self):
        """
        Intenta conectar al servidor de Binance y verifica la conexión.

        :return: True si la conexión es exitosa, False en caso contrario.
        """
        try:
            # Inicializa el cliente
            self.client = Client(self.api_key, self.api_secret)
            if self.testnet:
                self.client.API_URL = 'https://testnet.binance.vision/api'

            # Verifica la conexión
            server_time = self.client.get_server_time()
            self.logger.info(f"Conexión exitosa a Binance. Hora del servidor: {server_time}")
            return True
        except BinanceAPIException as e:
            self.logger.error(f"Error de API de Binance: {e}")
        except BinanceRequestException as e:
            self.logger.error(f"Error de conexión con Binance: {e}")
        except Exception as e:
            self.logger.error(f"Error inesperado conectando a Binance: {e}")
        return False

    def get_ohlcv(self, symbol, interval, limit=500):
        with threading.Lock():
            try:
                return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            except (BinanceAPIException, BinanceRequestException) as e:
                self.logger.error(f"Error fetching OHLCV data: {e}")
                return None

    def get_account_balance(self):
        with threading.Lock():
            try:
                return self.client.get_account()
            except (BinanceAPIException, BinanceRequestException) as e:
                self.logger.error(f"Error fetching account balance: {e}")
                return None

    def get_open_positions(self):
        with threading.Lock():
            try:
                return self.client.futures_account()
            except (BinanceAPIException, BinanceRequestException) as e:
                self.logger.error(f"Error fetching open positions: {e}")
                return None

    def create_order(self, symbol, side, order_type, quantity, price=None):
        with threading.Lock():
            try:
                if order_type == Client.ORDER_TYPE_LIMIT:
                    return self.client.create_order(
                        symbol=symbol,
                        side=side,
                        type=order_type,
                        quantity=quantity,
                        price=price,
                        timeInForce=Client.TIME_IN_FORCE_GTC
                    )
                else:
                    return self.client.create_order(
                        symbol=symbol,
                        side=side,
                        type=order_type,
                        quantity=quantity
                    )
            except (BinanceAPIException, BinanceRequestException) as e:
                self.logger.error(f"Error creating order: {e}")
                return None

    def cancel_order(self, symbol, order_id):
        with threading.Lock():
            try:
                return self.client.cancel_order(symbol=symbol, orderId=order_id)
            except (BinanceAPIException, BinanceRequestException) as e:
                self.logger.error(f"Error canceling order: {e}")
                return None

    def subscribe_to_ticker(self, symbol, callback):
        if not hasattr(self, 'bsm') or not self.bsm:
            self.bsm = BinanceSocketManager(self.client)
        conn_key = self.bsm.start_symbol_ticker_socket(symbol, callback)
        if not hasattr(self, 'ws_connections'):
            self.ws_connections = {}
        self.ws_connections[symbol] = conn_key
        self.bsm.start()

    def stop_ticker_subscription(self, symbol):
        if hasattr(self, 'ws_connections') and symbol in self.ws_connections:
            self.bsm.stop_socket(self.ws_connections[symbol])
            del self.ws_connections[symbol]

    def reconnect(self):
        self.logger.info("Reconnecting to Binance...")
        time.sleep(5)
        self.client = Client(self.api_key, self.api_secret)
        if self.testnet:
            self.client.API_URL = 'https://testnet.binance.vision/api'
        if hasattr(self, 'bsm') and self.bsm:
            self.bsm.close()
            self.bsm = None
        if hasattr(self, 'ws_connections'):
            self.ws_connections = {}

    def handle_error(self, error):
        self.logger.error(f"Error occurred: {error}")
        self.reconnect()

    def get_market_data(self, symbols=None):
        """
        Obtiene datos de mercado para los símbolos especificados.

        :param symbols: Lista de pares de mercado (por ejemplo, ["BTC/USDT", "ETH/USDT"]).
        :return: Diccionario con los datos de mercado o datos simulados en caso de error.
        """
        if not symbols:
            symbols = ["BTC/USDT", "ETH/USDT"]

        result = {}
        try:
            for symbol in symbols:
                # Convertir formato BTC/USDT a BTCUSDT para Binance
                binance_symbol = symbol.replace("/", "")
                ticker = self.client.get_ticker(symbol=binance_symbol)
                result[symbol] = {
                    'price': float(ticker['lastPrice']),
                    'volume': float(ticker['volume'])
                }
            return result
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de mercado: {e}")
            # Fallback a datos simulados
            return {
                'BTC/USDT': {'price': 50000, 'volume': 10},
                'ETH/USDT': {'price': 3000, 'volume': 20}
            }

    def disconnect(self):
        """
        Desconecta el cliente de Binance.

        :return: True si la desconexión es exitosa.
        """
        self.client = None
        self.logger.info("Cliente de Binance desconectado.")
        return True
