from core.utils.logging import TradingLogger
from services.data_service.database import Database
from traders.btc_trader.btc_trader import BTCTrader
from traders.btc_trader.config import BTCTraderConfig

# Configurar logging
logger = TradingLogger().get_logger()
logger.info("Iniciando prueba simplificada")

# Probar Database
try:
    db = Database("test.db")
    logger.info("✅ Database inicializada correctamente")
except Exception as e:
    logger.error(f"❌ Error al inicializar Database: {e}")
    logger.info(f"Firma esperada: {Database.__init__.__code__.co_varnames}")

# Probar BTCTrader
try:
    config = BTCTraderConfig().get_config()
    logger.info(f"Configuración obtenida: {config}")
    trader = BTCTrader()  # Sin parámetros
    logger.info("✅ BTCTrader inicializado correctamente sin parámetros")
except Exception as e:
    logger.error(f"❌ Error al inicializar BTCTrader sin parámetros: {e}")

# Probar con parámetros
try:
    trader = BTCTrader(config)  # Solo config como posicional
    logger.info("✅ BTCTrader inicializado correctamente con config posicional")
except Exception as e:
    logger.error(f"❌ Error al inicializar BTCTrader con config posicional: {e}")

# Más pruebas...
logger.info("Prueba completada")