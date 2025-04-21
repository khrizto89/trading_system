import os
import sys
import time
import signal
import logging

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('trading_system')

# Variables globales
running = True

def signal_handler(sig, frame):
    """Maneja señales para detener el sistema."""
    global running
    logger.info("Señal recibida. Deteniendo el sistema...")
    running = False

def main():
    """Función principal."""
    # Registrar handlers de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Sistema iniciado")
    
    try:
        # Ciclo simple
        for i in range(5):
            if not running:
                break
            logger.info(f"Iteración {i+1}")
            time.sleep(1)
    finally:
        logger.info("Sistema detenido")

if __name__ == "__main__":
    main()