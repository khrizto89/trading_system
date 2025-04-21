#!/usr/bin/env python3
"""
Validación del generador de señales del sistema de trading
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ValidacionSeñales')

def validate_signal_generator():
    """Valida el generador de señales"""
    try:
        from core.features.technical_features import TechnicalFeatures
        from core.strategy.signal_generator import SignalGenerator
        
        logger.info("Iniciando validación del generador de señales...")
        
        # Crear indicadores (necesarios para el SignalGenerator)
        indicators = TechnicalFeatures()
        logger.info("✓ TechnicalFeatures inicializado")
        
        # Crear modelos simulados
        dummy_models = {
            'bullish_model': lambda x: 0.75,  # Modelo que simula predecir tendencia alcista
            'bearish_model': lambda x: 0.25,  # Modelo que simula predecir tendencia bajista
            'neutral_model': lambda x: 0.5    # Modelo que simula predecir tendencia neutral
        }
        
        # Inicializar generador de señales
        signal_gen = SignalGenerator(models=dummy_models, indicators=indicators)
        logger.info("✓ SignalGenerator inicializado correctamente")
        
        # Crear datos de mercado de prueba
        market_data = {
            'BTC/USDT': {
                'price': 50000,
                'volume': 1000
            },
            'ETH/USDT': {
                'price': 3000,
                'volume': 2000
            }
        }
        
        # Generar señales para cada activo
        for symbol in market_data:
            try:
                signal = signal_gen.generate_signal(symbol, market_data)
                logger.info(f"✓ Señal generada para {symbol}: {signal}")
                
                # Verificar estructura de la señal
                if isinstance(signal, dict):
                    required_keys = ['symbol', 'action', 'confidence', 'timestamp']
                    missing_keys = [key for key in required_keys if key not in signal]
                    
                    if missing_keys:
                        logger.warning(f"! Estructura de señal incompleta. Faltan claves: {missing_keys}")
                    else:
                        logger.info(f"✓ Estructura de señal correcta para {symbol}")
                else:
                    logger.warning(f"! La señal para {symbol} no es un diccionario: {signal}")
            
            except Exception as e:
                logger.error(f"✗ Error generando señal para {symbol}: {e}")
        
        logger.info("Validación del generador de señales completada")
        return True
    
    except ImportError as e:
        logger.error(f"✗ Error importando módulos de señales: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error general en validación: {e}")
        return False

def validate_risk_manager():
    """Valida el gestor de riesgo"""
    try:
        from core.strategy.risk_manager import RiskManager
        
        logger.info("Iniciando validación del gestor de riesgo...")
        
        # Inicializar gestor de riesgo
        risk_manager = RiskManager()
        logger.info("✓ RiskManager inicializado correctamente")
        
        # Crear señal de prueba
        test_signal = {
            'symbol': 'BTC/USDT',
            'action': 'BUY',
            'confidence': 0.85,
            'timestamp': pd.Timestamp.now()
        }
        
        # Validar señal
        try:
            result = risk_manager.validate_signal(test_signal)
            logger.info(f"✓ Validación de señal: {result}")
        except Exception as e:
            logger.error(f"✗ Error validando señal: {e}")
        
        # Verificar límites de posición
        try:
            position_limit = risk_manager.get_position_limit('BTC/USDT')
            logger.info(f"✓ Límite de posición para BTC/USDT: {position_limit}")
        except Exception as e:
            logger.error(f"✗ Error obteniendo límite de posición: {e}")
        
        # Verificar stop loss
        try:
            stop_loss = risk_manager.calculate_stop_loss('BTC/USDT', 50000, 'BUY')
            logger.info(f"✓ Stop Loss calculado para BTC/USDT: {stop_loss}")
        except Exception as e:
            logger.error(f"✗ Error calculando stop loss: {e}")
        
        logger.info("Validación del gestor de riesgo completada")
        return True
    
    except ImportError as e:
        logger.error(f"✗ Error importando RiskManager: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error general en validación: {e}")
        return False

def main():
    """Función principal"""
    logger.info("=== VALIDACIÓN DE MÓDULOS DE SEÑALES ===")
    
    # Comprobar estructura de directorios
    logger.info("Verificando estructura de directorios...")
    
    for root, dirs, files in os.walk("./core/strategy"):
        logger.info(f"Directorio: {root}")
        logger.info(f"  Subdirectorios: {dirs}")
        logger.info(f"  Archivos: {files}")
    
    # Validar generador de señales
    signal_result = validate_signal_generator()
    
    # Validar gestor de riesgo
    risk_result = validate_risk_manager()
    
    if signal_result and risk_result:
        logger.info("✓ Todos los tests de señales pasaron")
    else:
        logger.warning("! Algunos tests de señales fallaron")
    
    logger.info("=== VALIDACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()