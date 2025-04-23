"""Módulo para manejar la cámara."""

import subprocess
import io
from PIL import Image
import pygame
import threading
import time
from config import CAMERA_WIDTH, CAMERA_HEIGHT

class Camera:
    """Clase para manejar la cámara CSI."""
    
    def __init__(self):
        """Inicializa la cámara."""
        self.process = None
        self.buffer = b''
        self.running = False
        self.frame = None
        self.frame_lock = threading.Lock()
        self.start_marker = b'\xff\xd8'  # Inicio de JPEG
        self.end_marker = b'\xff\xd9'    # Fin de JPEG
    
    def start(self):
        """Inicia la captura de video."""
        if self.process is not None:
            return
        
        try:
            # Iniciar libcamera-vid para generar frames JPEG
            cmd = [
                "libcamera-vid",
                "--width", str(CAMERA_WIDTH),
                "--height", str(CAMERA_HEIGHT),
                "--codec", "mjpeg",
                "--segment", "1",
                "--output", "-",
                "--nopreview"
            ]
            
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            self.running = True
            
            # Iniciar hilo para procesar frames
            threading.Thread(target=self._process_frames, daemon=True).start()
            
            # Esperar a que se capture al menos un frame
            timeout = 5  # segundos
            start_time = time.time()
            while self.frame is None:
                time.sleep(0.1)
                if time.time() - start_time > timeout:
                    raise TimeoutError("Tiempo de espera agotado para capturar el primer frame")
        
        except Exception as e:
            print(f"Error al iniciar la cámara: {e}")
            self.stop()
            raise
    
    def _process_frames(self):
        """Procesa los frames de la cámara."""
        while self.running and self.process:
            try:
                # Leer datos
                data = self.process.stdout.read(4096)
                if not data:
                    break
                
                # Agregar al buffer
                self.buffer += data
                
                # Buscar frames JPEG completos
                start_idx = self.buffer.find(self.start_marker)
                if start_idx != -1:
                    end_idx = self.buffer.find(self.end_marker, start_idx)
                    if end_idx != -1:
                        # Extraer frame completo
                        frame_data = self.buffer[start_idx:end_idx+2]
                        self.buffer = self.buffer[end_idx+2:]
                        
                        # Convertir a imagen PIL
                        try:
                            image = Image.open(io.BytesIO(frame_data)).convert('RGB')
                            
                            # Convertir a superficie pygame
                            mode = image.mode
                            size = image.size
                            data = image.tobytes()
                            with self.frame_lock:
                                self.frame = pygame.image.fromstring(data, size, mode)
                        except Exception as e:
                            print(f"Error al procesar frame: {e}")
            
            except Exception as e:
                print(f"Error en el procesamiento de frames: {e}")
                break
        
        self.running = False
    
    def get_frame(self):
        """Obtiene el frame actual."""
        with self.frame_lock:
            if self.frame:
                return self.frame.copy()
            return None
    
    def capture_image(self):
        """Captura una imagen y la devuelve como bytes."""
        with self.frame_lock:
            if self.frame:
                # Convertir superficie pygame a bytes
                pygame_surface = self.frame.copy()
                image_data = pygame.image.tostring(pygame_surface, 'RGB')
                image = Image.frombytes('RGB', pygame_surface.get_size(), image_data)
                
                # Convertir a bytes JPEG
                byte_io = io.BytesIO()
                image.save(byte_io, format='JPEG')
                byte_io.seek(0)
                return byte_io
            return None
    
    def stop(self):
        """Detiene la captura de video."""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process = None
        self.frame = None
        self.buffer = b''