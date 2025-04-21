# system_diagnostics.py
import logging
import importlib
import pandas as pd
import numpy as np
import os

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SystemDiagnostics')

def check_component(module_path, class_name, *args, **kwargs):
    """Verifica si un componente puede ser importado e inicializado"""
    print(f"\n=== Verificando {class_name} ===")
    try:
        module = importlib.import_module(module_path)
        print(f"✓ Módulo {module_path} importado correctamente")
        
        # Verificar si la clase existe
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            print(f"✓ Clase {class_name} encontrada")
            
            # Intentar instanciar la clase
            try:
                instance = cls(*args, **kwargs)
                print(f"✓ {class_name} inicializado correctamente")
                return instance
            except Exception as e:
                print(f"✗ Error al inicializar {class_name}: {str(e)}")
                print(f"  Argumentos esperados: {cls.__init__.__code__.co_varnames}")
                return None
        else:
            print(f"✗ Clase {class_name} no encontrada en {module_path}")
            return None
    except Exception as e:
        print(f"✗ Error al importar {module_path}: {str(e)}")
        return None

def test_model_prediction(model_manager):
    """Prueba la funcionalidad de predicción del ModelManager"""
    if not model_manager:
        return
        
    print("\n=== Prueba de predicción ===")
    try:
        # Generar datos de prueba
        sample_data = np.random.random((1, 10))
        prediction = model_manager.predict(sample_data)
        print(f"✓ Predicción exitosa: {prediction}")
        return prediction
    except Exception as e:
        print(f"✗ Error en predicción: {str(e)}")
        return None

def test_feature_extraction(feature_extractor):
    """Prueba la extracción de características"""
    if not feature_extractor:
        return
        
    print("\n=== Prueba de extracción de características ===")
    try:
        # Crear datos de mercado de prueba
        dates = pd.date_range(start='2025-04-01', periods=5)
        market_data = pd.DataFrame({
            'close': [42000, 42100, 42050, 42200, 42300],
            'open': [41900, 42000, 42100, 42050, 42200],
            'high': [42100, 42200, 42150, 42250, 42350],
            'low': [41850, 41950, 42000, 42000, 42150],
            'volume': [100, 150, 120, 110, 130]
        }, index=dates)
        
        features = feature_extractor.extract_features(market_data)
        print(f"✓ Extracción exitosa, se obtuvieron {len(features.columns) if hasattr(features, 'columns') else len(features)} características")
        return features
    except Exception as e:
        print(f"✗ Error en extracción: {str(e)}")
        return None

def test_signal_generation(signal_generator, prediction=0.75):
    """Prueba la generación de señales"""
    if not signal_generator:
        return
        
    print("\n=== Prueba de generación de señales ===")
    try:
        # Intentar generar una señal
        if hasattr(signal_generator, 'generate_signal_for_symbol'):
            signal = signal_generator.generate_signal_for_symbol('BTCUSDT', prediction)
        else:
            signal = signal_generator.generate_signal(prediction)
            
        print(f"✓ Generación de señal exitosa: {signal}")
        return signal
    except Exception as e:
        print(f"✗ Error en generación de señal: {str(e)}")
        return None

def check_directories():
    """Verifica la estructura de directorios del proyecto"""
    print("\n=== Verificando estructura de directorios ===")
    expected_dirs = [
        'core/models',
        'core/features',
        'core/strategy',
        'core/utils',
        'traders/btc_trader',
        'traders/eth_trader',
        'services/data_service',
        'services/monitor_service',
        'services/api_service'
    ]
    
    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            print(f"✓ Directorio {dir_path} existe")
        else:
            print(f"✗ Directorio {dir_path} no existe")

def check_files():
    """Verifica archivos críticos del sistema"""
    print("\n=== Verificando archivos críticos ===")
    critical_files = [
        'main.py',
        'config.json',
        'core/models/model_manager.py',
        'core/features/feature_extractor.py',
        'core/strategy/signal_generator.py'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✓ Archivo {file_path} existe")
        else:
            print(f"✗ Archivo {file_path} no existe")

def main():
    print("=== DIAGNÓSTICO COMPLETO DEL SISTEMA DE TRADING ===")
    
    # Verificar estructura básica
    check_directories()
    check_files()
    
    # Verificar componentes
    model_manager = check_component('core.models.model_manager', 'ModelManager', logger)
    feature_extractor = check_component('core.features.feature_extractor', 'FeatureExtractor', logger)
    
    # Intentar cargar TechnicalIndicators
    indicators = check_component('core.utils.indicators', 'TechnicalIndicators', logger)
    
    # Verificar SignalGenerator (con las dependencias necesarias)
    signal_generator = None
    if model_manager and indicators:
        signal_generator = check_component('core.strategy.signal_generator', 'SignalGenerator', model_manager, indicators)
    
    # Probar funcionamiento
    features = test_feature_extraction(feature_extractor)
    prediction = test_model_prediction(model_manager)
    if prediction:
        signal = test_signal_generation(signal_generator, prediction)
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")
    print("Nota: Resuelve los errores marcados con ✗ antes de continuar.")

if __name__ == "__main__":
    main()