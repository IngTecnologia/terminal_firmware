"""Pantalla principal con las tres opciones."""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class Button:
    """Clase para representar un botón en la interfaz."""
    
    def __init__(self, x, y, width, height, text, color, hover_color, text_color):
        """Inicializa un botón."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        
    def draw(self, screen, font):
        """Dibuja el botón en la pantalla."""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=10)
        
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_hovered(self, pos):
        """Verifica si el mouse está sobre el botón."""
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def is_clicked(self, pos, event):
        """Verifica si el botón ha sido clickeado."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class MainScreen:
    """Pantalla principal de la aplicación."""
    
    def __init__(self, screen, app):
        """Inicializa la pantalla principal."""
        self.screen = screen
        self.app = app
        
        # Colores
        self.bg_color = (240, 240, 240)
        self.button_color = (120, 180, 220)
        self.button_hover_color = (140, 200, 240)
        self.text_color = (10, 10, 10)
        
        # Fuentes - Escaladas para pantalla más grande
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 28)
        
        # Crear botones - Ajustados para pantalla vertical 400x800
        button_width = 300
        button_height = 80
        button_margin = 40
        
        # Calcular posiciones centradas verticalmente
        start_y = (SCREEN_HEIGHT - (3 * button_height + 2 * button_margin)) // 2
        
        self.entrada_button = Button(
            (SCREEN_WIDTH - button_width) // 2,
            start_y,
            button_width, button_height,
            "Entrada",
            self.button_color, self.button_hover_color, self.text_color
        )
        
        self.salida_button = Button(
            (SCREEN_WIDTH - button_width) // 2,
            start_y + button_height + button_margin,
            button_width, button_height,
            "Salida",
            self.button_color, self.button_hover_color, self.text_color
        )
        
        self.registro_button = Button(
            (SCREEN_WIDTH - button_width) // 2,
            start_y + 2 * (button_height + button_margin),
            button_width, button_height,
            "Modo de Registro",
            self.button_color, self.button_hover_color, self.text_color
        )
    
    def handle_event(self, event):
        """Maneja eventos de entrada."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Verificar si los botones están siendo hover
        self.entrada_button.is_hovered(mouse_pos)
        self.salida_button.is_hovered(mouse_pos)
        self.registro_button.is_hovered(mouse_pos)
        
        # Verificar clicks
        if self.entrada_button.is_clicked(mouse_pos, event):
            from ui.verification_screen import VerificationScreen
            self.app.change_screen(VerificationScreen, "entrada")
        
        elif self.salida_button.is_clicked(mouse_pos, event):
            from ui.verification_screen import VerificationScreen
            self.app.change_screen(VerificationScreen, "salida")
        
        elif self.registro_button.is_clicked(mouse_pos, event):
            from ui.registration_screen import RegistrationScreen
            self.app.change_screen(RegistrationScreen)
    
    def update(self):
        """Actualiza el estado de la pantalla."""
        pass
    
    def draw(self):
        """Dibuja la pantalla."""
        # Limpiar pantalla
        self.screen.fill(self.bg_color)
        
        # Dibujar título - Posición ajustada para pantalla vertical
        title_surface = self.title_font.render("Terminal Biométrica", True, self.text_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Dibujar botones
        self.entrada_button.draw(self.screen, self.button_font)
        self.salida_button.draw(self.screen, self.button_font)
        self.registro_button.draw(self.screen, self.button_font)