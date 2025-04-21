#!/usr/bin/env python3
"""
Script de diagnóstico para identificar todos los errores y dependencias
en el sistema de trading.
"""

import os
import sys
import importlib
import inspect
import time
import traceback

def print_header(text):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def check_module_imports(module_name):
    """Verifica si un módulo puede ser importado y sus clases accedidas."""
    results = {}
    
    try:
        # Intentar importar el módulo
        module = importlib.import_module(module_name)
        results["module_import"] = True
        
        # Encontrar todas las clases en el módulo
        classes = {}
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module_name:
                classes[name] = True
        
        results["classes"] = classes
        return True, results, None
    
    except Exception as e:
        # Capturar el error completo
        error_trace = traceback.format_exc()
        return False, {}, error_trace

def check_core_components():
    """Verifica los componentes core del sistema."""
    print_header("VERIFICANDO COMPONENTES CORE")
    
    core_modules = [
        # Utils
        "core.utils.logging",
        "core.utils.config",
        "core.utils.indicators",
        
        # Models
        "core.models.ensembler",
        "core.models.model_manager",
        "core.models.architectures.lstm_model",
        "core.models.architectures.transformer_model",
        "core.models.architectures.baseline_model",
        
        # Features
        "core.features.feature_extractor",
        "core.features.market_features",
        "core.features.technical_features",
        
        # Strategy
        "core.strategy.signal_generator",
        "core.strategy.position_manager",
        "core.strategy.risk_manager",
        
        # Optimization
        "core.optimization.gpu_optimizer",
        "core.optimization.gpu_utils",
    ]
    
    for module_name in core_modules:
        success, results, error = check_module_imports(module_name)
        
        if success:
            print(f"✅ {module_name}")
            if results.get("classes"):
                print(f"   Clases disponibles: {', '.join(results['classes'].keys())}")
        else:
            print(f"❌ {module_name}")
            print(f"   Error: {error.splitlines()[-1]}")

def check_services():
    """Verifica los servicios del sistema."""
    print_header("VERIFICANDO SERVICIOS")
    
    service_modules = [
        # Data service
        "services.data_service.binance_connector",
        "services.data_service.data_processor",
        "services.data_service.database",
        
        # Monitor service
        "services.monitor_service.system_monitor",
        "services.monitor_service.trading_monitor",
        "services.monitor_service.dashboard",
        
        # API service
        "services.api_service.rest_api",
        "services.api_service.notification",
        
        # Learning
        "services.learning.trainer",
        "services.learning.backtesting",
    ]
    
    for module_name in service_modules:
        success, results, error = check_module_imports(module_name)
        
        if success:
            print(f"✅ {module_name}")
            if results.get("classes"):
                print(f"   Clases disponibles: {', '.join(results['classes'].keys())}")
        else:
            print(f"❌ {module_name}")
            print(f"   Error: {error.splitlines()[-1]}")

def check_traders():
    """Verifica los traders del sistema."""
    print_header("VERIFICANDO TRADERS")
    
    trader_modules = [
        "traders.trader_base",
        "traders.btc_trader.btc_trader",
        "traders.btc_trader.config",
        "traders.eth_trader.eth_trader",
        "traders.eth_trader.config",
        "traders.template.template_trader",
        "traders.template.config",
    ]
    
    for module_name in trader_modules:
        success, results, error = check_module_imports(module_name)
        
        if success:
            print(f"✅ {module_name}")
            if results.get("classes"):
                print(f"   Clases disponibles: {', '.join(results['classes'].keys())}")
        else:
            print(f"❌ {module_name}")
            print(f"   Error: {error.splitlines()[-1]}")

def check_specific_class(module_name, class_name):
    """Verifica si una clase específica puede ser importada correctamente."""
    try:
        module = importlib.import_module(module_name)
        class_obj = getattr(module, class_name)
        return True, None
    except Exception as e:
        error_trace = traceback.format_exc()
        return False, error_trace

def check_main_imports():
    """Verifica las importaciones específicas usadas en main.py"""
    print_header("VERIFICANDO IMPORTACIONES DE MAIN.PY")
    
    main_imports = [
        ("core.utils.logging", "TradingLogger"),
        ("core.utils.config", "ConfigManager"),
        ("core.models.model_manager", "ModelManager"),
        ("core.models.ensembler", "ModelEnsembler"),  # Esta es la que falla
        ("core.features.feature_extractor", "FeatureExtractor"),
        ("core.strategy.signal_generator", "SignalGenerator"),
        ("core.strategy.position_manager", "PositionManager"),
        ("core.strategy.risk_manager", "RiskManager"),
        ("core.optimization.gpu_optimizer", "GPUOptimizer"),
        ("services.data_service.binance_connector", "BinanceConnector"),
        ("services.data_service.data_processor", "DataProcessor"),
        ("services.data_service.database", "Database"),
        ("services.monitor_service.system_monitor", "SystemMonitor"),
        ("services.monitor_service.trading_monitor", "TradingMonitor"),
        ("services.api_service.notification", "NotificationService"),
        ("services.learning.backtesting", "BacktestingEngine"),
        ("traders.trader_base", "Trader"),
        ("traders.btc_trader.btc_trader", "BTCTrader"),
        ("traders.btc_trader.config", "BTCTraderConfig"),
        ("traders.eth_trader.eth_trader", "ETHTrader"),
        ("traders.eth_trader.config", "ETHTraderConfig"),
    ]
    
    for module_name, class_name in main_imports:
        success, error = check_specific_class(module_name, class_name)
        
        if success:
            print(f"✅ from {module_name} import {class_name}")
        else:
            print(f"❌ from {module_name} import {class_name}")
            print(f"   Error: {error.splitlines()[-1]}")

def suggest_fixes():
    """Sugiere correcciones para problemas comunes."""
    print_header("SUGERENCIAS DE SOLUCIÓN")
    
    print("1. Para errores de clase no encontrada (como ModelEnsembler):")
    print("   - Revisa el nombre exacto de la clase en el archivo correspondiente")
    print("   - Modifica main.py para usar el nombre correcto")
    print("   - Alternativa: renombra la clase en el archivo original")
    
    print("\n2. Para errores de módulo no encontrado:")
    print("   - Verifica que el archivo existe en la ubicación correcta")
    print("   - Asegúrate de que hay un archivo __init__.py en cada directorio")
    
    print("\n3. Para errores de importación en módulos del sistema:")
    print("   - Revisa las dependencias circulares (A importa B, B importa A)")
    print("   - Verifica que todas las dependencias estén instaladas")
    
    print("\n4. Solución rápida para main.py:")
    print("   - Modifica cada línea de importación problemática")
    print("   - Ejemplo: cambiar 'from X import Y' por 'import X' y usar 'X.Y'")

def check_python_environment():
    """Verifica el entorno Python."""
    print_header("INFORMACIÓN DEL ENTORNO PYTHON")
    
    print(f"Python versión: {sys.version}")
    print(f"Ruta del intérprete: {sys.executable}")
    print(f"Directorio de trabajo: {os.getcwd()}")
    
    try:
        import pip
        print(f"Pip versión: {pip.__version__}")
        
        # Listar paquetes relevantes
        relevant_packages = ["numpy", "pandas", "torch", "tensorflow", "matplotlib", "scikit-learn"]
        print("\nPaquetes relevantes:")
        for package in relevant_packages:
            try:
                pkg = importlib.import_module(package)
                version = getattr(pkg, "__version__", "versión desconocida")
                print(f"  ✅ {package}: {version}")
            except ImportError:
                print(f"  ❌ {package}: no instalado")
    
    except ImportError:
        print("No se pudo importar pip")

def main():
    """Función principal."""
    print_header("DIAGNÓSTICO DEL SISTEMA DE TRADING")
    print(f"Fecha y hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_python_environment()
    check_core_components()
    check_services()
    check_traders()
    check_main_imports()
    suggest_fixes()
    
    print("\n" + "=" * 80)
    print(" Diagnóstico completado. Usa esta información para resolver los problemas.")
    print("=" * 80)

if __name__ == "__main__":
    main()