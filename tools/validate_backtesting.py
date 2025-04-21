import sys
import os
import logging
import json
from datetime import datetime, timedelta
import pandas as pd

# Añadir directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar componentes necesarios
from services.data_service.data_processor import DataProcessor
from services.data_service.binance_connector import BinanceConnector
from core.features.technical_features import TechnicalFeatures
from core.models.model_manager import ModelManager
from core.strategy.signal_generator import SignalGenerator
from services.learning.backtesting import Backtesting

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger('BacktestValidation')

def load_config():
    """Carga la configuración del sistema"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")
        return {}

def main():
    """Función principal para validar el sistema de backtesting"""
    logger.info("=== VALIDACIÓN DEL SISTEMA DE BACKTESTING ===")
    
    # Cargar configuración
    config = load_config()
    
    # Inicializar componentes
    logger.info("Inicializando componentes...")
    
    try:
        # Inicializar conector a Binance
        binance_connector = BinanceConnector(config)
        
        # Inicializar procesador de datos
        data_processor = DataProcessor(config, binance_connector)
        
        # Inicializar características técnicas
        technical_features = TechnicalFeatures()
        
        # Inicializar gestor de modelos
        model_manager = ModelManager(config)
        
        # Inicializar generador de señales
        signal_generator = SignalGenerator(config, model_manager, technical_features)
        
        # Inicializar sistema de backtesting
        backtest = Backtesting()
        
        logger.info("Componentes inicializados correctamente")
        
        # Definir período para el backtest
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Simular datos de mercado
        market_data = pd.DataFrame({
            'timestamp': pd.date_range(start=start_date, end=end_date, freq='D'),
            'price': [100 + i * 0.5 for i in range(31)],
            'signal': [{'action': 'BUY'} if i % 10 == 0 else {'action': 'HOLD'} for i in range(31)]
        })
        
        # Ejecutar backtest simple para BTC/USDT
        logger.info(f"Ejecutando backtest para BTC/USDT desde {start_date} hasta {end_date}...")
        
        strategy_params = {
            'stop_loss_pct': 5.0,
            'take_profit_pct': 10.0,
            'fee_pct': 0.1,
            'position_size_pct': 20.0
        }
        
        result = backtest.run_backtest(
            'BTC/USDT',
            start_date,
            end_date,
            initial_capital=10000.0,
            strategy_params=strategy_params,
            market_data=market_data
        )
        
        if result:
            logger.info("Backtest completado exitosamente")
            logger.info(f"Resultado final: {result['final_balance']:.2f} USD")
            logger.info(f"Retorno total: {result['metrics']['total_return_pct']:.2f}%")
            logger.info(f"Win rate: {result['metrics']['win_rate']*100:.2f}%")
            logger.info(f"Trades totales: {result['metrics']['total_trades']}")
            logger.info(f"Drawdown máximo: {result['metrics']['max_drawdown_pct']:.2f}%")
            logger.info(f"Informe guardado en: {result['equity_file']}")
        else:
            logger.error("Error ejecutando backtest")
            
        # Comparar estrategias
        logger.info("Comparando múltiples estrategias...")
        
        strategies = [
            {'name': 'Conservadora', 'stop_loss_pct': 3.0, 'take_profit_pct': 6.0, 'fee_pct': 0.1, 'position_size_pct': 10.0},
            {'name': 'Moderada', 'stop_loss_pct': 5.0, 'take_profit_pct': 10.0, 'fee_pct': 0.1, 'position_size_pct': 20.0},
            {'name': 'Agresiva', 'stop_loss_pct': 7.0, 'take_profit_pct': 14.0, 'fee_pct': 0.1, 'position_size_pct': 30.0}
        ]
        
        comparison = backtest.compare_strategies('BTC/USDT', start_date, end_date, strategies)
        
        if comparison:
            logger.info("Comparación de estrategias completada")
            for result in comparison:
                logger.info(f"Estrategia: {result['strategy_name']}, Retorno: {result['metrics']['total_return_pct']:.2f}%")
        else:
            logger.error("Error comparando estrategias")
            
        logger.info("=== VALIDACIÓN COMPLETADA ===")
        
    except Exception as e:
        logger.error(f"Error en validación: {e}")
        logger.info("=== VALIDACIÓN FALLIDA ===")

if __name__ == "__main__":
    main()