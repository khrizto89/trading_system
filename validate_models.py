#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Validación específica de modelos de IA para el sistema de trading
Este script se centra exclusivamente en la validación de los modelos de IA,
incluyendo pruebas de rendimiento con diferentes conjuntos de datos.
"""

import os
import sys
import json
import time
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('modelos_validacion.log')
    ]
)
logger = logging.getLogger('ValidacionModelos')

# Asegurar que estamos en el directorio correcto
ROOT_DIR = Path(__file__).parent
os.chdir(ROOT_DIR)

# Intentar importar los módulos necesarios
try:
    # Importar componentes relacionados con modelos
    from core.models.model_manager import ModelManager
    from core.models.ensembler import Ensembler
    from core.utils.config import ConfigManager
    
    logger.info("Importaciones de módulos de modelos completadas con éxito")
except ImportError as e:
    logger.error(f"Error importando módulos de modelos: {e}")
    logger.error("Verificando estructura de directorios...")
    
    # Enumerar directorios para diagnóstico
    for root, dirs, files in os.walk('./core/models', topdown=True):
        logger.info(f"Directorio: {root}")
        logger.info(f"  Subdirectorios: {dirs}")
        logger.info(f"  Archivos: {[f for f in files if f.endswith('.py')]}")
    
    sys.exit(1)

class ModelValidator:
    """Clase para validar modelos de IA del sistema de trading"""
    
    def __init__(self, config_path='config.json'):
        logger.info("Iniciando validación de modelos de IA")
        
        # Cargar configuración
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info("Configuración cargada correctamente")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            self.config = {}
        
        # Inicializar gestor de modelos
        try:
            self.model_manager = ModelManager()
            logger.info("Gestor de modelos inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando gestor de modelos: {e}")
            sys.exit(1)
        
        # Inicializar ensembler
        try:
            self.ensembler = Ensembler()
            logger.info("Ensembler inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando ensembler: {e}")
            self.ensembler = None
    
    def list_available_models(self):
        """Listar modelos disponibles en el sistema"""
        logger.info("Listando modelos disponibles...")
        
        try:
            available_models = self.model_manager.list_available_models()
            logger.info(f"Modelos disponibles: {available_models}")
            return available_models
        except Exception as e:
            logger.error(f"Error listando modelos: {e}")
            return []
    
    def validate_model_architecture(self, model_name):
        """Validar arquitectura de un modelo específico"""
        logger.info(f"Validando arquitectura del modelo: {model_name}")
        
        try:
            # Cargar modelo
            model = self.model_manager.load_model(model_name)
            
            # Verificar tipo de modelo
            model_type = type(model).__name__
            logger.info(f"Tipo de modelo: {model_type}")
            
            # Verificar estructura interna
            if hasattr(model, 'summary'):
                logger.info("Resumen del modelo:")
                model.summary()
            
            # Verificar atributos y métodos
            methods = [method for method in dir(model) if not method.startswith('_') and callable(getattr(model, method))]
            logger.info(f"Métodos disponibles: {methods}")
            
            # Verificar si el modelo tiene método de predicción
            if 'predict' in methods:
                logger.info("El modelo tiene método de predicción: OK")
                return True
            else:
                logger.warning("El modelo no tiene método de predicción")
                return False
            
        except Exception as e:
            logger.error(f"Error validando arquitectura del modelo {model_name}: {e}")
            return False
    
    def validate_model_performance(self, model_name, test_data=None):
        """Validar rendimiento de un modelo con datos de prueba"""
        logger.info(f"Validando rendimiento del modelo: {model_name}")
        
        # Si no se proporcionan datos de prueba, generar datos sintéticos
        if test_data is None:
            logger.info("Generando datos sintéticos para prueba...")
            
            # Generar datos simulados de cripto (OHLCV)
            n_samples = 1000
            base_price = 20000.0  # Precio base para BTC
            
            # Simular movimiento de precios
            price_changes = np.random.normal(0, 1, n_samples) * 100
            close_prices = base_price + np.cumsum(price_changes)
            
            # Generar OHLCV
            test_data = pd.DataFrame({
                'timestamp': pd.date_range(start='2025-01-01', periods=n_samples, freq='1h'),
                'open': close_prices - np.random.random(n_samples) * 50,
                'high': close_prices + np.random.random(n_samples) * 50,
                'low': close_prices - np.random.random(n_samples) * 50,
                'close': close_prices,
                'volume': np.random.random(n_samples) * 10 + 5
            })
            
            # Agregar características técnicas básicas
            test_data['rsi_14'] = np.random.random(n_samples) * 100
            test_data['macd'] = np.random.random(n_samples) * 2 - 1
            test_data['bb_upper'] = close_prices + np.random.random(n_samples) * 200
            test_data['bb_lower'] = close_prices - np.random.random(n_samples) * 200
            
            logger.info(f"Datos sintéticos generados: {test_data.shape}")
        
        try:
            # Cargar modelo
            model = self.model_manager.load_model(model_name)
            
            # Realizar predicción
            start_time = time.time()
            predictions = model.predict(test_data)
            end_time = time.time()
            
            # Calcular tiempo de predicción
            prediction_time = end_time - start_time
            
            logger.info(f"Tiempo de predicción: {prediction_time:.4f} segundos")
            logger.info(f"Número de predicciones: {len(predictions)}")
            
            # Analizar distribución de predicciones
            if isinstance(predictions, (list, np.ndarray, pd.Series)):
                mean_pred = np.mean(predictions)
                std_pred = np.std(predictions)
                min_pred = np.min(predictions)
                max_pred = np.max(predictions)
                
                logger.info(f"Estadísticas de predicciones:")
                logger.info(f"  Media: {mean_pred:.4f}")
                logger.info(f"  Desviación estándar: {std_pred:.4f}")
                logger.info(f"  Mínimo: {min_pred:.4f}")
                logger.info(f"  Máximo: {max_pred:.4f}")
            
            # Verificar que las predicciones sean razonables
            if isinstance(predictions, (list, np.ndarray, pd.Series)):
                if min_pred < -10 or max_pred > 10:
                    logger.warning("Las predicciones tienen valores extremos, posible problema")
                else:
                    logger.info("Rango de predicciones razonable: OK")
            
            return {
                "success": True,
                "prediction_time": prediction_time,
                "predictions": predictions[:5].tolist() if isinstance(predictions, (list, np.ndarray, pd.Series)) else None,
                "stats": {
                    "mean": float(mean_pred) if 'mean_pred' in locals() else None,
                    "std": float(std_pred) if 'std_pred' in locals() else None,
                    "min": float(min_pred) if 'min_pred' in locals() else None,
                    "max": float(max_pred) if 'max_pred' in locals() else None
                }
            }
        
        except Exception as e:
            logger.error(f"Error validando rendimiento del modelo {model_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_ensemble(self, test_data=None):
        """Validar el sistema de ensemble con todos los modelos"""
        logger.info("Validando sistema de ensemble...")
        
        if self.ensembler is None:
            logger.error("Ensembler no disponible, saltando validación")
            return {
                "success": False,
                "error": "Ensembler no disponible"
            }
        
        # Si no hay datos de prueba, generar sintéticos (igual que en validate_model_performance)
        if test_data is None:
            n_samples = 1000
            base_price = 20000.0
            price_changes = np.random.normal(0, 1, n_samples) * 100
            close_prices = base_price + np.cumsum(price_changes)
            
            test_data = pd.DataFrame({
                'timestamp': pd.date_range(start='2025-01-01', periods=n_samples, freq='1h'),
                'open': close_prices - np.random.random(n_samples) * 50,
                'high': close_prices + np.random.random(n_samples) * 50,
                'low': close_prices - np.random.random(n_samples) * 50,
                'close': close_prices,
                'volume': np.random.random(n_samples) * 10 + 5,
                'rsi_14': np.random.random(n_samples) * 100,
                'macd': np.random.random(n_samples) * 2 - 1,
                'bb_upper': close_prices + np.random.random(n_samples) * 200,
                'bb_lower': close_prices - np.random.random(n_samples) * 200
            })
        
        try:
            # Realizar predicción con ensemble
            start_time = time.time()
            ensemble_preds = self.ensembler.predict(test_data)
            end_time = time.time()
            
            # Calcular tiempo de predicción
            prediction_time = end_time - start_time
            
            logger.info(f"Tiempo de predicción ensemble: {prediction_time:.4f} segundos")
            logger.info(f"Número de predicciones ensemble: {len(ensemble_preds)}")
            
            # Analizar distribución de predicciones
            mean_pred = np.mean(ensemble_preds)
            std_pred = np.std(ensemble_preds)
            min_pred = np.min(ensemble_preds)
            max_pred = np.max(ensemble_preds)
            
            logger.info(f"Estadísticas de predicciones ensemble:")
            logger.info(f"  Media: {mean_pred:.4f}")
            logger.info(f"  Desviación estándar: {std_pred:.4f}")
            logger.info(f"  Mínimo: {min_pred:.4f}")
            logger.info(f"  Máximo: {max_pred:.4f}")
            
            return {
                "success": True,
                "prediction_time": prediction_time,
                "predictions": ensemble_preds[:5].tolist() if isinstance(ensemble_preds, (list, np.ndarray, pd.Series)) else None,
                "stats": {
                    "mean": float(mean_pred),
                    "std": float(std_pred),
                    "min": float(min_pred),
                    "max": float(max_pred)
                }
            }
        
        except Exception as e:
            logger.error(f"Error validando ensemble: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_gpu_usage(self, model_name):
        """Validar uso de GPU con un modelo específico"""
        logger.info(f"Validando uso de GPU con modelo: {model_name}")
        
        try:
            # Verificar disponibilidad de GPU primero
            try:
                import torch
                gpu_available = torch.cuda.is_available()
                
                if gpu_available:
                    device_name = torch.cuda.get_device_name(0)
                    logger.info(f"GPU disponible: {device_name}")
                    
                    # Verificar memoria
                    total_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                    allocated_memory = torch.cuda.memory_allocated(0) / 1e9
                    
                    logger.info(f"Memoria GPU total: {total_memory:.2f} GB")
                    logger.info(f"Memoria GPU asignada: {allocated_memory:.2f} GB")
                    
                    # Preparar datos de prueba grandes para GPU
                    n_samples = 10000
                    n_features = 50
                    test_data = pd.DataFrame(
                        np.random.random((n_samples, n_features)),
                        columns=[f'feature_{i}' for i in range(n_features)]
                    )
                    
                    # Cargar modelo
                    model = self.model_manager.load_model(model_name)
                    
                    # Verificar si el modelo está en GPU
                    model_device = "Desconocido"
                    if hasattr(model, 'device'):
                        model_device = str(model.device)
                    logger.info(f"Dispositivo del modelo: {model_device}")
                    
                    # Realizar predicción y medir tiempo
                    torch.cuda.reset_peak_memory_stats()
                    start_time = time.time()
                    predictions = model.predict(test_data)
                    end_time = time.time()
                    
                    # Calcular métricas
                    prediction_time = end_time - start_time
                    peak_memory = torch.cuda.max_memory_allocated() / 1e9
                    
                    logger.info(f"Tiempo de predicción GPU: {prediction_time:.4f} segundos")
                    logger.info(f"Memoria GPU pico: {peak_memory:.2f} GB")
                    
                    return {
                        "success": True,
                        "gpu_available": True,
                        "device_name": device_name,
                        "prediction_time": prediction_time,
                        "peak_memory_gb": peak_memory,
                        "predictions_shape": predictions.shape if hasattr(predictions, 'shape') else len(predictions)
                    }
                else:
                    logger.warning("GPU no disponible. Utilizando CPU.")
                    return {
                        "success": True,
                        "gpu_available": False
                    }
            except ImportError:
                logger.warning("PyTorch no está instalado. No se puede verificar GPU.")
                return {
                    "success": False,
                    "error": "PyTorch no está instalado"
                }
        
        except Exception as e:
            logger.error(f"Error validando uso de GPU: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def benchmark_models(self):
        """Realizar benchmark de todos los modelos disponibles"""
        logger.info("Iniciando benchmark de modelos...")
        
        # Obtener modelos disponibles
        available_models = self.list_available_models()
        
        if not available_models:
            logger.error("No hay modelos disponibles para benchmark")
            return {}
        
        # Generar datos de prueba comunes
        n_samples = 1000
        base_price = 20000.0
        price_changes = np.random.normal(0, 1, n_samples) * 100
        close_prices = base_price + np.cumsum(price_changes)
        
        test_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2025-01-01', periods=n_samples, freq='1h'),
            'open': close_prices - np.random.random(n_samples) * 50,
            'high': close_prices + np.random.random(n_samples) * 50,
            'low': close_prices - np.random.random(n_samples) * 50,
            'close': close_prices,
            'volume': np.random.random(n_samples) * 10 + 5,
            'rsi_14': np.random.random(n_samples) * 100,
            'macd': np.random.random(n_samples) * 2 - 1,
            'bb_upper': close_prices + np.random.random(n_samples) * 200,
            'bb_lower': close_prices - np.random.random(n_samples) * 200
        })
        
        # Resultados del benchmark
        benchmark_results = {}
        
        # Ejecutar benchmark para cada modelo
        for model_name in available_models:
            logger.info(f"Benchmarking modelo: {model_name}")
            
            # Realizar múltiples predicciones para medir rendimiento
            n_runs = 5
            times = []
            
            try:
                # Cargar modelo
                model = self.model_manager.load_model(model_name)
                
                for i in range(n_runs):
                    start_time = time.time()
                    predictions = model.predict(test_data)
                    end_time = time.time()
                    times.append(end_time - start_time)
                
                # Calcular estadísticas
                avg_time = np.mean(times)
                std_time = np.std(times)
                
                logger.info(f"Tiempo medio de predicción: {avg_time:.4f} segundos")
                logger.info(f"Desviación estándar: {std_time:.4f} segundos")
                
                benchmark_results[model_name] = {
                    "avg_time": float(avg_time),
                    "std_time": float(std_time),
                    "min_time": float(np.min(times)),
                    "max_time": float(np.max(times)),
                    "predictions_sample": predictions[:3].tolist() if isinstance(predictions, (list, np.ndarray, pd.Series)) else None
                }
            
            except Exception as e:
                logger.error(f"Error en benchmark de {model_name}: {e}")
                benchmark_results[model_name] = {
                    "error": str(e)
                }
        
        # Benchmark del ensemble si está disponible
        if self.ensembler is not None:
            logger.info("Benchmarking ensemble...")
            
            n_runs = 5
            times = []
            
            try:
                for i in range(n_runs):
                    start_time = time.time()
                    predictions = self.ensembler.predict(test_data)
                    end_time = time.time()
                    times.append(end_time - start_time)
                
                # Calcular estadísticas
                avg_time = np.mean(times)
                std_time = np.std(times)
                
                logger.info(f"Tiempo medio de predicción ensemble: {avg_time:.4f} segundos")
                logger.info(f"Desviación estándar ensemble: {std_time:.4f} segundos")
                
                benchmark_results["ensemble"] = {
                    "avg_time": float(avg_time),
                    "std_time": float(std_time),
                    "min_time": float(np.min(times)),
                    "max_time": float(np.max(times)),
                    "predictions_sample": predictions[:3].tolist() if isinstance(predictions, (list, np.ndarray, pd.Series)) else None
                }
            
            except Exception as e:
                logger.error(f"Error en benchmark de ensemble: {e}")
                benchmark_results["ensemble"] = {
                    "error": str(e)
                }
        
        # Crear gráfico comparativo
        try:
            model_names = []
            avg_times = []
            
            for model_name, results in benchmark_results.items():
                if "avg_time" in results:
                    model_names.append(model_name)
                    avg_times.append(results["avg_time"])
            
            if model_names:
                plt.figure(figsize=(10, 6))
                bars = plt.bar(model_names, avg_times)
                
                plt.title('Tiempo de Predicción por Modelo')
                plt.ylabel('Tiempo (segundos)')
                plt.xticks(rotation=45)
                
                # Añadir etiquetas
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.003,
                            f"{height:.4f}", ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig('model_benchmark.png')
                logger.info("Gráfico comparativo guardado como 'model_benchmark.png'")
        
        except Exception as e:
            logger.error(f"Error creando gráfico: {e}")
        
        return benchmark_results
    
    def validate_and_report(self):
        """Validar todos los modelos y generar informe"""
        logger.info("Iniciando validación completa de modelos...")
        
        # Resultados de la validación
        validation_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "models": {},
            "ensemble": None,
            "benchmark": None
        }
        
        # 1. Listar modelos disponibles
        available_models = self.list_available_models()
        
        if not available_models:
            logger.error("No se encontraron modelos disponibles")
            return {
                "success": False,
                "error": "No se encontraron modelos disponibles"
            }
        
        # 2. Validar cada modelo
        for model_name in available_models:
            logger.info(f"Validando modelo: {model_name}")
            
            # Validar arquitectura
            architecture_valid = self.validate_model_architecture(model_name)
            
            # Validar rendimiento
            performance_results = self.validate_model_performance(model_name)
            
            # Validar uso de GPU
            gpu_results = self.validate_gpu_usage(model_name)
            
            # Guardar resultados
            validation_results["models"][model_name] = {
                "architecture_valid": architecture_valid,
                "performance": performance_results,
                "gpu": gpu_results
            }
        
        # 3. Validar ensemble
        if self.ensembler is not None:
            ensemble_results = self.validate_ensemble()
            validation_results["ensemble"] = ensemble_results
        
        # 4. Realizar benchmark
        benchmark_results = self.benchmark_models()
        validation_results["benchmark"] = benchmark_results
        
        # 5. Guardar resultados en archivo JSON
        with open('model_validation_results.json', 'w') as f:
            json.dump(validation_results, f, indent=4)
        
        # 6. Generar informe de texto
        with open('model_validation_report.txt', 'w') as f:
            f.write("-" * 50 + "\n")
            f.write("INFORME DE VALIDACIÓN DE MODELOS DE IA\n")
            f.write("-" * 50 + "\n")
            f.write(f"Fecha: {validation_results['timestamp']}\n\n")
            
            f.write(f"Modelos disponibles: {', '.join(available_models)}\n\n")
            
            f.write("RESULTADOS POR MODELO:\n")
            for model_name, results in validation_results["models"].items():
                f.write(f"\n--- Modelo: {model_name} ---\n")
                
                # Arquitectura
                f.write(f"Arquitectura válida: {'✓' if results['architecture_valid'] else '✗'}\n")
                
                # Rendimiento
                if results["performance"]["success"]:
                    f.write(f"Tiempo de predicción: {results['performance']['prediction_time']:.4f} segundos\n")
                    
                    if "stats" in results["performance"] and results["performance"]["stats"]["mean"] is not None:
                        stats = results["performance"]["stats"]
                        f.write(f"Estadísticas de predicciones:\n")
                        f.write(f"  Media: {stats['mean']:.4f}\n")
                        f.write(f"  Desviación: {stats['std']:.4f}\n")
                        f.write(f"  Mínimo: {stats['min']:.4f}\n")
                        f.write(f"  Máximo: {stats['max']:.4f}\n")
                else:
                    f.write(f"Error de rendimiento: {results['performance'].get('error', 'Desconocido')}\n")
                
                # GPU
                if results["gpu"]["success"]:
                    if results["gpu"].get("gpu_available", False):
                        f.write(f"GPU: {results['gpu']['device_name']}\n")
                        f.write(f"Tiempo de predicción GPU: {results['gpu']['prediction_time']:.4f} segundos\n")
                        f.write(f"Memoria GPU pico: {results['gpu'].get('peak_memory_gb', 'N/A')} GB\n")
                    else:
                        f.write("GPU no disponible, usando CPU\n")
                else:
                    f.write(f"Error de GPU: {results['gpu'].get('error', 'Desconocido')}\n")
            
            # Ensemble
            f.write("\n--- ENSEMBLE ---\n")
            if validation_results["ensemble"] and validation_results["ensemble"]["success"]:
                f.write(f"Tiempo de predicción: {validation_results['ensemble']['prediction_time']:.4f} segundos\n")
                
                if "stats" in validation_results["ensemble"]:
                    stats = validation_results["ensemble"]["stats"]
                    f.write(f"Estadísticas de predicciones:\n")
                    f.write(f"  Media: {stats['mean']:.4f}\n")
                    f.write(f"  Desviación: {stats['std']:.4f}\n")
                    f.write(f"  Mínimo: {stats['min']:.4f}\n")
                    f.write(f"  Máximo: {stats['max']:.4f}\n")
            else:
                f.write("Ensemble no disponible o error\n")
            
            # Benchmark
            f.write("\n--- BENCHMARK ---\n")
            for model_name, results in validation_results["benchmark"].items():
                if "error" not in results:
                    f.write(f"{model_name}: {results['avg_time']:.4f} segundos (±{results['std_time']:.4f})\n")
                else:
                    f.write(f"{model_name}: Error - {results['error']}\n")
            
            f.write("\n" + "-" * 50 + "\n")
            f.write("FIN DEL INFORME\n")
        
        logger.info("Informe de validación generado correctamente")
        
        return validation_results


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validación de modelos de IA para trading')
    parser.add_argument('--config', type=str, default='config.json', help='Ruta al archivo de configuración')
    parser.add_argument('--benchmark', action='store_true', help='Realizar benchmark de modelos')
    parser.add_argument('--gpu', action='store_true', help='Validar uso de GPU')
    parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Crear validador
    validator = ModelValidator(args.config)
    
    # Listar modelos
    models = validator.list_available_models()
    
    if not models:
        logger.error("No se encontraron modelos para validar")
        return 1
    
    # Realizar validaciones
    if args.benchmark:
        logger.info("Realizando benchmark de modelos...")
        results = validator.benchmark_models()
        logger.info("Benchmark completado")
    elif args.gpu:
        logger.info("Validando uso de GPU...")
        for model in models:
            validator.validate_gpu_usage(model)
        logger.info("Validación de GPU completada")
    else:
        # Validación completa
        logger.info("Realizando validación completa...")
        results = validator.validate_and_report()
        logger.info("Validación completa finalizada")
        
        # Mostrar estado final
        success_count = sum(1 for m in results["models"].values() 
                          if m["architecture_valid"] and m["performance"]["success"])
        
        logger.info(f"Modelos validados correctamente: {success_count} de {len(models)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())