from core.utils.config import ConfigManager

class ETHTraderConfig:
    """Configuración específica para el trader de Ethereum."""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.default_config = {
            "timeframes": ["1m", "5m", "15m", "1h", "4h"],
            "analysis_periods": {
                "short_term": 12,
                "medium_term": 48,
                "long_term": 120
            },
            "position_size": 0.05,  # Tamaño de posición predeterminado (en ETH)
            "risk_limits": {
                "max_drawdown": 0.06,  # Máximo 6% de pérdida
                "stop_loss": 0.025,  # Stop loss en 2.5%
                "take_profit": 0.06  # Take profit en 6%
            },
            "preferred_models": ["transformer", "lstm"],
            "strategy_params": {
                "momentum_threshold": 0.12,
                "volatility_buffer": 0.025
            },
            "eth_btc_correlation_defaults": {
                "correlation_window": 30,
                "correlation_threshold": 0.8
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
