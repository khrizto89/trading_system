import importlib
import sys

# List of dependencies to check
dependencies = [
    "os", "sys", "time", "signal", "logging", "json", "argparse", "datetime",
    "core.utils.logging", "core.utils.config", "core.models.model_manager",
    "core.models.ensembler", "core.features.feature_extractor",
    "core.strategy.signal_generator", "core.strategy.risk_manager",
    "core.optimization.gpu_optimizer", "services.data_service.data_processor",
    "services.data_service.database", "services.monitor_service.system_monitor",
    "services.monitor_service.trading_monitor", "services.api_service.notification",
    "services.learning.backtesting", "traders.trader_base",
    "traders.btc_trader.btc_trader", "traders.btc_trader.config",
    "traders.eth_trader.eth_trader", "traders.eth_trader.config", "load_env"
]

def check_dependencies(dependencies):
    missing_dependencies = []
    for dependency in dependencies:
        try:
            importlib.import_module(dependency)
            print(f"✓ {dependency} is available.")
        except ImportError:
            print(f"✗ {dependency} is missing.")
            missing_dependencies.append(dependency)
    return missing_dependencies

if __name__ == "__main__":
    print("Checking dependencies for main.py...\n")
    missing = check_dependencies(dependencies)
    if missing:
        print("\nThe following dependencies are missing:")
        for dep in missing:
            print(f"  - {dep}")
        sys.exit(1)
    else:
        print("\nAll dependencies are satisfied.")