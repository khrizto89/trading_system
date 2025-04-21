#!/usr/bin/env python3
"""
Validación del flujo completo del sistema de trading
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.models.model_manager import ModelManager
from core.strategy.signal_generator import SignalGenerator
from core.strategy.trade_mode import PaperTradeMode

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('ValidateTradingLogic')

def calculate_macd(close_prices, fast_window=12, slow_window=26, signal_window=9):
    """
    Calcula el MACD (Moving Average Convergence Divergence).
    :param close_prices: Serie de precios de cierre.
    :param fast_window: Ventana rápida.
    :param slow_window: Ventana lenta.
    :param signal_window: Ventana de la señal.
    :return: MACD, señal y el histograma.
    """
    if not isinstance(close_prices, pd.Series):
        close_prices = pd.Series(close_prices)  # Convertir a pandas.Series si no lo es

    ema_fast = close_prices.ewm(span=fast_window, adjust=False).mean()
    ema_slow = close_prices.ewm(span=slow_window, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def create_test_market_data(symbols):
    """
    Crea datos de mercado sintéticos para validar el sistema
    
    Args:
        symbols (list): Lista de símbolos para los que crear datos
        
    Returns:
        dict: Datos de mercado sintéticos
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    logger.info("Creando datos históricos de prueba...")
    market_data = {}
    
    for symbol in symbols:
        # Asignar precio base según el símbolo
        base_price = 50000 if 'BTC' in symbol else 1500
        
        # Crear serie temporal
        periods = 20
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=periods)
        dates = pd.date_range(start=start_time, end=end_time, periods=periods)
        
        # Crear precios con tendencia alcista y algo de volatilidad
        np.random.seed(42)  # Para reproducibilidad
        prices = np.linspace(base_price * 0.95, base_price, periods)
        prices = prices + np.random.normal(0, base_price * 0.005, periods)
        
        # Crear serie de precios
        close_series = pd.Series(prices, index=dates)
        
        # Volumen aleatorio
        volume = np.random.uniform(10, 100) if 'BTC' in symbol else np.random.uniform(5, 50)
        
        # Crear estructura completa
        market_data[symbol] = {
            'price': float(prices[-1]),
            'volume': float(volume),
            'close': close_series,
            'timestamp': end_time
        }
        
        logger.info(f"Datos obtenidos para {symbol}: Precio: {prices[-1]:.2f}, Volumen: {volume:.2f}")
    
    return market_data

def test_complete_flow():
    """Prueba completa del flujo de trading"""
    try:
        logger.info("Iniciando prueba completa del flujo de trading...")
        
        # Inicializar ModelManager con configuración válida
        model_manager = ModelManager(config={})  # Cambiado para evitar el error
        
        # Inicializar SignalGenerator
        signal_generator = SignalGenerator(config={}, models_manager=model_manager)
        
        # Inicializar modo de operación (paper trading)
        trade_mode = PaperTradeMode(config={})
        
        # Crear datos de mercado sintéticos
        symbols = ['BTC/USDT', 'ETH/USDT']
        market_data = create_test_market_data(symbols)
        
        # Imprimir la estructura para depurar
        logger.debug(f"Estructura de market_data generado: {market_data.keys()}")
        for symbol in symbols:
            logger.debug(f"Claves para {symbol}: {market_data[symbol].keys()}")
        
        # Simular flujo de trading
        for symbol in symbols:
            signal = signal_generator.generate_signal(symbol, market_data)
            trade_mode.execute_trade(None, signal)  # Pasar un trader simulado
        
        logger.info("Prueba completa del flujo de trading completada exitosamente.")
    except Exception as e:
        logger.error(f"Error en prueba de flujo completo: {e}")

def test_trader_basic(trader_name, trader_module):
    """Prueba básica de un trader"""
    try:
        logger.info(f"Iniciando prueba básica para el trader: {trader_name}")
        
        # Simular inicialización del trader
        trader = trader_module(config={})
        
        # Corregir la función lambda para aceptar 3 argumentos
        market_analysis = lambda trader, market_data, *args: trader.analyze_market(market_data)
        
        # Simular análisis de mercado
        market_data = {'BTC/USDT': {'price': 50000, 'volume': 1000}}
        market_analysis(trader, market_data)
        
        logger.info(f"Prueba básica para el trader {trader_name} completada exitosamente.")
    except Exception as e:
        logger.error(f"Error inicializando trader {trader_name}: {e}")

if __name__ == "__main__":
    # Ejecutar pruebas
    test_complete_flow()
    # Agregar pruebas para traders específicos si es necesario