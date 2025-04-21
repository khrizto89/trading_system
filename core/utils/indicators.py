# Biblioteca de indicadores técnicos

import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def sma(data, window):
        """Simple Moving Average (SMA)"""
        return data['close'].rolling(window=window).mean()

    @staticmethod
    def ema(data, window):
        """Exponential Moving Average (EMA)"""
        return data['close'].ewm(span=window, adjust=False).mean()

    @staticmethod
    def wma(data, window):
        """Weighted Moving Average (WMA)"""
        weights = np.arange(1, window + 1)
        return data['close'].rolling(window=window).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

    @staticmethod
    def rsi(data, window=14):
        """Relative Strength Index (RSI)"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(data, fast=12, slow=26, signal=9):
        """Moving Average Convergence Divergence (MACD)"""
        ema_fast = Indicators.ema(data, fast)
        ema_slow = Indicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, signal_line

    @staticmethod
    def bollinger_bands(data, window=20, num_std=2):
        """Bollinger Bands"""
        sma = Indicators.sma(data, window)
        std = data['close'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        return upper_band, lower_band

    @staticmethod
    def atr(data, window=14):
        """Average True Range (ATR)"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=window).mean()

    @staticmethod
    def obv(data):
        """On-Balance Volume (OBV)"""
        direction = np.sign(data['close'].diff())
        return (direction * data['volume']).fillna(0).cumsum()

    @staticmethod
    def money_flow_index(data, window=14):
        """Money Flow Index (MFI)"""
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        money_flow = typical_price * data['volume']
        positive_flow = money_flow.where(typical_price > typical_price.shift(), 0).rolling(window=window).sum()
        negative_flow = money_flow.where(typical_price < typical_price.shift(), 0).rolling(window=window).sum()
        mfi = 100 - (100 / (1 + (positive_flow / negative_flow)))
        return mfi

    @staticmethod
    def roc(data, window=10):
        """Rate of Change (ROC)"""
        return data['close'].pct_change(periods=window) * 100

    @staticmethod
    def tsi(data, long=25, short=13):
        """True Strength Index (TSI)"""
        momentum = data['close'].diff()
        abs_momentum = momentum.abs()
        ema_long = momentum.ewm(span=long, adjust=False).mean()
        ema_abs_long = abs_momentum.ewm(span=long, adjust=False).mean()
        ema_short = ema_long.ewm(span=short, adjust=False).mean()
        ema_abs_short = ema_abs_long.ewm(span=short, adjust=False).mean()
        return (ema_short / ema_abs_short) * 100

    @staticmethod
    def detect_candlestick_patterns(data):
        """Detect common candlestick patterns"""
        patterns = {}
        patterns['doji'] = (abs(data['open'] - data['close']) <= (data['high'] - data['low']) * 0.1)
        patterns['hammer'] = ((data['close'] > data['open']) & 
                              ((data['low'] - data['open']) > 2 * (data['close'] - data['open'])) &
                              ((data['high'] - data['close']) < (data['close'] - data['open'])))
        patterns['engulfing'] = ((data['close'] > data['open']) & 
                                 (data['close'].shift() < data['open'].shift()) &
                                 (data['close'] > data['open'].shift()) &
                                 (data['open'] < data['close'].shift()))
        return pd.DataFrame(patterns)

    @staticmethod
    def ichimoku(data):
        """Ichimoku Cloud"""
        nine_period_high = data['high'].rolling(window=9).max()
        nine_period_low = data['low'].rolling(window=9).min()
        conversion_line = (nine_period_high + nine_period_low) / 2

        twenty_six_period_high = data['high'].rolling(window=26).max()
        twenty_six_period_low = data['low'].rolling(window=26).min()
        base_line = (twenty_six_period_high + twenty_six_period_low) / 2

        leading_span_a = ((conversion_line + base_line) / 2).shift(26)
        leading_span_b = ((data['high'].rolling(window=52).max() + data['low'].rolling(window=52).min()) / 2).shift(26)

        return conversion_line, base_line, leading_span_a, leading_span_b

    @staticmethod
    def normalize(data):
        """Normalize data to range [0, 1]"""
        return (data - data.min()) / (data.max() - data.min())

    @staticmethod
    def standardize(data):
        """Standardize data to mean 0 and std 1"""
        return (data - data.mean()) / data.std()
