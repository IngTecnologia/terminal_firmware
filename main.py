#!/usr/bin/env python3
"""Script principal que inicia la aplicación de terminal biométrica."""

import os
import sys
import signal
import pygame
from ui.main_screen import MainScreen
from utils.error_handler import setup_error_handling

class TerminalApp:
    """Aplicación principal de la terminal biométrica."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        try:
            # Configurar variables de entorno para SDL
            os.environ["SDL_VIDEODRIVER"] = "fbcon"
            os.environ["SDL_FBDEV"] = "/dev/fb0"
            os.environ["SDL_NOMOUSE"] = "1"
            
            # Inicializar pygame
            pygame.init()
            
            # Configurar pantalla
            from config import SCREEN_WIDTH, SCREEN_HEIGHT
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Terminal Biométrica")
            
            # AHORA configuramos la visibilidad del mouse (después de set_mode)
            pygame.mouse.set_visible(False)
            
            # Variable para controlar el ciclo principal
            self.running = True
            
            # Configurar manejo de señales
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Configurar manejo de errores
            setup_error_handling()
            
            # Pantalla actual
            self.current_screen = None
            
        except Exception as e:
            print(f"Error al inicializar la aplicación: {e}")
            raise
    
    def signal_handler(self, sig, frame):
        """Maneja señales para salida limpia."""
        self.running = False
        print("\nDeteniendo aplicación...")
    
    def run(self):
        """Ejecuta el ciclo principal de la aplicación."""
        try:
            # Mostrar pantalla principal
            self.current_screen = MainScreen(self.screen, self)
            
            # Ciclo principal
            while self.running:
                # Manejar eventos
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif self.current_screen:
                        self.current_screen.handle_event(event)
                
                # Actualizar y dibujar la pantalla actual
                if self.current_screen:
                    self.current_screen.update()
                    self.current_screen.draw()
                
                # Actualizar pantalla
                pygame.display.flip()
                
                # Limitar FPS
                pygame.time.Clock().tick(30)
        
        except Exception as e:
            print(f"Error en el ciclo principal: {e}")
        finally:
            # Limpieza
            pygame.quit()
            print("Aplicación terminada.")
    
    def change_screen(self, screen_class, *args, **kwargs):
        """Cambia a una nueva pantalla."""
        try:
            self.current_screen = screen_class(self.screen, self, *args, **kwargs)
        except Exception as e:
            print(f"Error al cambiar de pantalla: {e}")

if __name__ == "__main__":
    app = TerminalApp()
    app.run()