# Procesamiento de datos

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split

class DataProcessor:
    def __init__(self):
        self.scalers = {
            "standard": StandardScaler(),
            "minmax": MinMaxScaler(feature_range=(0, 1))
        }

    def preprocess_ohlcv(self, data):
        """
        Preprocess raw OHLCV data.
        :param data: Pandas DataFrame with OHLCV data.
        :return: Preprocessed DataFrame.
        """
        # Handle missing values
        data = data.fillna(method="ffill").fillna(method="bfill")

        # Add log returns
        data["log_return"] = np.log(data["close"] / data["close"].shift(1)).fillna(0)

        return data

    def normalize(self, data, columns):
        """
        Normalize specified columns using MinMaxScaler.
        :param data: Pandas DataFrame.
        :param columns: List of columns to normalize.
        :return: DataFrame with normalized columns.
        """
        data[columns] = self.scalers["minmax"].fit_transform(data[columns])
        return data

    def standardize(self, data, columns):
        """
        Standardize specified columns using StandardScaler.
        :param data: Pandas DataFrame.
        :param columns: List of columns to standardize.
        :return: DataFrame with standardized columns.
        """
        data[columns] = self.scalers["standard"].fit_transform(data[columns])
        return data

    def sliding_window(self, data, window_size, target_column):
        """
        Apply sliding window technique to prepare data for time series models.
        :param data: Pandas DataFrame.
        :param window_size: Size of the sliding window.
        :param target_column: Column to predict.
        :return: Tuple (X, y) with features and targets.
        """
        X, y = [], []
        for i in range(len(data) - window_size):
            X.append(data.iloc[i:i + window_size].values)
            y.append(data.iloc[i + window_size][target_column])
        return np.array(X), np.array(y)

    def augment_data(self, data, methods=["noise"]):
        """
        Apply data augmentation techniques.
        :param data: Pandas DataFrame.
        :param methods: List of augmentation methods (e.g., "noise").
        :return: Augmented DataFrame.
        """
        augmented_data = data.copy()
        if "noise" in methods:
            noise = np.random.normal(0, 0.001, data.shape)
            augmented_data += noise
        return augmented_data

    def split_data(self, data, test_size=0.2, val_size=0.1, random_state=42):
        """
        Split data into training, validation, and test sets.
        :param data: Pandas DataFrame.
        :param test_size: Fraction of data for testing.
        :param val_size: Fraction of training data for validation.
        :param random_state: Random seed for reproducibility.
        :return: Tuple (train, val, test) DataFrames.
        """
        train_data, test_data = train_test_split(data, test_size=test_size, random_state=random_state)
        train_data, val_data = train_test_split(train_data, test_size=val_size, random_state=random_state)
        return train_data, val_data, test_data

    def batch_process(self, data, batch_size):
        """
        Process data in batches to manage memory efficiently.
        :param data: Pandas DataFrame.
        :param batch_size: Size of each batch.
        :return: Generator yielding batches of data.
        """
        for i in range(0, len(data), batch_size):
            yield data.iloc[i:i + batch_size]

    def transform_for_inference(self, data, window_size):
        """
        Transform data in real-time for inference.
        :param data: Pandas DataFrame.
        :param window_size: Size of the sliding window.
        :return: Transformed data ready for inference.
        """
        return data.iloc[-window_size:].values.reshape(1, window_size, -1)
