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
            self.original_width = SCREEN_WIDTH   # 320
            self.original_height = SCREEN_HEIGHT  # 480
            
            # Importante: Para rotación horaria de 90°, intercambiamos las dimensiones
            self.screen = pygame.display.set_mode(
                (320, 480),  # Invertimos ancho/alto para la rotación
                pygame.FULLSCREEN  # Usar modo pantalla completa
            )

            # Superficie para dibujar con las dimensiones originales (sin rotar)
            # self.drawing_surface = pygame.Surface((self.original_width, self.original_height))

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
            self.screen_rotated = True
            
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

                # Limpiar la superficie de dibujo
                # self.drawing_surface.fill((240, 240, 240))  # Color de fondo

                # Actualizar y dibujar la pantalla actual
                if self.current_screen:
                    self.current_screen.update()
                    self.current_screen.draw()

                if self.screen_rotated:
                    # Rotar la pantalla completa después de dibujar
                    rotated_screen = pygame.transform.rotate(self.screen, 270)
                    # self.screen.fill((0, 0, 0))  # Limpiar pantalla con negro
                    self.screen.blit(rotated_screen, (70, -75))
            
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