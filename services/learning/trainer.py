# Entrenamiento básico

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import TimeSeriesSplit
from skopt import BayesSearchCV
import matplotlib.pyplot as plt
import numpy as np
import os
from torch.cuda.amp import autocast, GradScaler

class Trainer:
    def __init__(self, model_manager, logger):
        """
        Inicializa el entrenador de modelos.
        :param model_manager: Instancia de ModelManager para gestionar modelos.
        :param logger: Logger para registrar eventos.
        """
        self.model_manager = model_manager
        self.logger = logger

    def check_model_performance(self, model_name, recent_data, threshold=0.6):
        """
        Verifica si el modelo necesita reentrenamiento.
        
        Args:
            model_name: Nombre del modelo
            recent_data: Datos recientes para evaluación
            threshold: Umbral mínimo de precisión
            
        Returns:
            bool: True si el modelo necesita reentrenamiento
        """
        # Dividir datos en features y target
        features = self._prepare_features(recent_data)
        target = self._prepare_target(recent_data)
        
        # Evaluar modelo actual
        metrics = self.model_manager.evaluate_model(model_name, features, target)
        
        # Verificar si el rendimiento está por debajo del umbral
        if metrics and metrics['direction_accuracy'] < threshold:
            self.logger.warning(f"Modelo {model_name} por debajo del umbral de rendimiento. Recomendado reentrenamiento.")
            return True
        
        return False

    def retrain_model(self, model_name, training_data):
        """
        Reentrena un modelo con nuevos datos.
        
        Args:
            model_name: Nombre del modelo
            training_data: Datos para reentrenamiento
            
        Returns:
            bool: True si el reentrenamiento fue exitoso
        """
        self.logger.info(f"Iniciando reentrenamiento de {model_name}")
        
        # Preparar datos
        features = self._prepare_features(training_data)
        target = self._prepare_target(training_data)
        
        # Dividir en train/validation
        split_idx = int(len(features) * 0.8)
        train_features, val_features = features[:split_idx], features[split_idx:]
        train_target, val_target = target[:split_idx], target[split_idx:]
        
        # Obtener modelo
        model = self.model_manager.get_model(model_name)
        if not model:
            self.logger.error(f"Modelo {model_name} no encontrado")
            return False
        
        # Reentrenar
        try:
            model.fit(train_features, train_target, validation_data=(val_features, val_target))
            
            # Evaluar nuevo rendimiento
            new_metrics = self.model_manager.evaluate_model(model_name, val_features, val_target)
            self.logger.info(f"Reentrenamiento completado. Nuevas métricas: {new_metrics}")
            
            # Guardar modelo actualizado
            self.model_manager.save_model(model_name)
            
            return True
        except Exception as e:
            self.logger.error(f"Error en reentrenamiento: {e}")
            return False

    def _prepare_features(self, data):
        """
        Prepara las características (features) a partir de los datos.
        :param data: Datos de entrada.
        :return: Features procesadas.
        """
        # Implementar lógica para extraer características
        return data.drop(columns=["target"])

    def _prepare_target(self, data):
        """
        Prepara los valores objetivo (target) a partir de los datos.
        :param data: Datos de entrada.
        :return: Valores objetivo.
        """
        # Implementar lógica para extraer el target
        return data["target"]
