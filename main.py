#!/usr/bin/env python3
"""
Sistema de Trading Algorítmico con IA para Criptomonedas
Punto de entrada principal
"""

# Importaciones estándar
import os
import sys
import time
import signal
import logging
import json
import argparse
from datetime import datetime

# Componentes del sistema
try:
    # Core
    from core.utils.logging import TradingLogger
    from core.utils.config import ConfigManager
    from core.models.model_manager import ModelManager
    from core.models.ensembler import Ensembler  # Cambiar de ModelEnsembler a Ensembler
    from core.features.feature_extractor import FeatureExtractor
    from core.strategy.signal_generator import SignalGenerator
    from core.strategy.risk_manager import RiskManager
    from core.optimization.gpu_optimizer import GPUOptimizer

    # Services
    from services.data_service.data_processor import DataProcessor
    from services.data_service.database import Database
    from services.monitor_service.system_monitor import SystemMonitor
    from services.monitor_service.trading_monitor import TradingMonitor
    from services.api_service.notification import NotificationService
    from services.learning.backtesting import BacktestingEngine

    # Traders - Corregido el nombre de la clase
    from traders.trader_base import TraderBase  # Cambiado de Trader a TraderBase
    from traders.btc_trader.btc_trader import BTCTrader
    from traders.btc_trader.config import BTCTraderConfig
    from traders.eth_trader.eth_trader import ETHTrader
    from traders.eth_trader.config import ETHTraderConfig

    # Environment Loader
    from load_env import EnvironmentLoader
except ImportError as e:
    print(f"Error importando componentes del sistema: {e}")
    print("Asegúrate de que todos los módulos estén disponibles")
    sys.exit(1)

# Configuración de logging
logger = TradingLogger().get_logger()

# Variables globales
running = True
config = None
services = {}
traders = []

def signal_handler(sig, frame):
    """Maneja señales para detener el sistema de manera ordenada."""
    global running
    logger.info("Señal recibida. Deteniendo el sistema de trading...")
    running = False

def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description='Sistema de Trading Algorítmico')
    parser.add_argument('--diagnostico', action='store_true', help='Ejecutar diagnóstico del sistema')
    parser.add_argument('--verbose', action='store_true', help='Mostrar logs detallados')
    return parser.parse_args()

def load_configuration():
    """Carga la configuración del sistema."""
    try:
        logger.info("Cargando configuración...")
        
        # Cargar variables de entorno
        if os.path.exists(".env"):
            logger.info("Cargando variables de entorno desde .env")
            # Implementación básica, puedes expandir esto
            with open(".env") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
        
        # Cargar configuración desde JSON
        config_path = "config.json"
        if not os.path.exists(config_path):
            logger.warning(f"Archivo de configuración {config_path} no encontrado. Usando valores por defecto.")
            return {
                "system": {"name": "Trading System", "environment": "development"},
                "trading_mode": "paper",
                "binance": {"testnet": True},
                "traders": {"btc": {"enabled": True}, "eth": {"enabled": True}}
            }
        
        with open(config_path, "r") as f:
            config = json.load(f)
            logger.info(f"Configuración cargada desde {config_path}")
            return config
    
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")
        logger.info("Usando configuración por defecto")
        return {
            "system": {"name": "Trading System", "environment": "development"},
            "trading_mode": "paper",
            "binance": {"testnet": True},
            "traders": {"btc": {"enabled": True}, "eth": {"enabled": True}}
        }

def initialize_services(config):
    """Inicializa los servicios necesarios."""
    services = {}
    
    try:
        logger.info("Inicializando servicios...")
        
        # Base de datos
        logger.info("Inicializando base de datos...")
        db_path = config.get("database", {}).get("path", "trading_system.db")
        services["database"] = Database(db_path)
        
        # Procesador de datos
        logger.info("Inicializando procesador de datos...")
        services["data_processor"] = DataProcessor()
        
        # Inicializar conector de Binance real
        logger.info("Inicializando conector de Binance...")
        binance_config = config.get("binance", {})
        api_key = binance_config.get("api_key", "")
        api_secret = binance_config.get("api_secret", "")
        testnet = binance_config.get("testnet", True)
        
        try:
            # Intentar importar e inicializar el conector real
            from services.data_service.binance_connector import BinanceConnector  # Corrected import path
            
            binance = BinanceConnector(
                api_key=api_key,
                api_secret=api_secret,
                testnet=testnet
            )
            
            # Intentar conectar
            if hasattr(binance, "connect") and binance.connect():
                logger.info("Conexión exitosa con Binance")
                services["data_service"] = binance
            else:
                logger.warning("No se pudo conectar a Binance. Usando simulador.")
                services["data_service"] = create_simulated_data_service()
                
        except ImportError as e:
            logger.warning(f"No se pudo importar BinanceConnector: {e}")
            logger.info("Inicializando conector de Binance (simulado)...")
            services["data_service"] = create_simulated_data_service()
        except Exception as e:
            logger.warning(f"Error al inicializar Binance: {e}")
            logger.info("Inicializando conector de Binance (simulado)...")
            services["data_service"] = create_simulated_data_service()
        
        # Crear indicadores primero (necesarios para SignalGenerator)
        logger.info("Inicializando indicadores...")
        from core.features.technical_features import TechnicalFeatures
        indicators = TechnicalFeatures()
        services["indicators"] = indicators
        
        # Inicializar modelos - simplificado (necesarios para SignalGenerator)
        logger.info("Inicializando modelos simples...")
        simple_models = {"dummy_model": lambda x: 0.5}  # Modelo simulado que siempre devuelve 0.5
        
        # Inicializar SignalGenerator - Corregido: pasando los argumentos requeridos
        logger.info("Inicializando generador de señales...")
        services["signal_generator"] = SignalGenerator(models=simple_models, indicators=indicators)
        
        # Inicializar PositionManager - Corregido: funciones lambda con argumentos
        logger.info("Inicializando gestor de posiciones...")
        services["position_manager"] = type('PositionManagerSimulated', (), {
            'execute_trade': lambda signal, *args, **kwargs: True,
            'get_open_positions': lambda *args, **kwargs: []
        })()
        
        # Notificaciones - Corregido para soportar métodos esperados
        logger.info("Inicializando servicio de notificaciones...")
        notification_config = config.get("notifications", {})
        services["notification_service"] = type('NotificationServiceSimulated', (), {
            'send_message': lambda message, *args, **kwargs: None,
            'send_trade_notification': lambda result, *args, **kwargs: None,
            'enabled': notification_config.get("enabled", False),
            'token': notification_config.get("telegram_token", ""),
            'chat_id': notification_config.get("chat_id", "")
        })()
        
        # Intentar usar NotificationService real si está disponible
        try:
            real_notification = NotificationService(
                token=notification_config.get("telegram_token", ""),
                chat_id=notification_config.get("chat_id", ""),
                enabled=notification_config.get("enabled", False)
            )
            services["notification_service"] = real_notification
            logger.info("Servicio de notificaciones real inicializado")
        except Exception as e:
            logger.warning(f"Usando servicio de notificaciones simulado: {e}")
        
        # Monitores
        logger.info("Inicializando monitores...")
        services["system_monitor"] = type('SystemMonitorSimulated', (), {
            'check_status': lambda *args, **kwargs: {"healthy": True, "message": "OK"}
        })()
        services["trading_monitor"] = type('TradingMonitorSimulated', (), {
            'update_stats': lambda *args, **kwargs: None
        })()
        
        # Optimizador GPU
        if config.get("use_gpu", False):
            logger.info("Inicializando optimizador GPU...")
            services["gpu_optimizer"] = GPUOptimizer()
        
        logger.info("Servicios inicializados correctamente")
        return services
    
    except Exception as e:
        logger.error(f"Error inicializando servicios: {e}")
        return services

def create_simulated_data_service():
    """Crea un servicio de datos simulado."""
    return type('BinanceConnectorSimulated', (), {
        'get_market_data_simulation': lambda *args, **kwargs: {
            'BTC/USDT': {'price': 50000 + (time.time() % 1000) / 10, 'volume': 10},
            'ETH/USDT': {'price': 3000 + (time.time() % 500) / 10, 'volume': 20}
        },
        'get_market_data': lambda *args, **kwargs: {
            'BTC/USDT': {'price': 50000 + (time.time() % 1000) / 10, 'volume': 10},
            'ETH/USDT': {'price': 3000 + (time.time() % 500) / 10, 'volume': 20}
        },
        'connect': lambda: True,
        'disconnect': lambda *args, **kwargs: None
    })()

def initialize_models(config, services):
    """Inicializa y configura los modelos de IA."""
    try:
        logger.info("Inicializando modelos de IA...")
        
        # Inicializar gestor de modelos
        model_manager = ModelManager(logger)
        
        # Crear extractor de características
        feature_extractor = FeatureExtractor()
        
        # Inicializar ensemble
        model_ensembler = Ensembler(logger)
        
        # Cargar modelos pre-entrenados si existen
        models_dir = config.get("models_directory", "models")
        if os.path.exists(models_dir):
            for model_file in os.listdir(models_dir):
                if model_file.endswith(".pth") or model_file.endswith(".h5"):
                    model_path = os.path.join(models_dir, model_file)
                    model_name = os.path.splitext(model_file)[0]
                    model_manager.load_saved_model(model_name, model_path)
                    logger.info(f"Modelo {model_name} cargado desde {model_path}")
        
        logger.info("Modelos de IA inicializados correctamente")
        
        return {
            "model_manager": model_manager,
            "feature_extractor": feature_extractor,
            "model_ensembler": model_ensembler
        }
    
    except Exception as e:
        logger.error(f"Error inicializando modelos: {e}")
        return None

def load_traders(config, services, models):
    """Carga y configura los traders habilitados."""
    traders = []
    
    try:
        logger.info("Cargando traders habilitados...")
        
        # Configurar trader de BTC si está habilitado
        if config.get("traders", {}).get("btc", {}).get("enabled", False):
            logger.info("Inicializando trader de BTC...")
            
            # Inicializar BTCTrader con los argumentos requeridos
            btc_trader = BTCTrader(
                data_service=services["data_service"],
                signal_generator=services["signal_generator"],
                position_manager=services["position_manager"],
                notification_service=services["notification_service"]
            )
            
            traders.append(btc_trader)
            logger.info("Trader de BTC inicializado")
        
        # Configurar trader de ETH si está habilitado
        if config.get("traders", {}).get("eth", {}).get("enabled", False):
            logger.info("Inicializando trader de ETH...")
            
            # Inicializar ETHTrader con los argumentos requeridos (asumiendo la misma firma)
            eth_trader = ETHTrader(
                data_service=services["data_service"],
                signal_generator=services["signal_generator"],
                position_manager=services["position_manager"],
                notification_service=services["notification_service"]
            )
            
            traders.append(eth_trader)
            logger.info("Trader de ETH inicializado")
        
        logger.info(f"{len(traders)} traders inicializados")
        return traders
    
    except Exception as e:
        logger.error(f"Error cargando traders: {e}")
        return traders

def run_backtesting(config, services, models, traders):
    """Ejecuta backtesting con datos históricos."""
    try:
        logger.info("Iniciando modo backtesting...")
        
        # Inicializar motor de backtesting
        backtesting_config = config.get("backtesting", {})
        start_date = backtesting_config.get("start_date", "2023-01-01")
        end_date = backtesting_config.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        
        backtesting_engine = BacktestingEngine(
            services=services,
            config=backtesting_config
        )
        
        # Ejecutar backtesting para cada trader
        for trader in traders:
            logger.info(f"Ejecutando backtesting para {trader.get_name()}...")
            results = backtesting_engine.run(
                trader=trader,
                start_date=start_date,
                end_date=end_date
            )
            
            # Mostrar resultados
            logger.info(f"Resultados de backtesting para {trader.get_name()}:")
            logger.info(f"  Rentabilidad: {results.get('return', 0):.2f}%")
            logger.info(f"  Sharpe Ratio: {results.get('sharpe', 0):.2f}")
            logger.info(f"  Máximo Drawdown: {results.get('max_drawdown', 0):.2f}%")
            logger.info(f"  Operaciones ganadoras: {results.get('win_rate', 0):.2f}%")
        
        logger.info("Backtesting completado")
    
    except Exception as e:
        logger.error(f"Error en backtesting: {e}")

def run_paper_trading(services, traders):
    """Ejecuta paper trading (simulación)."""
    try:
        logger.info("Iniciando modo paper trading...")
        
        # Ejecutar solo unos pocos ciclos para prueba
        for iteration in range(1, 6):
            if not running:
                break
                
            logger.info(f"Ciclo de paper trading #{iteration}")
            
            try:
                # Obtener datos simulados de mercado
                market_data = {'BTC/USDT': {'price': 50000 + (iteration * 100), 'volume': 10}}
                
                # Procesar cada trader
                for trader in traders:
                    try:
                        # Analizar mercado
                        if hasattr(trader, 'analyze_market'):
                            signal = trader.analyze_market(market_data)
                            
                            # Ejecutar operación si hay señal
                            if signal and hasattr(trader, 'execute_paper_trade'):
                                trader.execute_paper_trade(signal)
                    except Exception as e:
                        logger.error(f"Error procesando trader: {e}")
                
                # Actualizar monitores
                try:
                    if services.get("trading_monitor") and hasattr(services["trading_monitor"], "update_stats"):
                        services["trading_monitor"].update_stats()
                except Exception as e:
                    logger.warning(f"Error actualizando monitor: {e}")
                    
                # Verificar estado
                try:
                    if services.get("system_monitor") and hasattr(services["system_monitor"], "check_status"):
                        services["system_monitor"].check_status()
                except Exception as e:
                    logger.warning(f"Error verificando estado: {e}")
                
                # Esperar entre ciclos
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error en ciclo {iteration}: {e}")
        
        logger.info("Ciclos de paper trading completados correctamente")
        
    except Exception as e:
        logger.error(f"Error en paper trading: {e}")

def run_live_trading(services, traders):
    """Ejecuta trading en vivo con dinero real."""
    try:
        logger.info("Iniciando modo live trading...")
        
        # Aviso importante de seguridad
        logger.warning("¡ATENCIÓN! El sistema está operando con dinero real.")
        services.get("notification_service").send_message("⚠️ Sistema de trading iniciado en modo REAL")
        
        iteration = 0
        while running:
            iteration += 1
            logger.info(f"Ciclo de live trading #{iteration}")
            
            # Obtener datos actuales de mercado
            market_data = services.get("data_service").get_market_data()
            
            # Procesar cada trader
            for trader in traders:
                try:
                    # Analizar mercado
                    signal = trader.analyze_market(market_data)
                    
                    # Ejecutar operación si hay señal
                    if signal:
                        result = trader.execute_live_trade(signal)
                        if result:
                            services.get("notification_service").send_trade_notification(result)
                
                except Exception as e:
                    error_msg = f"Error procesando trader {trader.get_name()}: {e}"
                    logger.error(error_msg)
                    services.get("notification_service").send_message(f"❌ {error_msg}")
            
            # Actualizar monitor de trading
            services.get("trading_monitor").update_stats()
            
            # Verificar estado del sistema
            system_status = services.get("system_monitor").check_status()
            if not system_status.get("healthy", False):
                error_msg = f"Estado del sistema: {system_status.get('message', 'Desconocido')}"
                logger.error(error_msg)
                services.get("notification_service").send_message(f"⚠️ {error_msg}")
            
            # Esperar antes del siguiente ciclo
            time.sleep(10)  # Intervalo entre ciclos (ajustable)
    
    except Exception as e:
        error_msg = f"Error crítico en live trading: {e}"
        logger.error(error_msg)
        services.get("notification_service").send_message(f"🚨 {error_msg}")

def cleanup():
    """Limpia recursos y finaliza componentes."""
    try:
        logger.info("Realizando limpieza del sistema...")
        
        # Notificar finalización - Usando enfoque más seguro
        try:
            if services.get("notification_service") and hasattr(services["notification_service"], 'send_message'):
                services["notification_service"].send_message("Sistema de trading detenido")
        except Exception as e:
            logger.warning(f"Error al enviar notificación de cierre: {e}")
        
        # Guardar estado de los traders - Usando enfoque más seguro
        for trader in traders:
            try:
                if hasattr(trader, 'save_state'):
                    trader.save_state()
            except Exception as e:
                logger.warning(f"Error al guardar estado del trader: {e}")
        
        # Cerrar conexiones - Usando enfoque más seguro
        try:
            if services.get("data_service") and hasattr(services["data_service"], 'disconnect'):
                services["data_service"].disconnect()
            logger.info("Servicio de datos desconectado correctamente.")
        except Exception as e:
            logger.warning(f"Error al desconectar servicio de datos: {e}")
        
        # Cerrar base de datos - Usando enfoque más seguro
        try:
            if services.get("database") and hasattr(services["database"], 'close'):
                services["database"].close()
            logger.info("Base de datos cerrada correctamente.")
        except Exception as e:
            logger.warning(f"Error al cerrar base de datos: {e}")
        
        logger.info("Limpieza completada")
    
    except Exception as e:
        logger.error(f"Error durante la limpieza: {e}")

def run_diagnostics():
    """Ejecuta diagnósticos básicos del sistema."""
    print("\n--- DIAGNÓSTICO DEL SISTEMA ---")
    try:
        from core.models.model_manager import ModelManager
        mm = ModelManager(logger)
        print("✓ ModelManager inicializado correctamente")
    except Exception as e:
        print(f"✗ Error en ModelManager: {str(e)}")
    
    try:
        from core.features.feature_extractor import FeatureExtractor
        fe = FeatureExtractor()
        print("✓ FeatureExtractor inicializado correctamente")
    except Exception as e:
        print(f"✗ Error en FeatureExtractor: {str(e)}")
    
    try:
        from services.data_service.binance_connector import BinanceConnector
        bc = BinanceConnector(testnet=True)
        if bc.connect():
            print("✓ BinanceConnector conectado correctamente")
        else:
            print("✗ BinanceConnector no pudo conectarse")
    except Exception as e:
        print(f"✗ Error en BinanceConnector: {str(e)}")
    
    try:
        from services.api_service.notification import NotificationService
        ns = NotificationService(token="dummy", chat_id="dummy", enabled=True)
        ns.send_message("Prueba de notificación")
        print("✓ NotificationService inicializado correctamente")
    except Exception as e:
        print(f"✗ Error en NotificationService: {str(e)}")

    try:
        from services.learning.backtesting import BacktestingEngine
        be = BacktestingEngine(services={})
        print("✓ BacktestingEngine inicializado correctamente")
    except Exception as e:
        print(f"✗ Error en BacktestingEngine: {str(e)}")

    print("--- FIN DEL DIAGNÓSTICO ---\n")

def setup_verbose_logging():
    """Configura loggers detallados para componentes clave."""
    # Configurar loggers específicos
    model_logger = logging.getLogger('TradingSystem.Models')
    model_logger.setLevel(logging.DEBUG)
    
    feature_logger = logging.getLogger('TradingSystem.Features')
    feature_logger.setLevel(logging.DEBUG)
    
    signal_logger = logging.getLogger('TradingSystem.Signals')
    signal_logger.setLevel(logging.DEBUG)
    
    # Añadir handler para todos los loggers
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    model_logger.addHandler(handler)
    feature_logger.addHandler(handler)
    signal_logger.addHandler(handler)
    
    return {
        'model_logger': model_logger,
        'feature_logger': feature_logger,
        'signal_logger': signal_logger
    }

def setup_detailed_logging():
    """Configura logs detallados para componentes clave y guarda en archivos."""
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Configurar handler de archivo para logs detallados
    debug_handler = logging.FileHandler('logs/trading_detailed.log')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Configurar loggers específicos
    models_logger = logging.getLogger('TradingSystem.Models')
    models_logger.setLevel(logging.DEBUG)
    models_logger.addHandler(debug_handler)
    
    features_logger = logging.getLogger('TradingSystem.Features')
    features_logger.setLevel(logging.DEBUG)
    features_logger.addHandler(debug_handler)
    
    strategy_logger = logging.getLogger('TradingSystem.Strategy')
    strategy_logger.setLevel(logging.DEBUG)
    strategy_logger.addHandler(debug_handler)
    
    return {
        'models': models_logger,
        'features': features_logger,
        'strategy': strategy_logger
    }

def log_model_operations(model_manager, signal_generator):
    """Configura loggers específicos para componentes de IA"""
    models_logger = logging.getLogger('TradingSystem.Models')
    models_logger.setLevel(logging.DEBUG)
    
    # Añade hook para registrar predicciones
    original_predict = model_manager.predict
    
    def predict_with_logging(*args, **kwargs):
        models_logger.debug(f"Iniciando predicción con datos: {args[0].shape if hasattr(args[0], 'shape') else 'unknown shape'}")
        result = original_predict(*args, **kwargs)
        models_logger.debug(f"Resultado de predicción: {result}")
        return result
    
    model_manager.predict = predict_with_logging
    
    # Añade hook para registrar generación de señales
    signals_logger = logging.getLogger('TradingSystem.Signals')
    signals_logger.setLevel(logging.DEBUG)
    
    original_generate = signal_generator.generate_signal
    
    def generate_with_logging(*args, **kwargs):
        signals_logger.debug(f"Generando señal con datos: {args}")
        result = original_generate(*args, **kwargs)
        signals_logger.debug(f"Señal generada: {result}")
        return result
    
    signal_generator.generate_signal = generate_with_logging

def main():
    """Función principal del sistema."""
    global config, services, traders, running
    
    # Registrar handlers de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("==========================================")
    logger.info("Sistema de Trading Algorítmico Inicializando")
    logger.info("==========================================")
    
    try:
        # Configurar logging detallado
        detailed_loggers = setup_detailed_logging()
        logger.info("Logging detallado configurado.")
        
        # Configurar logging detallado si se solicita
        if args.verbose:
            loggers = setup_verbose_logging()
            logger.info("Logging detallado habilitado.")
        
        # Cargar configuración
        env_loader = EnvironmentLoader(logger=logger)
        env_loader.load_env_file()
        env_loader.load_config_file("config.json")
        env_loader.load_environment(environment="development")
        
        # Validar claves críticas para el funcionamiento del sistema
        env_loader.validate_critical_keys(["trading_mode", "database.path"])
        
        # Verificar credenciales de Binance
        env_loader.manage_binance_credentials()
        
        config = env_loader.get_config()
        
        # Inicializar servicios
        services = initialize_services(config)
        
        # Inicializar modelos
        models = initialize_models(config, services)
        
        # Cargar traders
        traders = load_traders(config, services, models)
        
        if not traders:
            logger.error("No se pudieron inicializar traders. Abortando.")
            return
        
        # Configurar hooks de logging para modelos y generación de señales
        log_model_operations(models["model_manager"], services["signal_generator"])
        
        # Determinar modo de operación
        trading_mode = config.get("trading_mode", "paper")
        logger.info(f"Modo de operación seleccionado: {trading_mode}")
        
        # Ejecutar en el modo correspondiente
        if trading_mode == "backtesting":
            run_backtesting(config, services, models, traders)
        elif trading_mode == "paper":
            run_paper_trading(services, traders)
        elif trading_mode == "live":
            run_live_trading(services, traders)
        else:
            logger.error(f"Modo de operación desconocido: {trading_mode}")
    
    except Exception as e:
        logger.error(f"Error crítico en el sistema: {e}")
    
    finally:
        cleanup()
        logger.info("Sistema de Trading Algorítmico Finalizado")

if __name__ == "__main__":
    args = parse_args()
    
    # Configurar logging detallado si se solicita
    if args.verbose:
        logging.getLogger('TradingSystem').setLevel(logging.DEBUG)
    
    # Ejecutar diagnóstico si se solicita
    if args.diagnostico:
        run_diagnostics()
    else:
        main()