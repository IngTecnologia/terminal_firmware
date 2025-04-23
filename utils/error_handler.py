"""Manejo de errores en la aplicación."""

import sys
import traceback
import logging
import os
from datetime import datetime

def setup_error_handling():
    """Configura el manejo de errores global."""
    # Configurar logging
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'terminal.log')
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configurar handler para excepciones no manejadas
    def exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logging.error("Excepción no manejada:", exc_info=(exc_type, exc_value, exc_traceback))
        print("Se ha producido un error. Consulte el archivo de registro para más detalles.")
    
    sys.excepthook = exception_handler
    
    logging.info("Sistema iniciado")
    return True