# validate_binance_connector.py
import os
import time
from datetime import datetime
import logging

# Configurar logging básico para ver resultados
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importar específicamente solo la clase BinanceConnector
from services.data_service.binance_connector import BinanceConnector

def validate_binance_connector():
    print("\n===== VALIDACIÓN DE BINANCE CONNECTOR =====")
    
    # 1. Validar importación
    print("\n[1] Verificando importación")
    print(f"✓ Clase BinanceConnector importada correctamente")
    
    # 2. Validar constructor
    print("\n[2] Probando constructor")
    api_key = "test_api_key"
    api_secret = "test_api_secret"
    
    connector = BinanceConnector(
        api_key=api_key,
        api_secret=api_secret,
        testnet=True
    )
    print(f"✓ Instancia creada correctamente")
    print(f"✓ API Key configurada: {connector.api_key == api_key}")
    print(f"✓ API Secret configurada: {connector.api_secret == api_secret}")
    print(f"✓ TestNet activado: {connector.testnet}")
    
    # Verificar atributos adicionales si existen
    if hasattr(connector, 'api_url'):
        print(f"✓ API URL configurada: {connector.api_url}")
    if hasattr(connector, 'ws_url'):
        print(f"✓ WS URL configurada: {connector.ws_url}")
    
    # 3. Validar sesión HTTP
    print("\n[3] Verificando sesión HTTP")
    if hasattr(connector, 'session'):
        print(f"✓ Sesión HTTP creada: {connector.session is not None}")
        print(f"✓ User-Agent configurado: {'User-Agent' in connector.session.headers}")
        print(f"✓ API Key en headers: {'X-MBX-APIKEY' in connector.session.headers}")
    else:
        print("ℹ️ Sesión HTTP no disponible en esta implementación")
    
    # 4. Validar método connect
    print("\n[4] Probando método connect")
    if hasattr(connector, 'connect') and callable(getattr(connector, 'connect')):
        try:
            symbols = ["BTCUSDT", "ETHUSDT"]
            result = connector.connect(symbols)
            print(f"✓ Método connect ejecutado sin errores")
            print(f"✓ Resultado: {result}")
        except Exception as e:
            print(f"✗ Error en connect: {e}")
    else:
        print("ℹ️ Método connect no disponible en esta implementación")
    
    # 5. Validar get_server_time
    print("\n[5] Probando get_server_time")
    if hasattr(connector, 'get_server_time') and callable(getattr(connector, 'get_server_time')):
        try:
            server_time = connector.get_server_time()
            dt = datetime.fromtimestamp(server_time/1000)
            print(f"✓ Tiempo del servidor obtenido: {server_time}")
            print(f"✓ Fecha/hora formateada: {dt}")
        except Exception as e:
            print(f"✗ Error en get_server_time: {e}")
    else:
        print("ℹ️ Método get_server_time no disponible en esta implementación")
    
    # 6. Validar get_exchange_info
    print("\n[6] Probando get_exchange_info")
    if hasattr(connector, 'get_exchange_info') and callable(getattr(connector, 'get_exchange_info')):
        try:
            exchange_info = connector.get_exchange_info()
            print(f"✓ Información del exchange obtenida")
            print(f"✓ Zona horaria: {exchange_info.get('timezone')}")
            print(f"✓ Tiempo del servidor presente: {'serverTime' in exchange_info}")
        except Exception as e:
            print(f"✗ Error en get_exchange_info: {e}")
    else:
        print("ℹ️ Método get_exchange_info no disponible en esta implementación")
    
    # 7. Validar get_account_info
    print("\n[7] Probando get_account_info")
    if hasattr(connector, 'get_account_info') and callable(getattr(connector, 'get_account_info')):
        try:
            account_info = connector.get_account_info()
            print(f"✓ Información de la cuenta obtenida")
            print(f"✓ Balances presente: {'balances' in account_info}")
            print(f"✓ Permisos presente: {'permissions' in account_info}")
        except Exception as e:
            print(f"✗ Error en get_account_info: {e}")
    else:
        print("ℹ️ Método get_account_info no disponible en esta implementación")
    
    # 8. Validar disconnect
    print("\n[8] Probando disconnect")
    if hasattr(connector, 'disconnect') and callable(getattr(connector, 'disconnect')):
        try:
            connector.disconnect()
            print(f"✓ Método disconnect ejecutado sin errores")
        except Exception as e:
            print(f"✗ Error en disconnect: {e}")
    else:
        print("ℹ️ Método disconnect no disponible en esta implementación")
    
    print("\n===== VALIDACIÓN COMPLETADA =====")

if __name__ == "__main__":
    validate_binance_connector()