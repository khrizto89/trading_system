import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TradeMode:
    """Clase base para los diferentes modos de operación"""
    def __init__(self, config):
        self.config = config
        
    def execute_trade(self, trader, signal):
        """Método base para ejecutar operación según señal"""
        raise NotImplementedError("Subclases deben implementar execute_trade")
        
    def get_market_data(self, data_service, symbol):
        """Obtiene datos de mercado para el símbolo"""
        raise NotImplementedError("Subclases deben implementar get_market_data")
        
class PaperTradeMode(TradeMode):
    """Modo de operación en papel (simulado)"""
    def __init__(self, config):
        super().__init__(config)
        self.positions = {}  # Registro de posiciones abiertas
        self.balance = config.get('paper_trading', {}).get('initial_balance', 10000.0)
        self.trade_history = []
        
        logger.info(f"Modo paper trading inicializado con balance: {self.balance:.2f} USD")
        
    def execute_trade(self, trader, signal):
        """Ejecuta una operación simulada"""
        symbol = signal['symbol']
        action = signal['action']
        
        if action == 'HOLD':
            logger.debug(f"[PAPER] Mantener posición en {symbol}")
            return
            
        try:
            # Obtener precio actual
            current_price = trader.get_current_price(symbol)
            
            # Definir parámetros
            position_size_pct = self.config.get('paper_trading', {}).get('position_size_pct', 20.0)
            fee_percentage = self.config.get('paper_trading', {}).get('fee_percentage', 0.1)
            
            # Verificar si tenemos posición abierta
            position = self.positions.get(symbol)
            
            if action == 'BUY' and position is None:
                # Calcular tamaño de posición
                position_size = (self.balance * position_size_pct / 100)
                position_amount = position_size / current_price
                commission = position_size * fee_percentage / 100
                
                # Verificar fondos suficientes
                if position_size + commission > self.balance:
                    logger.warning(f"[PAPER] Fondos insuficientes para BUY {symbol}: {self.balance:.2f} < {position_size + commission:.2f}")
                    return
                    
                # Abrir posición
                self.positions[symbol] = {
                    'entry_time': datetime.now(),
                    'entry_price': current_price,
                    'amount': position_amount,
                    'size': position_size,
                    'direction': 'long'
                }
                
                # Actualizar balance
                self.balance -= (position_size + commission)
                
                # Registrar operación
                self.trade_history.append({
                    'time': datetime.now(),
                    'symbol': symbol,
                    'action': 'BUY',
                    'price': current_price,
                    'amount': position_amount,
                    'balance_after': self.balance
                })
                
                logger.info(f"[PAPER] BUY {symbol}: {position_amount:.6f} @ {current_price:.2f}, Balance: {self.balance:.2f}")
                
            elif action == 'SELL' and position is not None and position['direction'] == 'long':
                # Calcular valor actual y PnL
                current_value = position['amount'] * current_price
                pnl = ((current_price / position['entry_price']) - 1) * 100
                commission = current_value * fee_percentage / 100
                
                # Actualizar balance
                self.balance += (current_value - commission)
                
                # Registrar operación
                self.trade_history.append({
                    'time': datetime.now(),
                    'symbol': symbol,
                    'action': 'SELL',
                    'price': current_price,
                    'amount': position['amount'],
                    'pnl_pct': pnl,
                    'balance_after': self.balance
                })
                
                logger.info(f"[PAPER] SELL {symbol}: {position['amount']:.6f} @ {current_price:.2f}, PnL: {pnl:.2f}%, Balance: {self.balance:.2f}")
                
                # Cerrar posición
                del self.positions[symbol]
                
        except Exception as e:
            logger.error(f"[PAPER] Error ejecutando operación: {e}")
            
    def get_market_data(self, data_service, symbol):
        """Obtiene datos de mercado simulados"""
        return data_service.get_current_market_data(symbol)
        
    def get_open_positions(self):
        """Devuelve las posiciones abiertas"""
        return self.positions
        
    def get_trade_history(self):
        """Devuelve el historial de operaciones"""
        return self.trade_history
        
    def get_balance(self):
        """Devuelve el balance actual"""
        return self.balance
        
    def calculate_equity(self):
        """Calcula el equity actual (balance + posiciones abiertas)"""
        equity = self.balance
        
        for symbol, position in self.positions.items():
            try:
                current_price = position['entry_price']  # Simulación: usar precio de entrada
                position_value = position['amount'] * current_price
                equity += position_value
            except Exception as e:
                logger.error(f"Error calculando equity para {symbol}: {e}")
                
        return equity