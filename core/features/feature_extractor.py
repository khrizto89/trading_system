# Coordinador de extracción de características

import pandas as pd
from sklearn.decomposition import PCA
from .market_features import MarketFeatures
from .technical_features import TechnicalFeatures

class FeatureExtractor:
    def __init__(self, n_components=None):
        """
        Inicializa el extractor de características.
        :param n_components: Número de componentes para reducción dimensional (PCA).
        """
        self.market_features = MarketFeatures()
        self.technical_features = TechnicalFeatures()
        self.pca = PCA(n_components=n_components) if n_components else None

    def preprocess_data(self, data):
        """
        Preprocesa los datos antes de la extracción de características.
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            data = data.copy()
            data.index = pd.date_range(start='2023-01-01', periods=len(data), freq='H')
        return data

    def extract_features(self, data, timeframe='1h'):
        """
        Extrae y combina características de mercado y técnicas.
        """
        # Preprocesar los datos
        data = self.preprocess_data(data)

        # Extraer características de mercado
        market_features = self.market_features.calculate(data)

        # Extraer características técnicas
        technical_features = {
            'rsi': self.technical_features.calculate_rsi(data['close']),
            'bollinger_upper': self.technical_features.calculate_bollinger(data['close'])[0],
            'bollinger_lower': self.technical_features.calculate_bollinger(data['close'])[2],
        }

        # Combinar características
        features = pd.concat([market_features, pd.DataFrame(technical_features, index=data.index)], axis=1)

        # Aplicar PCA si está configurado
        if self.pca:
            features = pd.DataFrame(self.pca.fit_transform(features), index=data.index)

        return features
