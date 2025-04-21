import logging
from core.models.model_manager import ModelManager
import numpy as np

# Configurar un logger básico
logger = logging.getLogger('Validation')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

try:
    # Inicializar ModelManager con el logger requerido
    mm = ModelManager(logger)
    print("Estado de los modelos:")
    
    # Verificar métodos disponibles
    if hasattr(mm, 'get_models_status'):
        print(f"- Estado de los modelos: {mm.get_models_status()}")
    elif hasattr(mm, 'get_loaded_models'):
        print(f"- Modelos cargados: {mm.get_loaded_models()}")
    else:
        print("- Información de modelos no disponible directamente")
    
    # Intentar hacer una predicción simple
    try:
        # Datos de muestra (ajustar según lo esperado por tu modelo)
        sample_data = np.random.random((1, 10))
        prediction = mm.predict(sample_data)
        print(f"- Predicción de prueba: {prediction}")
    except Exception as e:
        print(f"- No se pudo realizar predicción: {str(e)}")
except Exception as e:
    print(f"Error al verificar modelos: {str(e)}")
