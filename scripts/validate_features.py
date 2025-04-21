import logging
import pandas as pd
from datetime import datetime, timedelta
from core.features.feature_extractor import FeatureExtractor

# Configurar logger
logger = logging.getLogger('Validation')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

try:
    # Según el diagnóstico, FeatureExtractor necesita n_components
    fe = FeatureExtractor(n_components=5)  # Ajustar el valor según tu implementación
    
    # Crear DataFrame de prueba
    dates = [datetime.now() - timedelta(days=i) for i in range(5)]
    market_data = pd.DataFrame({
        'close': [42000, 42100, 42050, 42200, 42300],
        'open': [41900, 42000, 42100, 42050, 42200],
        'high': [42100, 42200, 42150, 42250, 42350],
        'low': [41850, 41950, 42000, 42000, 42150],
        'volume': [100, 150, 120, 110, 130]
    }, index=dates)
    
    print("DataFrame de entrada:")
    print(market_data.head())
    
    # Extraer características
    features = fe.extract_features(market_data)
    
    print("\nCaracterísticas extraídas:")
    if isinstance(features, pd.DataFrame):
        print(f"- Forma: {features.shape}")
        print(f"- Columnas: {features.columns.tolist()}")
        print(f"- Primeras 3 filas:\n{features.head(3)}")
    else:
        print(f"- Tipo de datos: {type(features)}")
        print(f"- Contenido: {features}")
        
except Exception as e:
    print(f"Error al extraer características: {str(e)}")
