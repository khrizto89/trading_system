# test_binance.py
from services.data_service.binance_connector import BinanceConnector
from datetime import datetime
import time
import os

# Credenciales - Rellena estas variables con tus claves API
API_KEY = "tmE9XiPhXXfHRvqDNPAWawGpXyhbiei9pRAbdLUu9ZokTDv7r25GzXv1vXDG1LRr"  # Reemplazar con tu API key entre comillas
API_SECRET = "VQD3Ywd6cdHtMOHgKXN4JQhsV4aY5May6t6mqDSyQEDGhf1Dya6RrOpEXX5jxyBn"  # Reemplazar con tu API secret entre comillas

def test_binance_connector():
    print("\n=== TEST DEL CONECTOR DE BINANCE ===")
    
    # Crear directorio para logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Inicializar conector
    print("\nInicializando conector Binance...")
    binance = BinanceConnector(
        api_key=API_KEY,
        api_secret=API_SECRET,
        testnet=True
    )
    
    # Verificar propiedades básicas
    print(f"Modo TestNet: {binance.testnet}")
    
    # No todas las implementaciones tienen api_url
    if hasattr(binance, 'api_url'):
        print(f"API URL: {binance.api_url}")
    
    # Probar conexión
    print("\nIntentando conectar...")
    try:
        connection_success = binance.connect()
        if connection_success:
            print("✓ Conexión exitosa con Binance")
        else:
            print("✗ Falló la conexión con Binance")
            return
    except Exception as e:
        print(f"✗ Error al conectar con Binance: {str(e)}")
        return
    
    # Prueba 1: Obtener tiempo del servidor
    try:
        print("\nObteniendo tiempo del servidor...")
        server_time = binance.get_server_time()
        dt = datetime.fromtimestamp(server_time/1000)
        print(f"✓ Tiempo del servidor Binance: {dt}")
    except Exception as e:
        print(f"✗ Error al obtener tiempo del servidor: {str(e)}")
    
    # Prueba 2: Obtener información del exchange (si existe el método)
    if hasattr(binance, 'get_exchange_info') and callable(getattr(binance, 'get_exchange_info')):
        try:
            print("\nObteniendo información del exchange...")
            exchange_info = binance.get_exchange_info()
            print(f"✓ Información del exchange obtenida: {type(exchange_info)}")
            if isinstance(exchange_info, dict):
                print(f"✓ Zona horaria: {exchange_info.get('timezone', 'No disponible')}")
                print(f"✓ Tiempo del servidor: {datetime.fromtimestamp(exchange_info.get('serverTime', 0)/1000)}")
        except Exception as e:
            print(f"✗ Error al obtener información del exchange: {str(e)}")
    else:
        print("\nℹ️ Método get_exchange_info no disponible")
    
    # Prueba 3: Información de cuenta (si tiene API key y existe el método)
    if API_KEY and API_SECRET and hasattr(binance, 'get_account_info') and callable(getattr(binance, 'get_account_info')):
        try:
            print("\nObteniendo información de la cuenta...")
            account_info = binance.get_account_info()
            print(f"✓ Información de cuenta obtenida: {type(account_info)}")
            if isinstance(account_info, dict):
                permissions = account_info.get('permissions', [])
                print(f"✓ Permisos de la cuenta: {', '.join(permissions)}")
        except Exception as e:
            print(f"✗ Error al obtener información de la cuenta: {str(e)}")
    else:
        print("\nℹ️ Saltando prueba de cuenta (credenciales no proporcionadas o método no disponible)")
    
    # Desconectar
    print("\nDesconectando...")
    try:
        binance.disconnect()
        print("✓ Desconectado correctamente de Binance")
    except Exception as e:
        print(f"✗ Error al desconectar: {str(e)}")
    
    print("\n=== FIN DEL TEST DE BINANCE ===")

if __name__ == "__main__":
    test_binance_connector()
