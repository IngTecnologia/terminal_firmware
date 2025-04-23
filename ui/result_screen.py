"""Pantalla para mostrar resultados de verificación."""

import pygame
import time
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TIMEOUT_RESULT

class ResultScreen:
    """Pantalla para mostrar resultados."""
    
    def __init__(self, screen, app, success, result, cedula, tipo_registro):
        """Inicializa la pantalla de resultados."""
        self.screen = screen
        self.app = app
        self.success = success
        self.result = result
        self.cedula = cedula
        self.tipo_registro = tipo_registro
        
        # Colores
        self.bg_color = (240, 240, 240)
        self.text_color = (10, 10, 10)
        self.success_color = (40, 180, 40)
        self.error_color = (180, 40, 40)
        self.button_color = (120, 180, 220)
        self.button_hover_color = (140, 200, 240)
        
        # Fuentes
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.message_font = pygame.font.SysFont("Arial", 22, bold=True)
        
        # Botón de volver
        self.home_button_rect = pygame.Rect(
            (SCREEN_WIDTH - 150) // 2,
            SCREEN_HEIGHT - 60,
            150, 40
        )
        self.home_button_hover = False
        
        # Tiempo para volver automáticamente
        self.start_time = time.time()
        self.timeout = TIMEOUT_RESULT
    
    def handle_event(self, event):
        """Maneja eventos de entrada."""
        pos = pygame.mouse.get_pos()
        
        # Actualizar estado de hover del botón
        self.home_button_hover = self.home_button_rect.collidepoint(pos)
        
        # Manejar clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.home_button_rect.collidepoint(pos):
                self._go_home()
        
        # Manejar teclado
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._go_home()
    
    def _go_home(self):
        """Vuelve a la pantalla principal."""
        from ui.main_screen import MainScreen
        self.app.change_screen(MainScreen)
    
    def update(self):
        """Actualiza el estado de la pantalla."""
        # Verificar tiempo para volver automáticamente
        if time.time() - self.start_time > self.timeout:
            self._go_home()
    
    def draw(self):
        """Dibuja la pantalla."""
        # Limpiar pantalla
        self.screen.fill(self.bg_color)
        
        # Dibujar título
        title_text = f"Resultado - {self.tipo_registro.capitalize()}"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Dibujar resultado
        if self.success and self.result.get("verified", False):
            result_color = self.success_color
            result_text = "VERIFICACIÓN EXITOSA"
            result_details = f"Registro de {self.tipo_registro} completado"
        else:
            result_color = self.error_color
            result_text = "VERIFICACIÓN FALLIDA"
            
            # Determinar mensaje de error
            error_msg = "No se pudo verificar su identidad"
            if self.result and "error" in self.result:
                error_msg = self.result["error"]
            
            result_details = error_msg
        
        # Dibujar mensaje principal
        result_surface = self.message_font.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(result_surface, result_rect)
        
        # Dibujar detalles
        details_surface = self.text_font.render(result_details, True, self.text_color)
        details_rect = details_surface.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(details_surface, details_rect)
        
        # Dibujar información adicional
        info_text = f"Cédula: {self.cedula}"
        info_surface = self.text_font.render(info_text, True, self.text_color)
        info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, 190))
        self.screen.blit(info_surface, info_rect)
        
        time_info = f"Volviendo a inicio en {int(self.timeout - (time.time() - self.start_time))} segundos"
        time_surface = self.text_font.render(time_info, True, self.text_color)
        time_rect = time_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(time_surface, time_rect)
        
        # Dibujar botón de volver
        home_color = self.button_hover_color if self.home_button_hover else self.button_color
        pygame.draw.rect(self.screen, home_color, self.home_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), self.home_button_rect, 2, border_radius=5)
        
        home_surface = self.text_font.render("Volver a Inicio", True, self.text_color)
        home_text_rect = home_surface.get_rect(center=self.home_button_rect.center)
        self.screen.blit(home_surface, home_text_rect)