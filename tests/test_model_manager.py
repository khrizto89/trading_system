from core.models.model_manager import ModelManager

def test_model_manager():
    config = {
        'models': {
            'base_path': 'models',
            'symbols': {
                'BTC/USDT': {
                    'enabled': True,
                    'lstm': {'enabled': True, 'path': 'lstm_model.h5'},
                    'transformer': {'enabled': True, 'path': 'transformer_model.h5'}
                }
            }
        }
    }
    manager = ModelManager(config)
    features = {'sequence': [[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]]}
    prediction = manager.predict('BTC/USDT', features)
    print("Predicción:", prediction)

if __name__ == "__main__":
    test_model_manager()