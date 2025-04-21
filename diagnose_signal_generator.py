# Archivo: diagnose_signal_generator.py

import os
import sys
import logging
import traceback
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Diagnóstico")

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar componentes necesarios
try:
    from core.strategy.signal_generator import SignalGenerator
    from core.models.model_manager import ModelManager
    from core.features.technical_features import TechnicalFeatures
except ImportError as e:
    logger.error(f"Error importando componentes: {e}")
    sys.exit(1)

def create_synthetic_data():
    """Crea datos sintéticos para probar el generador de señales"""
    # Crear datos para BTC/USDT
    btc_price = 50000
    btc_volume = 100
    
    # Crear fechas para series temporales
    dates = pd.date_range(
        start=datetime.now() - timedelta(hours=10),
        end=datetime.now(),
        periods=10
    )
    
    # Crear precios con tendencia
    btc_prices = np.linspace(btc_price * 0.95, btc_price, 10)
    btc_close = pd.Series(btc_prices, index=dates)
    
    # Estructura completa
    market_data = {
        'BTC/USDT': {
            'price': float(btc_prices[-1]),
            'volume': float(btc_volume),
            'close': btc_close,
            'timestamp': datetime.now()
        },
        'ETH/USDT': {
            'price': 1500.0,
            'volume': 200.0,
            'close': pd.Series(np.linspace(1450, 1500, 10), index=dates),
            'timestamp': datetime.now()
        }
    }
    
    return market_data

def inspect_object(obj, name="objeto", max_depth=3, current_depth=0):
    """Inspecciona un objeto recursivamente hasta max_depth"""
    if current_depth >= max_depth:
        return f"[Profundidad máxima alcanzada]"
    
    if obj is None:
        return "None"
    
    if isinstance(obj, (int, float, str, bool)):
        return str(obj)
    
    if isinstance(obj, (list, tuple)):
        if len(obj) > 5:
            return f"[{type(obj).__name__} con {len(obj)} elementos]"
        return [inspect_object(x, f"{name}[{i}]", max_depth, current_depth+1) 
                for i, x in enumerate(obj[:5])]
    
    if isinstance(obj, dict):
        if len(obj) > 10:
            return f"[Diccionario con {len(obj)} claves]"
        return {k: inspect_object(v, f"{name}.{k}", max_depth, current_depth+1) 
                for k, v in list(obj.items())[:10]}
    
    if isinstance(obj, pd.Series):
        return f"[Serie de pandas con {len(obj)} elementos]"
    
    if isinstance(obj, pd.DataFrame):
        return f"[DataFrame de pandas con {obj.shape}]"
    
    if hasattr(obj, '__dict__'):
        attrs = {}
        for k, v in obj.__dict__.items():
            if not k.startswith('_'):
                attrs[k] = inspect_object(v, f"{name}.{k}", max_depth, current_depth+1)
        return attrs
    
    return str(type(obj))

def diagnose_signal_generator():
    """Diagnostica el problema en el generador de señales"""
    logger.info("=== DIAGNÓSTICO DEL GENERADOR DE SEÑALES ===")
    
    try:
        # Crear instancias para prueba
        config = {}
        technical_features = TechnicalFeatures()
        model_manager = ModelManager(config)
        signal_generator = SignalGenerator(config, model_manager, technical_features)
        
        logger.info("Componentes inicializados correctamente")
        
        # Crear datos sintéticos completos
        logger.info("Creando datos sintéticos completos...")
        complete_data = create_synthetic_data()
        
        # Probar con datos completos
        logger.info("Probando con datos completos...")
        try:
            signal = signal_generator.generate_signal('BTC/USDT', complete_data)
            logger.info(f"Señal generada correctamente: {signal}")
        except Exception as e:
            logger.error(f"Error con datos completos: {e}")
            logger.error(traceback.format_exc())
        
        # Crear datos incompletos (sin 'close')
        logger.info("Creando datos incompletos (sin 'close')...")
        incomplete_data = {
            'BTC/USDT': {
                'price': 50000.0,
                'volume': 100.0,
                'timestamp': datetime.now()
            }
        }
        
        # Probar con datos incompletos
        logger.info("Probando con datos incompletos...")
        try:
            signal = signal_generator.generate_signal('BTC/USDT', incomplete_data)
            logger.info(f"Señal generada correctamente: {signal}")
        except Exception as e:
            logger.error(f"Error con datos incompletos: {e}")
            logger.error(traceback.format_exc())
        
        # Inspeccionar el método _extract_features
        logger.info("Inspeccionando método _extract_features...")
        
        # Verificar si el método existe
        if hasattr(signal_generator, '_extract_features'):
            try:
                # Guardar referencia al método original
                original_method = signal_generator._extract_features
                
                # Crear un wrapper para el método
                def debug_extract_features(self, symbol, market_data):
                    logger.debug(f"DENTRO DE _extract_features - symbol: {symbol}")
                    logger.debug(f"DENTRO DE _extract_features - market_data keys: {market_data.keys()}")
                    if symbol in market_data:
                        logger.debug(f"DENTRO DE _extract_features - market_data[symbol] keys: {market_data[symbol].keys()}")
                    
                    try:
                        result = original_method(symbol, market_data)
                        logger.debug(f"DENTRO DE _extract_features - result: {result}")
                        return result
                    except Exception as e:
                        logger.error(f"DENTRO DE _extract_features - ERROR: {e}")
                        # Si el error es sobre 'close', mostrar información específica
                        if "'close'" in str(e):
                            logger.error("El error está relacionado con 'close'")
                            # Ver exactamente dónde se está intentando acceder a 'close'
                            logger.error(traceback.format_exc())
                        raise
                
                # Reemplazar temporalmente el método
                from types import MethodType
                signal_generator._extract_features = MethodType(debug_extract_features, signal_generator)
                
                # Probar nuevamente con datos incompletos
                logger.info("Probando nuevamente con datos incompletos (con debug)...")
                try:
                    signal = signal_generator.generate_signal('BTC/USDT', incomplete_data)
                    logger.info(f"Señal generada correctamente: {signal}")
                except Exception as e:
                    logger.error(f"Error con datos incompletos (con debug): {e}")
                
                # Restaurar el método original
                signal_generator._extract_features = original_method
                
            except Exception as e:
                logger.error(f"Error al inspeccionar _extract_features: {e}")
                logger.error(traceback.format_exc())
        else:
            logger.warning("El método _extract_features no existe en SignalGenerator")
        
        # Inspeccionar la clase SignalGenerator
        logger.info("Inspeccionando clase SignalGenerator...")
        sg_attrs = inspect_object(signal_generator, "signal_generator")
        logger.info(f"Atributos de SignalGenerator: {json.dumps(sg_attrs, indent=2)}")
        
        # Ver código fuente de los métodos
        import inspect
        if hasattr(signal_generator, 'generate_signal'):
            logger.info("Código de generate_signal:")
            logger.info(inspect.getsource(signal_generator.generate_signal))
        
        if hasattr(signal_generator, '_extract_features'):
            logger.info("Código de _extract_features:")
            logger.info(inspect.getsource(signal_generator._extract_features))
        
    except Exception as e:
        logger.error(f"Error general en diagnóstico: {e}")
        logger.error(traceback.format_exc())
    
    logger.info("=== DIAGNÓSTICO COMPLETADO ===")

if __name__ == "__main__":
    diagnose_signal_generator()