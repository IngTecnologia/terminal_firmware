"""Componentes comunes de UI para reutilización."""

import pygame

class Button:
    """Clase para representar un botón en la interfaz."""
    
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font=None):
        """Inicializa un botón."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.font = font or pygame.font.SysFont("Arial", 18)
        
    def draw(self, screen):
        """Dibuja el botón en la pantalla."""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        """Actualiza el estado del botón."""
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered
    
    def is_clicked(self, pos, event):
        """Verifica si el botón ha sido clickeado."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class TextBox:
    """Clase para representar una caja de texto."""
    
    def __init__(self, x, y, width, height, bg_color, border_color, text_color, font=None):
        """Inicializa una caja de texto."""
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = border_color
        self.text_color = text_color
        self.font = font or pygame.font.SysFont("Arial", 18)
        self.text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_time = 500  # ms
        self.active = False
        
    def draw(self, screen):
        """Dibuja la caja de texto en la pantalla."""
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Dibujar texto
        display_text = self.text
        if self.active and self.cursor_visible:
            display_text += "|"
        
        if display_text:
            text_surface = self.font.render(display_text, True, self.text_color)
            text_rect = text_surface.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
            screen.blit(text_surface, text_rect)
    
    def update(self, events, mouse_pos):
        """Actualiza el estado de la caja de texto."""
        # Manejar clicks para activar/desactivar
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.active = self.rect.collidepoint(mouse_pos)
            
            # Manejar entrada de texto
            if self.active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.active = False
                else:
                    # Limitar longitud y solo permitir ciertos caracteres
                    if len(self.text) < 30 and event.unicode.isprintable():
                        self.text += event.unicode
        
        # Actualizar parpadeo del cursor
        now = pygame.time.get_ticks()
        if now - self.cursor_timer > self.cursor_blink_time:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = now
        
        return self.active

class MessageBox:
    """Clase para mostrar mensajes temporales."""
    
    def __init__(self, width, height, message, bg_color, text_color, font=None, duration=3000):
        """Inicializa una caja de mensaje."""
        from config import SCREEN_WIDTH, SCREEN_HEIGHT
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - width) // 2,
            (SCREEN_HEIGHT - height) // 2,
            width, height
        )
        self.message = message
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font or pygame.font.SysFont("Arial", 18)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        
    def draw(self, screen):
        """Dibuja la caja de mensaje en la pantalla."""
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=10)
        
        # Dibujar mensaje
        text_surface = self.font.render(self.message, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_expired(self):
        """Verifica si el mensaje ha expirado."""
        return pygame.time.get_ticks() - self.start_time > self.duration