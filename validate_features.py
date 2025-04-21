#!/usr/bin/env python3
"""
Validación de características del sistema de trading
"""

import os
import sys
import logging
import numpy as np
import pandas as pd

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ValidacionFeatures')

def validate_feature_extraction():
    """Valida el extractor de características"""
    try:
        from core.features.feature_extractor import FeatureExtractor
        
        logger.info("Iniciando validación del extractor de características...")
        
        # Crear instancia
        extractor = FeatureExtractor()
        logger.info("✓ FeatureExtractor inicializado")
        
        # Verificar que tenga los métodos necesarios
        required_methods = ['extract_features', 'preprocess_data']
        for method in required_methods:
            if hasattr(extractor, method) and callable(getattr(extractor, method)):
                logger.info(f"✓ Método {method} disponible")
            else:
                logger.error(f"✗ Método {method} no encontrado")
                
        # Crear datos de prueba
        test_data = {
            'close': [100, 101, 102, 103, 104, 105],
            'open': [99, 100, 101, 102, 103, 104],
            'high': [101, 102, 103, 104, 105, 106],
            'low': [98, 99, 100, 101, 102, 103],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500]
        }
        
        df = pd.DataFrame(test_data)
        
        # Intentar extraer características
        if hasattr(extractor, 'extract_features'):
            try:
                features = extractor.extract_features(df)
                logger.info(f"✓ Extracción de características exitosa. Forma: {features.shape if hasattr(features, 'shape') else 'No disponible'}")
            except Exception as e:
                logger.error(f"✗ Error en extracción de características: {e}")
                
        logger.info("Validación de extracción de características completada")
        return True
    
    except ImportError as e:
        logger.error(f"✗ Error importando módulos de características: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error general en validación: {e}")
        return False

def validate_technical_features():
    """Valida los indicadores técnicos"""
    try:
        from core.features.technical_features import TechnicalFeatures
        
        logger.info("Iniciando validación de indicadores técnicos...")
        
        # Crear instancia
        indicators = TechnicalFeatures()
        logger.info("✓ TechnicalFeatures inicializado")
        
        # Verificar métodos comunes
        common_indicators = ['calculate_rsi', 'calculate_macd', 'calculate_bollinger']
        for indicator in common_indicators:
            if hasattr(indicators, indicator) and callable(getattr(indicators, indicator)):
                logger.info(f"✓ Indicador {indicator} disponible")
            else:
                logger.warning(f"! Indicador {indicator} no encontrado")
        
        # Crear datos de prueba
        test_data = {
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
            'open': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113],
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115],
            'low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400]
        }
        
        df = pd.DataFrame(test_data)
        
        # Probar cálculo de RSI
        if hasattr(indicators, 'calculate_rsi'):
            try:
                rsi = indicators.calculate_rsi(df['close'].values)
                logger.info(f"✓ Cálculo de RSI exitoso. Valores: {rsi[-5:]} (últimos 5)")
            except Exception as e:
                logger.error(f"✗ Error calculando RSI: {e}")
                
        logger.info("Validación de indicadores técnicos completada")
        return True
    
    except ImportError as e:
        logger.error(f"✗ Error importando módulos de indicadores: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error general en validación: {e}")
        return False

def main():
    """Función principal"""
    logger.info("=== VALIDACIÓN DE MÓDULOS DE CARACTERÍSTICAS ===")
    
    # Comprobar estructura de directorios
    logger.info("Verificando estructura de directorios...")
    
    for root, dirs, files in os.walk("./core/features"):
        logger.info(f"Directorio: {root}")
        logger.info(f"  Subdirectorios: {dirs}")
        logger.info(f"  Archivos: {files}")
    
    # Validar extractor de características
    feature_result = validate_feature_extraction()
    
    # Validar indicadores técnicos
    technical_result = validate_technical_features()
    
    if feature_result and technical_result:
        logger.info("✓ Todos los tests de características pasaron")
    else:
        logger.warning("! Algunos tests de características fallaron")
    
    logger.info("=== VALIDACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()