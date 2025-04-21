# Gestión de riesgo básica

import threading
import numpy as np

class RiskManager:
    def __init__(self, account_balance=10000.0):
        """
        Inicializa el gestor de riesgos.

        :param account_balance: Saldo de la cuenta (por defecto: 10000.0).
        """
        self.account_balance = account_balance
        self.max_risk_per_trade = 0.02  # Ejemplo: 2% del saldo por operación

    def calculate_position_size(self, stop_loss, entry_price):
        """
        Calcula el tamaño de la posición basado en el riesgo permitido.

        :param stop_loss: Precio de stop loss.
        :param entry_price: Precio de entrada.
        :return: Tamaño de la posición.
        """
        risk_amount = self.account_balance * self.max_risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss)
        position_size = risk_amount / risk_per_unit if risk_per_unit > 0 else 0

        return position_size

    def validate_signal(self, signal):
        """
        Valida si una señal cumple con las reglas de riesgo.
        """
        if not isinstance(signal, dict):
            return False
        if 'confidence' not in signal:
            return False
        if signal['confidence'] < 0.6:  # Umbral mínimo de confianza
            return False
        return True

    def get_position_limit(self, symbol):
        """
        Obtiene el límite de posición para un símbolo.
        """
        if symbol == 'BTC/USDT':
            return self.account_balance * 0.1
        return self.account_balance * 0.05

    def calculate_stop_loss(self, symbol, entry_price, action):
        """
        Calcula el nivel de stop loss para una operación.
        """
        if action == 'BUY':
            return entry_price * 0.95
        elif action == 'SELL':
            return entry_price * 1.05
        return entry_price  # En caso de acción desconocida
