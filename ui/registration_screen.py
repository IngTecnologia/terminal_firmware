"""Pantalla para registro de huellas."""

import pygame
import time
import threading
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from hardware.fingerprint import Fingerprint
from services.api_client import ApiClient

class RegistrationScreen:
    """Pantalla para registro de huellas."""
    
    def __init__(self, screen, app):
        """Inicializa la pantalla de registro."""
        self.screen = screen
        self.app = app
        
        # Colores
        self.bg_color = (240, 240, 240)
        self.text_color = (10, 10, 10)
        self.button_color = (120, 180, 220)
        self.button_hover_color = (140, 200, 240)
        
        # Fuentes
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        
        # Estado
        self.status = "Verificando registros pendientes..."
        self.pending_registrations = None
        self.registration_error = None
        self.current_registration = None
        self.registration_state = "checking"  # checking, registering, success, error
        
        # Lector de huellas
        self.fingerprint = Fingerprint()
        
        # Cliente API
        self.api_client = ApiClient()
        
        # Botón de volver
        self.back_button_rect = pygame.Rect(
            10, 10, 80, 30
        )
        self.back_button_hover = False
        
        # Botón de registrar
        self.register_button_rect = pygame.Rect(
            (SCREEN_WIDTH - 150) // 2,
            200,
            150, 40
        )
        self.register_button_hover = False
        
        # Verificar registros pendientes en un hilo separado
        threading.Thread(target=self._check_pending_registrations, daemon=True).start()
    
    def _check_pending_registrations(self):
        """Verifica si hay registros pendientes."""
        try:
            success, result = self.api_client.check_pending_registrations()
            
            if success:
                self.pending_registrations = result.get("registrations", [])
                if self.pending_registrations:
                    self.current_registration = self.pending_registrations[0]
                    self.status = f"Registro pendiente para cédula: {self.current_registration.get('cedula', 'Unknown')}"
                    self.registration_state = "ready"
                else:
                    self.status = "No hay registros pendientes"
            else:
                self.registration_error = result.get("error", "Error desconocido")
                self.status = f"Error: {self.registration_error}"
                self.registration_state = "error"
                        
        except Exception as e:
            self.registration_error = str(e)
            self.status = f"Error al verificar registros: {str(e)}"
            self.registration_state = "error"
    
    def _start_registration(self):
        """Inicia el proceso de registro de huella."""
        if not self.current_registration:
            self.status = "No hay registro para procesar"
            return
        
        self.registration_state = "registering"
        self.status = "Conectando con lector de huellas..."
        
        # Iniciar el proceso en un hilo separado
        threading.Thread(target=self._registration_process, daemon=True).start()
    
    def _registration_process(self):
        """Proceso de registro de huella."""
        try:
            if not self.fingerprint.connect():
                self.status = "Error al conectar con el lector"
                self.registration_state = "error"
                return
            
            # Obtener ID para la huella del registro actual
            finger_id = self.current_registration.get("finger_id", 1)
            cedula = self.current_registration.get("cedula", "Unknown")
            registration_id = self.current_registration.get("id", "Unknown")
            
            self.status = f"Coloque el dedo en el lector (Cédula: {cedula})"
            time.sleep(2)  # Esperar a que el usuario coloque el dedo
            
            # Simular registro (en un sistema real, aquí se implementaría el protocolo real)
            # Para simplificar, simulamos un éxito después de unos segundos
            time.sleep(3)
            
            self.status = "Procesando huella..."
            time.sleep(1)
            
            # Registrar huella (aquí iría la implementación real)
            success = self.fingerprint.register_fingerprint(finger_id)
            
            if success:
                self.status = "Huella registrada con éxito"
                self.registration_state = "success"
                
                # Confirmar registro con el servidor
                confirm_success, confirm_result = self.api_client.confirm_registration(
                    registration_id,
                    True,
                    {"finger_id": finger_id}
                )
                
                if confirm_success:
                    self.status = "Registro confirmado con el servidor"
                else:
                    self.status = f"Huella registrada, pero error al confirmar: {confirm_result.get('error', 'Error desconocido')}"
            else:
                self.status = "Error al registrar huella"
                self.registration_state = "error"
                
                # Informar al servidor del fallo
                self.api_client.confirm_registration(
                    registration_id,
                    False,
                    {"error": "Error al registrar huella"}
                )
        
        except Exception as e:
            self.status = f"Error en registro: {str(e)}"
            self.registration_state = "error"
            
            # Informar al servidor del fallo si tenemos ID
            if self.current_registration and "id" in self.current_registration:
                self.api_client.confirm_registration(
                    self.current_registration["id"],
                    False,
                    {"error": str(e)}
                )
        finally:
            # Cerrar conexión del lector
            self.fingerprint.disconnect()
    
    def _on_back(self):
        """Maneja la pulsación del botón de volver."""
        # Detener procesos y volver a la pantalla principal
        if self.fingerprint:
            self.fingerprint.disconnect()
        
        from ui.main_screen import MainScreen
        self.app.change_screen(MainScreen)
    
    def handle_event(self, event):
        """Maneja eventos de entrada."""
        pos = pygame.mouse.get_pos()
        
        # Actualizar estado de hover de botones
        self.back_button_hover = self.back_button_rect.collidepoint(pos)
        self.register_button_hover = self.register_button_rect.collidepoint(pos)
        
        # Manejar clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button_rect.collidepoint(pos):
                self._on_back()
            elif self.register_button_rect.collidepoint(pos) and self.registration_state == "ready":
                self._start_registration()
        
        # Manejar teclado
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_back()
            elif event.key == pygame.K_RETURN and self.registration_state == "ready":
                self._start_registration()
    
    def update(self):
        """Actualiza el estado de la pantalla."""
        pass
    
    def draw(self):
        """Dibuja la pantalla."""
        # Limpiar pantalla
        self.screen.fill(self.bg_color)
        
        # Dibujar título
        title_surface = self.title_font.render("Modo de Registro", True, self.text_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Dibujar estado
        status_surface = self.text_font.render(self.status, True, self.text_color)
        status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(status_surface, status_rect)
        
        # Dibujar información adicional
        if self.current_registration:
            info_text = f"Cédula: {self.current_registration.get('cedula', 'Unknown')}"
            info_surface = self.text_font.render(info_text, True, self.text_color)
            info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, 130))
            self.screen.blit(info_surface, info_rect)
            
            if "nombre" in self.current_registration:
                name_text = f"Nombre: {self.current_registration['nombre']}"
                name_surface = self.text_font.render(name_text, True, self.text_color)
                name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, 160))
                self.screen.blit(name_surface, name_rect)
        
        # Dibujar botón de registrar (solo si hay registro pendiente y estado adecuado)
        if self.registration_state == "ready":
            register_color = self.button_hover_color if self.register_button_hover else self.button_color
            pygame.draw.rect(self.screen, register_color, self.register_button_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), self.register_button_rect, 2, border_radius=5)
            
            register_surface = self.text_font.render("Iniciar Registro", True, self.text_color)
            register_text_rect = register_surface.get_rect(center=self.register_button_rect.center)
            self.screen.blit(register_surface, register_text_rect)
        
        # Dibujar botón de volver
        back_color = self.button_hover_color if self.back_button_hover else self.button_color
        pygame.draw.rect(self.screen, back_color, self.back_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), self.back_button_rect, 2, border_radius=5)
        
        back_surface = self.text_font.render("Volver", True, self.text_color)
        back_text_rect = back_surface.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_surface, back_text_rect)
        
        # Mostrar instrucciones según el estado
        if self.registration_state == "registering":
            instruction_text = "Siga las instrucciones en pantalla..."
            instruction_surface = self.text_font.render(instruction_text, True, self.text_color)
            instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(instruction_surface, instruction_rect)
        elif self.registration_state == "success":
            success_text = "Registro completado con éxito"
            success_surface = self.text_font.render(success_text, True, (40, 180, 40))
            success_rect = success_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(success_surface, success_rect)
        elif self.registration_state == "error":
            error_text = "Se produjo un error durante el registro"
            error_surface = self.text_font.render(error_text, True, (180, 40, 40))
            error_rect = error_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(error_surface, error_rect)