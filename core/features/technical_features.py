# Indicadores técnicos

import numpy as np
import pandas as pd

def calculate_sma(data, window):
    """Calcula la Media Móvil Simple (SMA)."""
    return data.rolling(window=window).mean()

def calculate_ema(data, window):
    """Calcula la Media Móvil Exponencial (EMA)."""
    return data.ewm(span=window, adjust=False).mean()

def calculate_rsi(data, window):
    """Calcula el Índice de Fuerza Relativa (RSI)."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

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

def calculate_bollinger_bands(data, window, num_std_dev):
    """Calcula las Bandas de Bollinger."""
    sma = calculate_sma(data, window)
    std_dev = data.rolling(window=window).std()
    upper_band = sma + (std_dev * num_std_dev)
    lower_band = sma - (std_dev * num_std_dev)
    return upper_band, sma, lower_band

def calculate_atr(high, low, close, window):
    """Calcula el Rango Verdadero Promedio (ATR)."""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=window).mean()

def calculate_obv(close, volume):
    """Calcula el On-Balance Volume (OBV)."""
    direction = np.sign(close.diff())
    obv = (volume * direction).fillna(0).cumsum()
    return obv

def detect_candlestick_patterns(data):
    """Detecta patrones de velas como Doji, Hammer y Engulfing."""
    patterns = {}
    body = abs(data['close'] - data['open'])
    upper_shadow = data['high'] - data[['close', 'open']].max(axis=1)
    lower_shadow = data[['close', 'open']].min(axis=1) - data['low']
    
    patterns['doji'] = (body / (data['high'] - data['low'])) < 0.1
    patterns['hammer'] = (lower_shadow > 2 * body) & (upper_shadow < body)
    patterns['engulfing'] = ((data['close'] > data['open']) & 
                             (data['close'].shift(1) < data['open'].shift(1)) &
                             (data['close'] > data['open'].shift(1)) &
                             (data['open'] < data['close'].shift(1)))
    return patterns

def extract_technical_features(data, timeframes):
    """Extrae indicadores técnicos para múltiples marcos temporales."""
    features = {}
    for timeframe in timeframes:
        resampled_data = data.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        features[timeframe] = {
            'sma_20': calculate_sma(resampled_data['close'], 20),
            'rsi_14': calculate_rsi(resampled_data['close'], 14),
            'macd': calculate_macd(resampled_data['close'], 12, 26, 9),
            'bollinger_bands': calculate_bollinger_bands(resampled_data['close'], 20, 2),
            'atr_14': calculate_atr(resampled_data['high'], resampled_data['low'], resampled_data['close'], 14),
            'obv': calculate_obv(resampled_data['close'], resampled_data['volume']),
            'candlestick_patterns': detect_candlestick_patterns(resampled_data)
        }
    return features

class TechnicalFeatures:
    """Clase para calcular indicadores técnicos."""

    def __init__(self):
        """
        Inicializa el módulo de características técnicas.
        """
        pass

    def calculate_rsi(self, prices, window=14):
        """
        Calcula el RSI (Relative Strength Index).

        :param prices: Serie de precios.
        :param window: Ventana para el cálculo del RSI.
        :return: Serie con los valores de RSI.
        """
        if len(prices) < window:
            return np.array([np.nan] * len(prices))

        # Calcular cambios en los precios
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        # Calcular promedios móviles exponenciales
        avg_gain = np.convolve(gains, np.ones(window), 'valid') / window
        avg_loss = np.convolve(losses, np.ones(window), 'valid') / window

        # Evitar divisiones por cero
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        # Rellenar con NaN para mantener el tamaño original
        rsi = np.concatenate((np.array([np.nan] * (window - 1)), rsi))
        return rsi

    def calculate_bollinger(self, prices, window=20, num_std=2):
        """
        Calcula las bandas de Bollinger.

        :param prices: Serie de precios.
        :param window: Ventana para el cálculo de la media móvil.
        :param num_std: Número de desviaciones estándar para las bandas.
        :return: Bandas superior, media y inferior.
        """
        if len(prices) < window:
            return (
                np.array([np.nan] * len(prices)),
                np.array([np.nan] * len(prices)),
                np.array([np.nan] * len(prices)),
            )

        # Calcular la media móvil
        middle_band = np.array([
            np.mean(prices[i - window:i]) if i >= window else np.nan
            for i in range(1, len(prices) + 1)
        ])

        # Calcular la desviación estándar
        std = np.array([
            np.std(prices[i - window:i]) if i >= window else np.nan
            for i in range(1, len(prices) + 1)
        ])

        # Calcular bandas superior e inferior
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)

        return upper_band, middle_band, lower_band

    def calculate_macd(self, prices, fast_window=12, slow_window=26, signal_window=9):
        """
        Calcula el indicador MACD
        
        Args:
            prices: Precios de cierre (array, Series o lista)
            fast_window (int): Período para EMA rápida (default=12)
            slow_window (int): Período para EMA lenta (default=26)
            signal_window (int): Período para la línea de señal (default=9)
            
        Returns:
            tuple: (macd_line, signal_line)
        """
        try:
            # Convertir a series de pandas si no lo es
            if not isinstance(prices, pd.Series):
                if isinstance(prices, np.ndarray):
                    prices = pd.Series(prices)
                elif isinstance(prices, list):
                    prices = pd.Series(prices)
                    
            # Calcular EMAs
            fast_ema = prices.ewm(span=fast_window, adjust=False).mean()
            slow_ema = prices.ewm(span=slow_window, adjust=False).mean()
            
            # Calcular línea MACD y señal
            macd_line = fast_ema - slow_ema
            signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
            
            return macd_line, signal_line
            
        except Exception as e:
            print(f"Error calculando MACD: {e}")
            # Retornar valores neutrales en caso de error
            if isinstance(prices, pd.Series):
                zeros = pd.Series([0] * len(prices), index=prices.index)
                return zeros, zeros
            else:
                zeros = np.zeros(len(prices))
                return zeros, zeros

    @staticmethod
    def calculate_sma(data, window):
        """Calcula la Media Móvil Simple (SMA)."""
        return calculate_sma(data, window)

    @staticmethod
    def calculate_ema(data, window):
        """Calcula la Media Móvil Exponencial (EMA)."""
        return calculate_ema(data, window)

    @staticmethod
    def calculate_rsi_static(data, window):
        """Calcula el Índice de Fuerza Relativa (RSI)."""
        return calculate_rsi(data, window)

    @staticmethod
    def calculate_macd(data, fast_window, slow_window, signal_window):
        """
        Calcula el MACD y la señal.
        
        Args:
            data: Serie de precios de cierre.
            fast_window: Período para EMA rápida.
            slow_window: Período para EMA lenta.
            signal_window: Período para la línea de señal.
            
        Returns:
            tuple: (macd_line, signal_line)
        """
        # Llamar a la función global pero descartar el tercer valor (histograma)
        macd, signal, _ = calculate_macd(data, fast_window, slow_window, signal_window)
        return macd, signal

    @staticmethod
    def calculate_bollinger_bands(data, window, num_std_dev):
        """Calcula las Bandas de Bollinger."""
        return calculate_bollinger_bands(data, window, num_std_dev)

    @staticmethod
    def calculate_atr(high, low, close, window):
        """Calcula el Rango Verdadero Promedio (ATR)."""
        return calculate_atr(high, low, close, window)

    @staticmethod
    def calculate_obv(close, volume):
        """Calcula el On-Balance Volume (OBV)."""
        return calculate_obv(close, volume)

    @staticmethod
    def detect_candlestick_patterns(data):
        """Detecta patrones de velas como Doji, Hammer y Engulfing."""
        return detect_candlestick_patterns(data)

    @staticmethod
    def extract_technical_features(data, timeframes):
        """Extrae indicadores técnicos para múltiples marcos temporales."""
        return extract_technical_features(data, timeframes)
