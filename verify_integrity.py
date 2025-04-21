import os
import importlib
import logging
from pathlib import Path

# Configurar logger
logging.basicConfig(
    filename="module_integrity.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ModuleIntegrity")

def find_python_modules(base_dir):
    """Encuentra todos los módulos Python en el directorio base."""
    modules = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                relative_path = os.path.relpath(os.path.join(root, file), base_dir)
                module_name = relative_path.replace(os.sep, ".").replace(".py", "")
                # Asegúrate de que las rutas sean correctas
                if module_name.startswith("core.services"):
                    module_name = module_name.replace("core.services", "services")
                modules.append(module_name)
    return modules

def check_imports(modules):
    """Intenta importar cada módulo y registra errores."""
    logger.info("Iniciando verificación de módulos...")
    for module in modules:
        try:
            importlib.import_module(module)
            logger.info(f"Módulo importado correctamente: {module}")
        except ImportError as e:
            logger.error(f"Error al importar el módulo {module}: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al importar el módulo {module}: {e}")

def check_circular_dependencies(modules):
    """Verifica dependencias circulares entre módulos."""
    logger.info("Verificando dependencias circulares...")
    try:
        for module in modules:
            importlib.import_module(module)
        logger.info("No se detectaron dependencias circulares.")
    except Exception as e:
        logger.error(f"Dependencia circular detectada: {e}")

def main():
    """Punto de entrada principal del script."""
    base_dir = Path(__file__).parent
    logger.info("Iniciando verificación de integridad del sistema...")
    
    # Encontrar todos los módulos Python
    modules = find_python_modules(base_dir)
    logger.info(f"Se encontraron {len(modules)} módulos para verificar.")
    
    # Verificar importaciones
    check_imports(modules)
    
    # Verificar dependencias circulares
    check_circular_dependencies(modules)
    
    logger.info("Verificación de integridad completada.")

if __name__ == "__main__":
    main()
