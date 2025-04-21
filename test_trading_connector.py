# test_trading_connector.py
from services.data_service.binance_connector import BinanceConnector
import json

# Configura tus credenciales
API_KEY = "Iqs8VWUBIc47QsNxpIplR5yalmKWULpd0rAswofp9Fxp3z1zfiXl270chGVOqiXF"  # Reemplaza con tu API key
API_SECRET = "Jm876AxTdvFrcROySuZsOETMMH6vROH4cgJmOW6wsa9Rfm4sBIyeWRaNBZc0bL9X"  # Reemplaza con tu API secret

print("=== TEST DEL CONECTOR DE TRADING BINANCE ===")

# Crear instancia con credenciales
connector = BinanceConnector(api_key=API_KEY, api_secret=API_SECRET, testnet=True)
print("✓ Conector inicializado correctamente")

# Listar los métodos disponibles
methods = [m for m in dir(connector) if not m.startswith('_') and callable(getattr(connector, m))]
print(f"\nMétodos disponibles ({len(methods)}):")
for method in methods:
    print(f"- {method}")

# Probar get_ohlcv (datos de velas)
try:
    print("\nObteniendo datos OHLCV para BTCUSDT...")
    ohlcv_data = connector.get_ohlcv("BTCUSDT", interval="1h", limit=5)
    print(f"✓ Datos OHLCV obtenidos: {len(ohlcv_data)} registros")
    print(f"✓ Primera vela: {ohlcv_data[0] if ohlcv_data else 'No hay datos'}")
except Exception as e:
    print(f"✗ Error al obtener OHLCV: {str(e)}")

# Probar get_account_balance
try:
    print("\nObteniendo saldo de la cuenta...")
    balance = connector.get_account_balance()
    print(f"✓ Saldo obtenido: {balance}")
except Exception as e:
    print(f"✗ Error al obtener saldo: {str(e)}")

# Probar get_open_positions
try:
    print("\nObteniendo posiciones abiertas...")
    positions = connector.get_open_positions()
    print(f"✓ Posiciones obtenidas: {positions}")
except Exception as e:
    print(f"✗ Error al obtener posiciones: {str(e)}")

print("\n=== TEST COMPLETADO ===")