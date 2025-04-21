import os
import json
import logging
from dotenv import load_dotenv

class EnvironmentLoader:
    """Cargador de variables de entorno y configuración."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.config = {}
    
    def load_env_file(self):
        """Carga variables desde archivo .env"""
        if self.logger:
            self.logger.info("Cargando variables de entorno desde .env")
        
        # Cargar variables de .env si existe
        if os.path.exists(".env"):
            load_dotenv()
            return True
        else:
            if self.logger:
                self.logger.warning("Archivo .env no encontrado")
            return False
    
    def load_config_file(self, filename="config.json"):
        """Carga configuración desde archivo JSON"""
        if self.logger:
            self.logger.info(f"Cargando configuración desde {filename}")
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.config = json.load(f)
            return True
        else:
            if self.logger:
                self.logger.warning(f"Archivo {filename} no encontrado")
            return False
    
    def load_environment(self, environment="development"):
        """Carga configuración específica al entorno"""
        if self.logger:
            self.logger.info(f"Configurando entorno: {environment}")
        
        # Sobreescribir valores de configuración con variables de entorno
        
        # Binance
        if 'BINANCE_API_KEY' in os.environ:
            self._ensure_config_section('binance')
            self.config['binance']['api_key'] = os.environ['BINANCE_API_KEY']
        
        if 'BINANCE_API_SECRET' in os.environ:
            self._ensure_config_section('binance')
            self.config['binance']['api_secret'] = os.environ['BINANCE_API_SECRET']
        
        if 'BINANCE_TESTNET' in os.environ:
            self._ensure_config_section('binance')
            self.config['binance']['testnet'] = os.environ['BINANCE_TESTNET'].lower() == 'true'
        
        # Base de datos
        if 'DATABASE_PATH' in os.environ:
            self._ensure_config_section('database')
            self.config['database']['path'] = os.environ['DATABASE_PATH']
        
        # Modo de trading
        if 'TRADING_MODE' in os.environ:
            self.config['trading_mode'] = os.environ['TRADING_MODE']
        
        return True
    
    def _ensure_config_section(self, section):
        """Asegura que existe una sección en la configuración"""
        if section not in self.config:
            self.config[section] = {}
    
    def validate_critical_keys(self, keys):
        """Valida que existan claves críticas en la configuración"""
        missing_keys = []
        
        for key in keys:
            # Manejar claves anidadas (con punto)
            if '.' in key:
                parts = key.split('.')
                section = self.config
                found = True
                
                for part in parts:
                    if isinstance(section, dict) and part in section:
                        section = section[part]
                    else:
                        found = False
                        break
                
                if not found:
                    missing_keys.append(key)
            else:
                if key not in self.config:
                    missing_keys.append(key)
        
        if missing_keys and self.logger:
            self.logger.warning(f"Claves críticas faltantes: {', '.join(missing_keys)}")
        
        return len(missing_keys) == 0
    
    def manage_binance_credentials(self):
        """Gestiona las credenciales de Binance de manera segura"""
        if self.logger:
            self.logger.info("Gestionando credenciales de Binance")
        
        # Verificar si tenemos credenciales
        binance_config = self.config.get('binance', {})
        api_key = binance_config.get('api_key', '')
        api_secret = binance_config.get('api_secret', '')
        testnet = binance_config.get('testnet', True)
        
        if not api_key or not api_secret:
            # Si no hay credenciales, advertir pero continuar
            if self.logger:
                self.logger.warning("Credenciales de Binance no configuradas. "
                                    "El sistema funcionará en modo simulado o paper trading.")
        else:
            # Verificar si estamos en testnet
            if testnet:
                if self.logger:
                    self.logger.info("Usando Binance Testnet")
            else:
                # Advertir cuando se usan credenciales de producción
                if self.logger:
                    self.logger.warning("ATENCIÓN: Usando Binance Producción con credenciales reales!")
        
        return True
    
    def get_config(self):
        """Obtiene la configuración actual"""
        return self.config