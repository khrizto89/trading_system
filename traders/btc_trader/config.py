# Configuración para BTC trader

from core.utils.config import ConfigManager

class BTCTraderConfig:
    """Configuración específica para el trader de Bitcoin."""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.default_config = {
            "timeframes": ["1m", "5m", "15m", "1h", "4h"],
            "analysis_periods": {
                "short_term": 14,
                "medium_term": 50,
                "long_term": 200
            },
            "position_size": 0.01,  # Tamaño de posición predeterminado (en BTC)
            "risk_limits": {
                "max_drawdown": 0.05,  # Máximo 5% de pérdida
                "stop_loss": 0.02,  # Stop loss en 2%
                "take_profit": 0.05  # Take profit en 5%
            },
            "preferred_models": ["lstm", "transformer"],
            "strategy_params": {
                "momentum_threshold": 0.1,
                "volatility_buffer": 0.02
            },
            "volatility_optimized_defaults": {
                "sma_window": 20,
                "rsi_window": 14,
                "atr_multiplier": 2
            }
        }
        self.config_manager.update_from_dict(self.default_config)

    def get_config(self):
        """Devuelve la configuración completa."""
        return self.config_manager.get_all()

    def update_config(self, updates):
        """Actualiza dinámicamente la configuración."""
        self.config_manager.update_from_dict(updates)

    def integrate_with_global_config(self, global_config):
        """Integra con la configuración global."""
        self.config_manager.integrate_with_components(global_config)
