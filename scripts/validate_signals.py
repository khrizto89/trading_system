import logging
from core.strategy.signal_generator import SignalGenerator
from core.models.model_manager import ModelManager
from core.features.technical_features import Indicators  # Adjusted to match the correct class name

# Configurar logger
logger = logging.getLogger('Validation')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

try:
    # Crear dependencias necesarias
    models = ModelManager(logger)
    indicators = Indicators()  # Ajustar según la firma correcta
    
    # Inicializar SignalGenerator con las dependencias requeridas
    sg = SignalGenerator(models, indicators)
    
    # Simular predicciones del modelo
    sample_prediction = 0.75  # Valor entre 0 y 1
    
    # Verificar método de generación de señales
    try:
        signal = sg.generate_signal(sample_prediction)
        print(f"Predicción: {sample_prediction}")
        print(f"Señal generada: {signal}")
    except Exception as e:
        print(f"Error con generate_signal básico: {str(e)}")
        # Intentar con método alternativo
        try:
            signal = sg.generate_signal_for_symbol('BTCUSDT', sample_prediction)
            print(f"Señal para BTCUSDT: {signal}")
        except Exception as e:
            print(f"Error con generate_signal_for_symbol: {str(e)}")
    
except Exception as e:
    print(f"Error al generar señales: {str(e)}")
