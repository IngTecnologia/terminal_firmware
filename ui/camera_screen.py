"""Pantalla para captura facial."""

import pygame
import time
import threading
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TIMEOUT_FACIAL
from hardware.camera import Camera
from services.api_client import ApiClient

class CameraScreen:
    """Pantalla para captura y verificación facial."""
    
    def __init__(self, screen, app, cedula, tipo_registro):
        """Inicializa la pantalla de cámara."""
        self.screen = screen
        self.app = app
        self.cedula = cedula
        self.tipo_registro = tipo_registro
        
        # Colores
        self.bg_color = (240, 240, 240)
        self.text_color = (10, 10, 10)
        self.button_color = (120, 180, 220)
        self.button_hover_color = (140, 200, 240)
        
        # Fuentes
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        
        # Estados
        self.status = "Iniciando cámara..."
        self.camera_ready = False
        self.capturing = False
        self.sending = False
        self.result = None
        
        # Tiempo de inactividad
        self.start_time = time.time()
        self.timeout = TIMEOUT_FACIAL
        
        # Áreas de la pantalla
        self.preview_rect = pygame.Rect(
            (SCREEN_WIDTH - 240) // 2,
            80,
            240, 180
        )
        
        # Botones
        self.capture_button_rect = pygame.Rect(
            (SCREEN_WIDTH - 120) // 2,
            270,
            120, 40
        )
        self.capture_button_hover = False
        
        self.back_button_rect = pygame.Rect(
            10, 10, 80, 30
        )
        self.back_button_hover = False
        
        # Inicializar cámara en un hilo separado
        self.camera = None
        self.frame = None
        threading.Thread(target=self._init_camera, daemon=True).start()
        
        # Cliente API
        self.api_client = ApiClient()
        
        # Iniciar detección facial automática después de inicializar la cámara
        self.face_detection_active = False
        self.face_detect_thread = None
    
    def _init_camera(self):
        """Inicializa la cámara en un hilo separado."""
        try:
            self.camera = Camera()
            self.camera.start()
            self.status = "Cámara lista. Posicione su rostro"
            self.camera_ready = True
            
            # Iniciar detección facial automática
            self.face_detection_active = True
            self.face_detect_thread = threading.Thread(
                target=self._auto_face_detect,
                daemon=True
            )
            self.face_detect_thread.start()
            
        except Exception as e:
            self.status = f"Error: {str(e)}"
    
    def _auto_face_detect(self):
        """Detecta rostros automáticamente y captura cuando se detecta uno."""
        # En un sistema real, aquí se implementaría la detección facial.
        # Para simplificar, solo simulamos una espera y luego capturamos
        time.sleep(2)  # Simular tiempo de preparación
        
        if self.camera_ready and self.face_detection_active:
            self.status = "Rostro detectado. Capturando..."
            self._capture_and_verify()
    
    def _capture_and_verify(self):
        """Captura una imagen y la envía para verificación."""
        if not self.camera_ready or self.capturing or self.sending:
            return
        
        self.capturing = True
        try:
            # Capturar imagen
            image_data = self.camera.capture_image()
            if not image_data:
                self.status = "Error al capturar imagen"
                self.capturing = False
                return
            
            self.status = "Enviando para verificación..."
            self.sending = True
            
            # Enviar para verificación en un hilo separado
            threading.Thread(
                target=self._send_for_verification,
                args=(image_data,),
                daemon=True
            ).start()
            
        except Exception as e:
            self.status = f"Error al capturar: {str(e)}"
            self.capturing = False
    
    def _send_for_verification(self, image_data):
        """Envía la imagen para verificación facial."""
        try:
            success, result = self.api_client.verify_face(
                self.cedula,
                self.tipo_registro,
                image_data
            )
            
            if success and result.get("verified", False):
                self.status = "Verificación exitosa"
                self.result = result
            else:
                error_msg = result.get("error", "Verificación fallida")
                self.status = f"Error: {error_msg}"
            
            # Cambiar a pantalla de resultado después de un breve retraso
            time.sleep(1.5)
            
            # Detener cámara y procesos de detección
            self.face_detection_active = False
            if self.camera:
                self.camera.stop()
            
            # Cambiar a pantalla de resultado
            from ui.result_screen import ResultScreen
            self.app.change_screen(ResultScreen, success, result, self.cedula, self.tipo_registro)
            
        except Exception as e:
            self.status = f"Error: {str(e)}"
        finally:
            self.capturing = False
            self.sending = False
    
    def _on_back(self):
        """Maneja la pulsación del botón de volver."""
        # Detener procesos de cámara
        self.face_detection_active = False
        if self.camera:
            self.camera.stop()
        
        # Volver a la pantalla de verificación
        from ui.verification_screen import VerificationScreen
        self.app.change_screen(VerificationScreen, self.tipo_registro)
    
    def handle_event(self, event):
        """Maneja eventos de entrada."""
        pos = pygame.mouse.get_pos()
        
        # Actualizar estado de hover de botones
        self.capture_button_hover = self.capture_button_rect.collidepoint(pos)
        self.back_button_hover = self.back_button_rect.collidepoint(pos)
        
        # Manejar clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.capture_button_rect.collidepoint(pos) and self.camera_ready:
                self._capture_and_verify()
            elif self.back_button_rect.collidepoint(pos):
                self._on_back()
        
        # Manejar teclado
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.camera_ready:
                self._capture_and_verify()
            elif event.key == pygame.K_ESCAPE:
                self._on_back()
    
    def update(self):
        """Actualiza el estado de la pantalla."""
        # Obtener frame de la cámara
        if self.camera_ready and self.camera:
            self.frame = self.camera.get_frame()
        
        # Verificar tiempo de inactividad
        if time.time() - self.start_time > self.timeout:
            self._on_back()  # Volver por inactividad
    
    def draw(self):
        """Dibuja la pantalla."""
        # Limpiar pantalla
        self.screen.fill(self.bg_color)
        
        # Dibujar título
        title_text = f"Verificación Facial - {self.tipo_registro.capitalize()}"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Dibujar vista previa de la cámara
        pygame.draw.rect(self.screen, (200, 200, 200), self.preview_rect)
        if self.frame:
            # Redimensionar frame si es necesario
            if self.frame.get_width() != self.preview_rect.width or self.frame.get_height() != self.preview_rect.height:
                self.frame = pygame.transform.scale(self.frame, (self.preview_rect.width, self.preview_rect.height))
            self.screen.blit(self.frame, self.preview_rect)
        else:
            # Si no hay frame, dibujar un mensaje
            no_preview_text = "Sin vista previa"
            no_preview_surface = self.text_font.render(no_preview_text, True, self.text_color)
            no_preview_rect = no_preview_surface.get_rect(center=self.preview_rect.center)
            self.screen.blit(no_preview_surface, no_preview_rect)
        
        # Dibujar botón de captura
        capture_color = self.button_hover_color if self.capture_button_hover else self.button_color
        pygame.draw.rect(self.screen, capture_color, self.capture_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), self.capture_button_rect, 2, border_radius=5)
        
        capture_text = "Capturar" if not self.capturing else "Procesando..."
        capture_surface = self.text_font.render(capture_text, True, self.text_color)
        capture_text_rect = capture_surface.get_rect(center=self.capture_button_rect.center)
        self.screen.blit(capture_surface, capture_text_rect)
        
        # Dibujar botón de volver
        back_color = self.button_hover_color if self.back_button_hover else self.button_color
        pygame.draw.rect(self.screen, back_color, self.back_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), self.back_button_rect, 2, border_radius=5)
        
        back_surface = self.text_font.render("Volver", True, self.text_color)
        back_text_rect = back_surface.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_surface, back_text_rect)
        
        # Dibujar estado
        status_surface = self.text_font.render(self.status, True, self.text_color)
        status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(status_surface, status_rect)