# Notificaciones (Telegram)

import logging
import time
from threading import Lock
import requests
from datetime import datetime

class NotificationService:
    def __init__(self, token="", chat_id="", enabled=False):
        """
        Inicializa el servicio de notificaciones.
        
        Args:
            token: Token de autenticación para el servicio (e.g., Telegram).
            chat_id: ID del chat para enviar notificaciones.
            enabled: Si es True, habilita el envío de notificaciones.
        """
        self.token = token
        self.chat_id = chat_id
        self.enabled = enabled

        # Inicialización si es necesario
        if self.enabled:
            self._init_telegram()

    def _init_telegram(self):
        # Inicialización de Telegram si es necesario
        pass

    def send_message(self, message):
        """
        Envía un mensaje de notificación.
        
        Args:
            message: Mensaje a enviar.
        """
        if not self.enabled:
            return
        
        # Implementación de ejemplo para Telegram
        if self.token and self.chat_id:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": message}
            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
            except Exception as e:
                print(f"Error enviando notificación: {e}")

    def send_trade_notification(self, trader_name, symbol, action, price, amount=None, pnl=None):
        """
        Envía notificación sobre una operación de trading
        
        Args:
            trader_name (str): Nombre del trader
            symbol (str): Símbolo/par de trading
            action (str): Acción realizada (BUY, SELL, HOLD)
            price (float): Precio de la operación
            amount (float, optional): Cantidad operada
            pnl (float, optional): Profit and Loss si aplica
        """
        if not self.enabled:
            return
            
        message = f"🤖 {trader_name} - {action} {symbol}\n"
        message += f"💲 Precio: {price:.2f}\n"
        
        if amount is not None:
            message += f"📊 Cantidad: {amount:.6f}\n"
            
        if pnl is not None:
            emoji = "🟢" if pnl >= 0 else "🔴"
            message += f"{emoji} PnL: {pnl:.2f}%\n"
            
        message += f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_telegram_message(message)
        
    def _send_telegram_message(self, message):
        """Envía mensaje a través de Telegram"""
        if not self.enabled:
            return
            
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Error enviando notificación Telegram: {e}")
