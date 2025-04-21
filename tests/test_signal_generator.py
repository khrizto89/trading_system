from core.strategy.signal_generator import SignalGenerator
from core.models.model_manager import ModelManager

def test_signal_generator():
    config = {
        'strategy': {'buy_threshold': 0.6, 'sell_threshold': 0.6},
        'models': {'base_path': 'models'}
    }
    models_manager = ModelManager(config)
    signal_generator = SignalGenerator(config, models_manager=models_manager)
    
    market_data = {'BTC/USDT': {'price': 50000, 'volume': 1000}}
    signal = signal_generator.generate_signal('BTC/USDT', market_data)
    print("Señal generada:", signal)

if __name__ == "__main__":
    test_signal_generator()