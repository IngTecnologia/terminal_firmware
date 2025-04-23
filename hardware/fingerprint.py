"""Módulo para manejar el lector de huellas."""

import serial
import time
import threading
from config import FINGERPRINT_PORT, FINGERPRINT_BAUDRATE

class Fingerprint:
    """Clase para manejar el lector de huellas AS608."""
    
    def __init__(self):
        """Inicializa el lector de huellas."""
        self.serial = None
        self.is_connected = False
        self.callback = None
        self.scanning = False
        self.scan_thread = None
    
    def connect(self):
        """Conecta con el lector de huellas."""
        try:
            self.serial = serial.Serial(
                FINGERPRINT_PORT,
                FINGERPRINT_BAUDRATE,
                timeout=1
            )
            self.is_connected = True
            print("Lector de huellas conectado")
            return True
        except Exception as e:
            print(f"Error al conectar con el lector de huellas: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Desconecta el lector de huellas."""
        self.stop_scan()
        if self.serial:
            self.serial.close()
            self.serial = None
        self.is_connected = False
    
    def start_scan(self, callback):
        """Inicia el escaneo de huellas."""
        if not self.is_connected:
            if not self.connect():
                return False
        
        if self.scanning:
            return True
        
        self.callback = callback
        self.scanning = True
        self.scan_thread = threading.Thread(target=self._scan_thread, daemon=True)
        self.scan_thread.start()
        return True
    
    def _scan_thread(self):
        """Hilo para escanear huellas."""
        while self.scanning and self.serial:
            try:
                # Comando para capturar imagen (esto varía según la biblioteca real del AS608)
                # Esto es un ejemplo simplificado
                command = bytearray([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05])
                self.serial.write(command)
                time.sleep(0.5)
                
                # Leer respuesta
                response = self.serial.read(12)
                
                # Procesar respuesta
                # Esto es un ejemplo simplificado, en la realidad
                # tendrías que interpretar la respuesta según el protocolo del AS608
                if len(response) >= 12 and response[9] == 0x00:
                    # Simular identificación exitosa
                    # En un sistema real, aquí harías la búsqueda de la huella
                    # en la base de datos y obtendrías la cédula asociada
                    if self.callback:
                        # Simular una cédula encontrada (en la realidad, esto vendría de tu base de datos)
                        cedula = "123456789"
                        self.callback(True, cedula)
                        self.scanning = False
                        break
            
            except Exception as e:
                print(f"Error al escanear huella: {e}")
                time.sleep(1)
        
        print("Escaneo de huellas detenido")
    
    def stop_scan(self):
        """Detiene el escaneo de huellas."""
        self.scanning = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1)
        self.scan_thread = None
    
    def register_fingerprint(self, finger_id):
        """Registra una nueva huella."""
        # Implementar el registro de huellas según el protocolo del AS608
        # Este es un método más complejo que requiere varios pasos:
        # 1. Capturar la huella dos veces para verificación
        # 2. Generar la plantilla
        # 3. Almacenar la plantilla en el ID especificado
        # Para simplificar, retornamos éxito simulado
        return True