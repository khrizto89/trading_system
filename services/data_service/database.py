# Almacenamiento de datos
import sqlite3
from contextlib import closing
import os
import pandas as pd
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path="trading_system.db"):
        """
        Initialize the database.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """
        Create necessary tables if they do not exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Table for historical market data (OHLCV)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    UNIQUE(symbol, timestamp)
                )
            """)
            # Table for trade logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trade_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    pnl REAL,
                    timestamp DATETIME NOT NULL
                )
            """)
            # Table for signals
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    signal INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    stop_loss REAL,
                    take_profit REAL,
                    timestamp DATETIME NOT NULL
                )
            """)
            # Table for model states
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    state BLOB NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            """)
            # Table for configurations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_name TEXT NOT NULL,
                    config_data TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            """)

    def store_market_data(self, symbol, data):
        """
        Store historical market data (OHLCV).
        :param symbol: Trading pair (e.g., BTCUSDT).
        :param data: Pandas DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume'].
        """
        with sqlite3.connect(self.db_path) as conn:
            data['symbol'] = symbol
            data.to_sql('market_data', conn, if_exists='append', index=False)

    def fetch_market_data(self, symbol, start_time, end_time):
        """
        Fetch historical market data for a given symbol and time range.
        :param symbol: Trading pair (e.g., BTCUSDT).
        :param start_time: Start time as a datetime object.
        :param end_time: End time as a datetime object.
        :return: Pandas DataFrame with market data.
        """
        query = """
            SELECT timestamp, open, high, low, close, volume
            FROM market_data
            WHERE symbol = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=(symbol, start_time, end_time))

    def log_trade(self, symbol, side, quantity, price, pnl, timestamp=None):
        """
        Log a trade.
        :param symbol: Trading pair (e.g., BTCUSDT).
        :param side: Trade side ('BUY' or 'SELL').
        :param quantity: Quantity traded.
        :param price: Trade price.
        :param pnl: Profit or loss from the trade.
        :param timestamp: Timestamp of the trade (default: current time).
        """
        timestamp = timestamp or datetime.utcnow()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO trade_logs (symbol, side, quantity, price, pnl, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (symbol, side, quantity, price, pnl, timestamp))

    def store_signal(self, symbol, signal, confidence, stop_loss, take_profit, timestamp=None):
        """
        Store a trading signal.
        :param symbol: Trading pair (e.g., BTCUSDT).
        :param signal: Signal (-1: Sell, 0: Hold, 1: Buy).
        :param confidence: Confidence level of the signal.
        :param stop_loss: Stop-loss price.
        :param take_profit: Take-profit price.
        :param timestamp: Timestamp of the signal (default: current time).
        """
        timestamp = timestamp or datetime.utcnow()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO signals (symbol, signal, confidence, stop_loss, take_profit, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (symbol, signal, confidence, stop_loss, take_profit, timestamp))

    def save_model_state(self, model_name, state, timestamp=None):
        """
        Save the state of a model.
        :param model_name: Name of the model.
        :param state: Serialized model state (e.g., using pickle or torch.save).
        :param timestamp: Timestamp of the state (default: current time).
        """
        timestamp = timestamp or datetime.utcnow()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO model_states (model_name, state, timestamp)
                VALUES (?, ?, ?)
            """, (model_name, state, timestamp))

    def load_model_state(self, model_name):
        """
        Load the most recent state of a model.
        :param model_name: Name of the model.
        :return: Serialized model state.
        """
        query = """
            SELECT state
            FROM model_states
            WHERE model_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(query, (model_name,)).fetchone()
            return result[0] if result else None

    def save_configuration(self, config_name, config_data, timestamp=None):
        """
        Save a configuration.
        :param config_name: Name of the configuration.
        :param config_data: Configuration data as a JSON string.
        :param timestamp: Timestamp of the configuration (default: current time).
        """
        timestamp = timestamp or datetime.utcnow()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO configurations (config_name, config_data, timestamp)
                VALUES (?, ?, ?)
            """, (config_name, config_data, timestamp))

    def load_configuration(self, config_name):
        """
        Load the most recent configuration by name.
        :param config_name: Name of the configuration.
        :return: Configuration data as a JSON string.
        """
        query = """
            SELECT config_data
            FROM configurations
            WHERE config_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(query, (config_name,)).fetchone()
            return result[0] if result else None

    def apply_retention_policy(self, retention_days=365):
        """
        Apply a retention policy to delete old market data.
        :param retention_days: Number of days to retain data.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM market_data
                WHERE timestamp < ?
            """, (cutoff_date,))
