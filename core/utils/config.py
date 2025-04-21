from typing import Dict, Any

class ConfigManager:
    """Gestión de configuración."""

    def __init__(self):
        self.config = {}

    def get_all(self) -> Dict[str, Any]:
        """Obtiene todas las configuraciones actuales."""
        return self.config

    def update_from_dict(self, config_updates: Dict[str, Any]):
        """Actualiza dinámicamente la configuración desde un diccionario."""
        self.config.update(config_updates)

    def validate_schema(self, schema: Dict[str, Any]):
        """Valida la configuración actual contra un esquema."""
        for key, value_type in schema.items():
            if key not in self.config:
                raise ValueError(f"Falta la clave requerida en la configuración: {key}")
            if not isinstance(self.config[key], value_type):
                raise TypeError(f"El valor de '{key}' debe ser de tipo {value_type}, pero es {type(self.config[key])}.")

    def integrate_with_components(self, component):
        """Integra configuraciones con un componente del sistema."""
        if hasattr(component, "configure"):
            component.configure(self.config)
        else:
            raise AttributeError(f"El componente {component} no soporta integración de configuración.")
