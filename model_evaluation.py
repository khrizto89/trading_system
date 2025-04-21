import logging
import pandas as pd
from datetime import datetime, timedelta

from core.models.model_manager import ModelManager
from services.learning.backtesting import BacktestingEngine
from core.strategy.signal_generator import SignalGenerator
from services.data_service.binance_connector import BinanceConnector

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModelEvaluation")

def run_model_evaluation():
    """Ejecuta una evaluación completa de modelos."""
    logger.info("Iniciando evaluación de modelos")
    
    # Inicializar componentes
    binance = BinanceConnector(testnet=True)
    binance.connect()
    
    model_manager = ModelManager(logger)
    
    # Cargar modelos disponibles
    available_models = ["lstm", "transformer", "baseline"]
    models = {}
    for model_name in available_models:
        try:
            model = model_manager.load_model(model_name)
            models[model_name] = model
            logger.info(f"Modelo {model_name} cargado correctamente")
        except Exception as e:
            logger.warning(f"No se pudo cargar modelo {model_name}: {e}")
    
    # Definir períodos de evaluación
    end_date = datetime.now()
    periods = [
        ("1 semana", end_date - timedelta(days=7), end_date),
        ("1 mes", end_date - timedelta(days=30), end_date),
        ("3 meses", end_date - timedelta(days=90), end_date),
    ]
    
    # Símbolos a evaluar
    symbols = ["BTC/USDT", "ETH/USDT"]
    
    # Métricas por modelo
    model_metrics = {model_name: {} for model_name in models}
    
    # Evaluar cada combinación
    for symbol in symbols:
        for period_name, start, end in periods:
            logger.info(f"Evaluando {symbol} para {period_name}")
            
            # Obtener datos históricos
            data = binance.get_historical_data(
                symbol=symbol,
                interval="1h",
                start_time=int(start.timestamp() * 1000),
                end_time=int(end.timestamp() * 1000)
            )
            
            # Evaluar cada modelo
            for model_name, model in models.items():
                logger.info(f"Evaluando modelo {model_name}")
                
                # Crear indicadores y procesamiento específicos para este modelo
                processed_data = prepare_data_for_model(data, model_name)
                
                # Dividir en features y target
                features = processed_data.drop(columns=['target'])
                target = processed_data['target']
                
                # Evaluar métricas directas del modelo
                predictions = model.predict(features)
                metrics = calculate_metrics(predictions, target.values)
                
                # Crear estrategia basada en este modelo para backtest
                strategy = create_strategy_from_model(model, model_name)
                
                # Ejecutar backtest
                backtest_engine = BacktestingEngine({"data_service": binance})
                backtest_results = backtest_engine.run_backtest(
                    strategy=strategy,
                    start_date=start.strftime("%Y-%m-%d"),
                    end_date=end.strftime("%Y-%m-%d"),
                    symbol=symbol
                )
                
                # Combinar métricas
                combined_metrics = {
                    **metrics,
                    "return": backtest_results["final_balance"] / backtest_results["initial_balance"] - 1,
                    "win_rate": backtest_results["win_rate"],
                    "max_drawdown": backtest_results["max_drawdown"],
                    "sharpe_ratio": backtest_results["sharpe_ratio"],
                    "profit_factor": backtest_results["profit_factor"],
                    "trade_count": len(backtest_results["trades"])
                }
                
                # Guardar métricas
                key = f"{symbol}_{period_name}"
                model_metrics[model_name][key] = combined_metrics
                logger.info(f"Métricas para {model_name} en {symbol} ({period_name}): {combined_metrics}")
    
    # Generar reporte final
    generate_evaluation_report(model_metrics, symbols, periods)
    
    # Desconectar
    binance.disconnect()
    logger.info("Evaluación completada")

def generate_evaluation_report(metrics, symbols, periods):
    """Genera un reporte completo de evaluación."""
    report = []
    for model_name, model_data in metrics.items():
        for key, metric_data in model_data.items():
            report.append({"model": model_name, "key": key, **metric_data})
    
    df = pd.DataFrame(report)
    report_path = "model_evaluation_report.csv"
    df.to_csv(report_path, index=False)
    logger.info(f"Reporte de evaluación generado: {report_path}")

# Funciones auxiliares (implementación simplificada)
def prepare_data_for_model(data, model_name):
    """Prepara datos para un modelo específico."""
    # Implementación real depende del modelo
    data['target'] = data['close'].shift(-1)  # Ejemplo: predecir el próximo precio
    return data.dropna()

def calculate_metrics(predictions, actuals):
    """Calcula métricas de rendimiento."""
    accuracy = sum((predictions > 0) == (actuals > 0)) / len(actuals)
    mse = sum((predictions - actuals) ** 2) / len(actuals)
    return {"accuracy": accuracy, "mse": mse}

def create_strategy_from_model(model, model_name):
    """Crea una estrategia de trading basada en un modelo."""
    class ModelBasedStrategy:
        def __init__(self, model):
            self.model = model
        
        def generate_signals(self, data):
            predictions = self.model.predict(data)
            signals = pd.DataFrame({"signal": (predictions > 0).astype(int) - (predictions < 0).astype(int)})
            return signals
    
    return ModelBasedStrategy(model)

if __name__ == "__main__":
    run_model_evaluation()
