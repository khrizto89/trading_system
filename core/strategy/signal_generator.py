# Archivo: core/strategy/signal_generator.py

import logging
import pandas as pd
import numpy as np
import traceback

logger = logging.getLogger(__name__)

class SignalGenerator:
    def __init__(self, config, models_manager=None, technical_features=None):
        self.config = config
        self.models_manager = models_manager
        self.technical_features = technical_features
        
    def generate_signal(self, symbol, market_data):
        """
        Genera señal de trading basada en datos de mercado y modelos
        
        Args:
            symbol (str): Símbolo para el que se genera la señal
            market_data (dict): Datos de mercado actualizados
            
        Returns:
            dict: Señal con acción, confianza y timestamp
        """
        logger.debug(f"Generando señal con datos: {symbol, market_data}")
        
        try:
            # Valores por defecto
            action = "HOLD"
            confidence = 0.5
            
            # Si no hay modelo o datos, retornamos HOLD
            if not market_data or not self.models_manager:
                return self._create_signal_dict(symbol, action, confidence)
                
            # Verificamos si hay suficientes datos
            if not market_data.get(symbol, {}):
                logger.warning(f"No hay datos disponibles para {symbol}")
                return self._create_signal_dict(symbol, action, confidence)
                
            # Preparar datos de mercado (añadir datos faltantes si es necesario)
            prepared_data = {symbol: self._prepare_market_data(symbol, market_data)}
            
            # Extraer features con los datos preparados
            features = self._extract_features(symbol, prepared_data)
            if not features:
                logger.warning(f"No se pudieron extraer características para {symbol}")
                return self._create_signal_dict(symbol, action, confidence)
                
            # Obtener predicción de modelos
            prediction = self.models_manager.predict(symbol, features)
            
            # Convertir predicción a señal
            action, confidence = self._prediction_to_signal(prediction, prepared_data[symbol])
            
            # Crear y retornar la señal
            return self._create_signal_dict(symbol, action, confidence)
            
        except Exception as e:
            logger.error(f"Error generando señal para {symbol}: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            # En caso de error, retornamos HOLD por seguridad
            return self._create_signal_dict(symbol, "HOLD", 0.5)
    
    def _prepare_market_data(self, symbol, market_data):
        """
        Prepara los datos de mercado, generando datos sintéticos si es necesario
        
        Args:
            symbol (str): Símbolo de trading
            market_data (dict): Datos de mercado originales
            
        Returns:
            dict: Datos de mercado preparados con todos los campos necesarios
        """
        logger.debug(f"Preparando datos de mercado para {symbol}")
        
        # Verificar si el símbolo existe en los datos
        if symbol not in market_data:
            logger.warning(f"Símbolo {symbol} no encontrado en los datos de mercado")
            return self._create_default_market_data(symbol)
        
        # Crear una copia para no modificar los originales
        data = market_data[symbol].copy() if isinstance(market_data[symbol], dict) else {'price': 50000, 'volume': 100}
        
        # Asegurarse de que existen los campos básicos
        if 'price' not in data:
            logger.warning(f"Campo 'price' no encontrado para {symbol}, usando valor predeterminado")
            data['price'] = 50000 if 'BTC' in symbol else 1500
            
        if 'volume' not in data:
            logger.warning(f"Campo 'volume' no encontrado para {symbol}, usando valor predeterminado")
            data['volume'] = 100
        
        # Si no hay datos históricos (close), crear sintéticos
        if 'close' not in data:
            logger.info(f"Generando datos históricos sintéticos para {symbol}")
            current_price = data['price']
            
            # Crear una pequeña serie temporal basada en el precio actual
            # con una ligera tendencia alcista
            prices = [
                current_price * 0.97,
                current_price * 0.98,
                current_price * 0.99,
                current_price,
                current_price * 1.01
            ]
            
            # Crear serie de pandas
            from datetime import datetime, timedelta
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=5)
            dates = pd.date_range(start=start_time, end=end_time, periods=5)
            
            data['close'] = pd.Series(prices, index=dates)
            logger.debug(f"Serie temporal sintética creada para {symbol}: {data['close']}")
        
        return data
    
    def _create_default_market_data(self, symbol):
        """Crea datos de mercado predeterminados para un símbolo"""
        # Asignar precio base según el símbolo
        base_price = 50000 if 'BTC' in symbol else 1500
        
        # Crear serie temporal sintética
        from datetime import datetime, timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=5)
        dates = pd.date_range(start=start_time, end=end_time, periods=5)
        
        prices = [
            base_price * 0.97,
            base_price * 0.98,
            base_price * 0.99,
            base_price,
            base_price * 1.01
        ]
        
        # Crear estructura completa
        return {
            'price': base_price,
            'volume': 100,
            'close': pd.Series(prices, index=dates)
        }
            
    def _extract_features(self, symbol, market_data):
        """Extrae características para alimentar los modelos"""
        if not self.technical_features:
            return {'price': market_data[symbol]['price'], 'volume': market_data[symbol]['volume']}
            
        try:
            # Obtener datos básicos
            current_price = market_data[symbol]['price']
            current_volume = market_data[symbol]['volume']
            close_prices = market_data[symbol]['close']
            
            logger.debug(f"Extrayendo características para {symbol} con {len(close_prices)} puntos de precio")
            
            # Calcular indicadores técnicos
            rsi = self.technical_features.calculate_rsi(close_prices)
            macd_line, signal_line = self.technical_features.calculate_macd(
                close_prices, 
                fast_window=12, 
                slow_window=26, 
                signal_window=9
            )
            upper, middle, lower = self.technical_features.calculate_bollinger_bands(
                close_prices,
                window=20,  # Valor estándar para las Bandas de Bollinger
                num_std_dev=2  # Valor estándar para las Bandas de Bollinger
            )
            
            # Crear formato de secuencia para modelos
            # Tomar los últimos 5 puntos (o menos si no hay suficientes)
            sequence_length = min(5, len(close_prices))
            
            # Convertir todo a listas para facilitar la creación de la secuencia
            rsi_list = [rsi[-i] if isinstance(rsi, (list, np.ndarray)) and i <= len(rsi) else 50 
                       for i in range(1, sequence_length+1)]
            
            macd_list = [macd_line[-i] if isinstance(macd_line, (pd.Series, list, np.ndarray)) and i <= len(macd_line) else 0 
                        for i in range(1, sequence_length+1)]
                        
            signal_list = [signal_line[-i] if isinstance(signal_line, (pd.Series, list, np.ndarray)) and i <= len(signal_line) else 0 
                          for i in range(1, sequence_length+1)]
                          
            upper_list = [upper[-i] if isinstance(upper, (list, np.ndarray)) and i <= len(upper) else current_price*1.02 
                         for i in range(1, sequence_length+1)]
                         
            middle_list = [middle[-i] if isinstance(middle, (list, np.ndarray)) and i <= len(middle) else current_price 
                          for i in range(1, sequence_length+1)]
                          
            lower_list = [lower[-i] if isinstance(lower, (list, np.ndarray)) and i <= len(lower) else current_price*0.98 
                         for i in range(1, sequence_length+1)]
            
            # Obtener precios y volúmenes reales o usar constantes
            price_list = [close_prices[-i] if i <= len(close_prices) else current_price 
                         for i in range(1, sequence_length+1)]
                         
            volume_list = [current_volume] * sequence_length
            
            # Crear secuencia
            sequence = []
            for i in range(sequence_length):
                sequence.append([
                    price_list[i],
                    volume_list[i],
                    rsi_list[i],
                    macd_list[i],
                    signal_list[i],
                    upper_list[i],
                    middle_list[i],
                    lower_list[i]
                ])
            
            # Crear diccionario de características
            features = {
                'price': current_price,
                'volume': current_volume,
                'rsi': rsi[-1] if isinstance(rsi, (list, np.ndarray)) and len(rsi) > 0 else 50,
                'macd': macd_list[0],
                'macd_signal': signal_list[0],
                'bb_upper': upper_list[0],
                'bb_middle': middle_list[0],
                'bb_lower': lower_list[0],
                'sequence': sequence
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extrayendo características: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            # En caso de error, devolver características mínimas
            return {
                'price': market_data[symbol]['price'],
                'volume': market_data[symbol]['volume'],
                'sequence': [[market_data[symbol]['price'], market_data[symbol]['volume'], 50, 0, 0, 0, 0, 0] for _ in range(5)]
            }
            
    def _prediction_to_signal(self, prediction, market_data):
        """Convierte una predicción a una señal de trading"""
        # Valores por defecto
        action = "HOLD"
        confidence = prediction.get('confidence', 0.5)
        
        # Obtener dirección y porcentaje de cambio predicho
        direction = prediction.get('direction', 0)
        price_change_pct = prediction.get('price_change_pct', 0.0)
        
        # Umbral para señales
        buy_threshold = self.config.get('strategy', {}).get('buy_threshold', 0.6)
        sell_threshold = self.config.get('strategy', {}).get('sell_threshold', 0.6)
        
        # Convertir predicción a señal
        if direction > 0 and confidence >= buy_threshold:
            action = "BUY"
        elif direction < 0 and confidence >= sell_threshold:
            action = "SELL"
        
        return action, confidence
        
    def _create_signal_dict(self, symbol, action, confidence):
        """Crea un diccionario con la señal de trading"""
        signal = {
            'symbol': symbol,
            'action': action,
            'confidence': confidence,
            'timestamp': pd.Timestamp.now()
        }
        
        logger.debug(f"Señal generada: {signal}")
        return signal