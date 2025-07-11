"""Script principal que inicia la aplicación de terminal biométrica."""

import os
import sys
import signal
import pygame
from ui.main_screen import MainScreen
from utils.error_handler import setup_error_handling

class TerminalApp:
    """Aplicación principal de la terminal biométrica."""
    
    def signal_handler(self, sig, frame):
        """Maneja señales para salida limpia."""
        self.running = False
        print("\nDeteniendo aplicación...")
    
    def __init__(self):
        """Inicializa la aplicación."""
        try:
            # Intentar varios controladores de video en orden
            video_drivers = ["fbcon", "directfb", "x11", "dummy"]
            driver_success = False
            
            for driver in video_drivers:
                print(f"Intentando inicializar con controlador: {driver}")
                os.environ["SDL_VIDEODRIVER"] = driver
                
                try:
                    pygame.display.init()
                    driver_success = True
                    print(f"Éxito con controlador: {driver}")
                    break
                except pygame.error:
                    print(f"Falló el controlador: {driver}")
                    continue
            
            if not driver_success:
                raise Exception("No se pudo inicializar ningún controlador de video")
            
            # Completar inicialización de pygame
            pygame.init()
            
            # Configurar pantalla
            from config import SCREEN_WIDTH, SCREEN_HEIGHT
            
            # Pantalla naturalmente vertical 400x800
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.FULLSCREEN
            )

            pygame.display.set_caption("Terminal Biométrica")
        
            # Configuramos la visibilidad del mouse
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