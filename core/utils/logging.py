# Sistema de logs unificado

import logging
from logging.handlers import RotatingFileHandler

class TradingLogger:
    """Sistema de logging para el sistema de trading."""

    def __init__(self, log_file="trading_system.log", max_size=5 * 1024 * 1024, backup_count=3):
        """
        Inicializa el sistema de logging.
        :param log_file: Nombre del archivo de log.
        :param max_size: Tamaño máximo del archivo de log en bytes.
        :param backup_count: Número de archivos de respaldo.
        """
        self.logger = logging.getLogger("TradingSystem")
        self.logger.setLevel(logging.DEBUG)  # Cambiado a DEBUG para más detalles

        # Formateo personalizado
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Rotación de archivos de log
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_size, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        # Consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # Agregar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Loggers específicos para componentes clave
        self.model_logger = logging.getLogger("TradingSystem.Models")
        self.signal_logger = logging.getLogger("TradingSystem.Signals")
        self.model_logger.setLevel(logging.DEBUG)
        self.signal_logger.setLevel(logging.DEBUG)

    def get_logger(self):
        """Devuelve el logger configurado."""
        return self.logger

    def get_model_logger(self):
        """Devuelve el logger específico para modelos."""
        return self.model_logger

    def get_signal_logger(self):
        """Devuelve el logger específico para señales."""
        return self.signal_logger

    def log_trade(self, trade_info):
        """
        Log específico para operaciones de trading.
        :param trade_info: Diccionario con información de la operación.
        """
        self.logger.info(f"Trade ejecutado: {trade_info}")

    def log_error(self, error_message):
        """
        Log específico para errores críticos.
        :param error_message: Mensaje de error.
        """
        self.logger.error(f"Error crítico: {error_message}")

    def integrate_with_monitoring(self, monitoring_system):
        """
        Integra el sistema de logging con un sistema de monitoreo.
        :param monitoring_system: Objeto del sistema de monitoreo.
        """
        if hasattr(monitoring_system, "send_notification"):
            self.logger.addHandler(MonitoringHandler(monitoring_system))
        else:
            self.logger.warning("El sistema de monitoreo no soporta integración.")

class MonitoringHandler(logging.Handler):
    """Handler para enviar logs al sistema de monitoreo."""

    def __init__(self, monitoring_system):
        super().__init__()
        self.monitoring_system = monitoring_system

    def emit(self, record):
        log_entry = self.format(record)
        self.monitoring_system.send_notification(log_entry)
