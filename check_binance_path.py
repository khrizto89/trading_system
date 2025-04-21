# check_binance_path.py
from services.data_service.binance_connector import BinanceConnector
import inspect

# Imprimir la ruta exacta del archivo importado
file_path = inspect.getfile(BinanceConnector)
print(f"Archivo importado: {file_path}")

# Ver todos los atributos y métodos disponibles
attrs = [attr for attr in dir(BinanceConnector) if not attr.startswith('_')]
print(f"\nAtributos y métodos disponibles ({len(attrs)}):")
for attr in attrs:
    print(f"- {attr}")

# Crear instancia mínima y verificar sus atributos
instance = BinanceConnector(testnet=True)
instance_attrs = [attr for attr in dir(instance) if not attr.startswith('_')]
print(f"\nAtributos y métodos de la instancia ({len(instance_attrs)}):")
for attr in instance_attrs:
    value = getattr(instance, attr)
    if not callable(value):
        print(f"- {attr}: {value}")
    else:
        print(f"- {attr}() [método]")