#!/usr/bin/env python3
"""
Test rápido del sistema de trading
"""

import logging
import pandas as pd
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('QuickTest')

def main():
    """Test rápido del sistema de trading"""
    logger.info("=== TEST RÁPIDO DEL SISTEMA DE TRADING ===")
    
    # 1. Verificar binance connector
    logger.info("1. Verificando conector a Binance...")
    try:
        from services.data_service.binance_connector import BinanceConnector
        binance = BinanceConnector(testnet=True)
        
        if hasattr(binance, 'connect') and binance.connect():
            logger.info("✓ Conectado a Binance exitosamente")
            
            # Verificar datos de mercado
            data = binance.get_market_data(["BTC/USDT"])
            logger.info(f"✓ Datos de mercado obtenidos: {data}")
        else:
            logger.error("✗ No se pudo conectar a Binance")
    except Exception as e:
        logger.error(f"✗ Error con el conector de Binance: {e}")
    
    # 2. Verificar modelo manager
    logger.info("\n2. Verificando Model Manager...")
    try:
        from core.models.model_manager import ModelManager
        model_manager = ModelManager()
        logger.info("✓ ModelManager inicializado")
        
        if hasattr(model_manager, 'list_available_models'):
            models = model_manager.list_available_models()
            logger.info(f"✓ Modelos disponibles: {models}")
        else:
            logger.warning("! Método list_available_models no disponible")
    except Exception as e:
        logger.error(f"✗ Error con ModelManager: {e}")
    
    # 3. Verificar indicadores técnicos
    logger.info("\n3. Verificando indicadores técnicos...")
    try:
        from core.features.technical_features import TechnicalFeatures
        indicators = TechnicalFeatures()
        logger.info("✓ TechnicalFeatures inicializado")
        
        # Crear datos de prueba
        import numpy as np
        test_prices = np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 
                               108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0])
        
        # RSI
        if hasattr(indicators, 'calculate_rsi'):
            try:
                rsi = indicators.calculate_rsi(test_prices, window=14)
                logger.info(f"✓ RSI calculado: {rsi[-1]}")
            except Exception as e:
                logger.error(f"✗ Error calculando RSI: {e}")
        
        # Bollinger Bands
        if hasattr(indicators, 'calculate_bollinger'):
            try:
                upper, middle, lower = indicators.calculate_bollinger(test_prices, window=20, num_std=2)
                logger.info(f"✓ Bandas de Bollinger calculadas")
            except Exception as e:
                logger.error(f"✗ Error calculando Bollinger Bands: {e}")
        
    except Exception as e:
        logger.error(f"✗ Error con indicadores técnicos: {e}")
    
    # 4. Verificar traders disponibles
    logger.info("\n4. Verificando traders...")
    try:
        # BTC Trader
        logger.info("Verificando BTC Trader...")
        from traders.btc_trader.btc_trader import BTCTrader
        
        # Crear mocks mínimos
        mock_data_service = type('DataServiceMock', (), {
            'get_market_data': lambda *args: {'BTC/USDT': {'price': 50000, 'volume': 1000}}
        })()
        
        mock_signal_gen = type('SignalGeneratorMock', (), {
            'generate_signal': lambda *args, **kwargs: {
                'symbol': 'BTC/USDT', 
                'action': 'BUY', 
                'confidence': 0.75,
                'timestamp': datetime.now()
            }
        })()
        
        mock_pos_mgr = type('PositionManagerMock', (), {
            'execute_trade': lambda *args, **kwargs: True,
            'get_open_positions': lambda: []
        })()
        
        mock_notify = type('NotificationServiceMock', (), {
            'send_message': lambda *args: None,
            'send_trade_notification': lambda *args: None
        })()
        
        # Inicializar trader
        btc_trader = BTCTrader(
            data_service=mock_data_service,
            signal_generator=mock_signal_gen,
            position_manager=mock_pos_mgr,
            notification_service=mock_notify
        )
        
        logger.info(f"✓ BTC Trader inicializado: {btc_trader.name}")
        
        # ETH Trader
        logger.info("Verificando ETH Trader...")
        try:
            from traders.eth_trader.eth_trader import ETHTrader
            
            # Intentar inicializar
            try:
                eth_trader = ETHTrader(
                    data_service=mock_data_service,
                    signal_generator=mock_signal_gen,
                    position_manager=mock_pos_mgr,
                    notification_service=mock_notify
                )
                logger.info(f"✓ ETH Trader inicializado: {eth_trader.name}")
            except TypeError as e:
                if "Can't instantiate abstract class" in str(e):
                    logger.warning(f"! ETH Trader es una clase abstracta: {e}")
                else:
                    logger.error(f"✗ Error inicializando ETH Trader: {e}")
            except Exception as e:
                logger.error(f"✗ Error inicializando ETH Trader: {e}")
                
        except ImportError:
            logger.error("✗ No se encontró ETHTrader")
            
    except Exception as e:
        logger.error(f"✗ Error verificando traders: {e}")
    
    # Resumen
    logger.info("\n=== TEST RÁPIDO COMPLETADO ===")

if __name__ == "__main__":
    main()