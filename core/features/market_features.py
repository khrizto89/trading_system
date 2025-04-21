# Características de mercado

import pandas as pd
import numpy as np

class MarketFeatures:
    def calculate(self, data):
        """
        Calcula características de mercado a partir de los datos proporcionados.

        :param data: DataFrame con datos de mercado.
        :return: DataFrame con características calculadas.
        """
        features = pd.DataFrame()
        features['price_mean'] = (data['high'] + data['low']) / 2
        features['price_range'] = data['high'] - data['low']
        return features

    def extract(self, data):
        """
        Extract basic market features.
        :param data: Pandas DataFrame with OHLCV data.
        :return: DataFrame with extracted features.
        """
        features = pd.DataFrame(index=data.index)

        # Basic market features
        features['price'] = data['close']
        features['volume'] = data['volume']
        features['spread'] = data['high'] - data['low']

        # Volatility (e.g., rolling standard deviation of returns)
        features['volatility'] = data['close'].pct_change().rolling(window=14).std()

        # Momentum (e.g., price change over a window)
        features['momentum'] = data['close'].diff(3)

        # Liquidity metrics (e.g., volume over spread)
        features['liquidity'] = data['volume'] / features['spread'].replace(0, np.nan)

        # Seasonal and periodic features
        features['hour_of_day'] = data.index.hour
        features['day_of_week'] = data.index.dayofweek

        return features

    def analyze_order_book(self, order_book):
        """
        Analyze market depth and order book.
        :param order_book: Dictionary with 'bids' and 'asks' (price, volume).
        :return: Dictionary with order book metrics.
        """
        bids = np.array(order_book['bids'])
        asks = np.array(order_book['asks'])

        # Calculate bid-ask spread
        spread = asks[0, 0] - bids[0, 0]

        # Calculate market depth
        depth_bids = np.sum(bids[:, 1])
        depth_asks = np.sum(asks[:, 1])

        return {
            'spread': spread,
            'depth_bids': depth_bids,
            'depth_asks': depth_asks
        }

    def calculate_correlation(self, data, other_assets):
        """
        Calculate correlations with other assets.
        :param data: Pandas DataFrame with OHLCV data for the main asset.
        :param other_assets: Dictionary of DataFrames with OHLCV data for other assets.
        :return: Series with correlation values.
        """
        correlations = {}
        for asset, asset_data in other_assets.items():
            correlations[asset] = data['close'].pct_change().corr(asset_data['close'].pct_change())
        return pd.Series(correlations)

    def calculate_dominance(self, data, total_market_cap):
        """
        Calculate market dominance.
        :param data: Pandas DataFrame with market cap data for the asset.
        :param total_market_cap: Total market capitalization of all assets.
        :return: Series with dominance values.
        """
        return data['market_cap'] / total_market_cap

    def calculate_on_chain_metrics(self, on_chain_data):
        """
        Calculate on-chain metrics for cryptocurrencies.
        :param on_chain_data: DataFrame with on-chain metrics (e.g., active addresses, transaction volume).
        :return: DataFrame with processed on-chain metrics.
        """
        metrics = pd.DataFrame(index=on_chain_data.index)

        # Example: Normalize active addresses and transaction volume
        metrics['active_addresses'] = on_chain_data['active_addresses'] / on_chain_data['active_addresses'].max()
        metrics['transaction_volume'] = on_chain_data['transaction_volume'] / on_chain_data['transaction_volume'].max()

        return metrics
