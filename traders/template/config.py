# Configuración de plantilla

from core.utils.config import ConfigManager

class TemplateTraderConfig:
    """Plantilla de configuración para nuevos traders."""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.default_config = {
            "timeframes": ["1m", "5m", "15m", "1h", "4h"],  # Marcos temporales estándar
            "analysis_periods": {
                "short_term": 14,  # Periodo corto para análisis técnico
                "medium_term": 50,  # Periodo medio para tendencias
                "long_term": 200  # Periodo largo para análisis macro
            },
            "position_size": 0.01,  # Tamaño de posición predeterminado
            "risk_limits": {
                "max_drawdown": 0.05,  # Máximo porcentaje de pérdida
                "stop_loss": 0.02,  # Stop loss predeterminado
                "take_profit": 0.05  # Take profit predeterminado
            },
            "preferred_models": ["baseline"],  # Modelos predeterminados
            "strategy_params": {
                "momentum_threshold": 0.1,  # Umbral de momentum
                "volatility_buffer": 0.02  # Buffer para volatilidad
            },
            "examples": {
                "low_risk": {
                    "position_size": 0.005,
                    "risk_limits": {"max_drawdown": 0.03, "stop_loss": 0.01, "take_profit": 0.03}
                },
                "high_risk": {
                    "position_size": 0.02,
                    "risk_limits": {"max_drawdown": 0.1, "stop_loss": 0.05, "take_profit": 0.1}
                }
            }
        }
        self.config_manager.update_from_dict(self.default_config)

    def get_config(self):
        """Devuelve la configuración completa."""
        return self.config_manager.get_all()

    def update_config(self, updates):
        """Actualiza dinámicamente la configuración."""
        self.config_manager.update_from_dict(updates)

    def validate_config(self):
        """Valida los valores de configuración."""
        schema = {
            "timeframes": list,
            "analysis_periods": dict,
            "position_size": float,
            "risk_limits": dict,
            "preferred_models": list,
            "strategy_params": dict
        }
        self.config_manager.validate_schema(schema)

    def integrate_with_global_config(self, global_config):
        """Integra con la configuración global."""
        self.config_manager.integrate_with_components(global_config)

    def optimize_parameters(self):
        """Guía para optimización de parámetros."""
        print("Para optimizar parámetros, ajuste 'position_size' y 'risk_limits' según el perfil de riesgo.")
        print("Considere usar análisis histórico para ajustar 'strategy_params' y 'analysis_periods'.")
