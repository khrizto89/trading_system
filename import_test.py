"""Prueba todas las importaciones críticas del sistema"""
import sys

def test_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name} importado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error importando {module_name}: {e}")
        return False

# Prueba módulos estándar
std_modules = ['os', 'sys', 'time', 'signal', 'logging']
print("== Probando módulos estándar ==")
for module in std_modules:
    test_import(module)

# Prueba módulos del proyecto
project_modules = [
    'core.utils.logging',
    'core.models.model_manager',
    'traders.btc_trader.config',
    'traders.eth_trader.config',
    'traders.template.template_trader'
]
print("\n== Probando módulos del proyecto ==")
for module in project_modules:
    test_import(module)

print("\nPruebas completadas")