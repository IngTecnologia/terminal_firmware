"""Pantalla de verificación para ingreso de cédula o huella."""

import pygame
import time
import threading
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TIMEOUT_VERIFICATION
from hardware.fingerprint import Fingerprint
from ui.camera_screen import CameraScreen

class VerificationScreen:
    """Pantalla para verificación de identidad."""
    
    def __init__(self, screen, app, tipo_registro):
        """Inicializa la pantalla de verificación."""
        self.screen = screen
        self.app = app
        self.tipo_registro = tipo_registro
        
        # Colores
        self.bg_color = (240, 240, 240)
        self.text_color = (10, 10, 10)
        self.input_bg_color = (255, 255, 255)
        self.button_color = (120, 180, 220)
        self.button_hover_color = (140, 200, 240)
        
        # Fuentes
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 18)
        self.input_font = pygame.font.SysFont("Arial", 20)
        
        # Estado de la entrada
        self.cedula_input = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_time = 500  # ms
        
        # Botones
        self.buttons = []
        self._create_buttons()
        
        # Áreas interactivas
        self.input_rect = pygame.Rect(
            (SCREEN_WIDTH - 200) // 2,
            120,
            200, 40
        )
        
        # Lector de huellas
        self.fingerprint = Fingerprint()
        self.fingerprint_thread = None
        self.fingerprint_status = "Conectando..."
        
        # Tiempo de inactividad
        self.start_time = time.time()
        self.timeout = TIMEOUT_VERIFICATION
        
        # Iniciar escaneo de huellas en un hilo separado
        self.fingerprint_thread = threading.Thread(
            target=self._start_fingerprint_scan,
            daemon=True
        )
        self.fingerprint_thread.start()
    
    def _create_buttons(self):
        """Crea los botones numéricos y de acción."""
        # Botones numéricos
        button_size = 50
        margin = 10
        start_x = (SCREEN_WIDTH - (3 * button_size + 2 * margin)) // 2
        start_y = 180
        
        # Crear botones del 1 al 9
        for i in range(9):
            row = i // 3
            col = i % 3
            x = start_x + col * (button_size + margin)
            y = start_y + row * (button_size + margin)
            
            self.buttons.append({
                "rect": pygame.Rect(x, y, button_size, button_size),
                "text": str(i + 1),
                "action": lambda digit=str(i + 1): self._on_digit_press(digit),
                "hovered": False
            })
        
        # Botón 0
        self.buttons.append({
            "rect": pygame.Rect(start_x + button_size + margin, start_y + 3 * (button_size + margin), button_size, button_size),
            "text": "0",
            "action": lambda: self._on_digit_press("0"),
            "hovered": False
        })
        
        # Botón borrar
        self.buttons.append({
            "rect": pygame.Rect(start_x, start_y + 3 * (button_size + margin), button_size, button_size),
            "text": "←",
            "action": self._on_backspace,
            "hovered": False
        })
        
        # Botón aceptar
        self.buttons.append({
            "rect": pygame.Rect(start_x + 2 * (button_size + margin), start_y + 3 * (button_size + margin), button_size, button_size),
            "text": "✓",
            "action": self._on_submit,
            "hovered": False
        })
        
        # Botón volver
        self.buttons.append({
            "rect": pygame.Rect(10, 10, 80, 30),
            "text": "Volver",
            "action": self._on_back,
            "hovered": False
        })
    
    def _start_fingerprint_scan(self):
        """Inicia el escaneo de huellas."""
        try:
            if self.fingerprint.connect():
                self.fingerprint_status = "Coloque su dedo en el lector"
                self.fingerprint.start_scan(self._on_fingerprint_scan)
            else:
                self.fingerprint_status = "Error al conectar el lector"
        except Exception as e:
            self.fingerprint_status = f"Error: {str(e)}"
    
    def _on_fingerprint_scan(self, success, cedula):
        """Callback cuando se detecta una huella."""
        if success:
            self.cedula_input = cedula
            self._on_submit()
        else:
            self.fingerprint_status = "Huella no reconocida"
    
    def _on_digit_press(self, digit):
        """Maneja la pulsación de un dígito."""
        if len(self.cedula_input) < 15:  # Limitar longitud
            self.cedula_input += digit
        self.start_time = time.time()  # Reiniciar tiempo de inactividad
    
    def _on_backspace(self):
        """Maneja la pulsación del botón de borrar."""
        if self.cedula_input:
            self.cedula_input = self.cedula_input[:-1]
        self.start_time = time.time()  # Reiniciar tiempo de inactividad
    
    def _on_submit(self):
        """Maneja la pulsación del botón de aceptar."""
        if len(self.cedula_input) >= 5:  # Validación básica
            # Detener escaneo de huellas
            if self.fingerprint:
                self.fingerprint.stop_scan()
            
            # Cambiar a la pantalla de cámara
            from ui.camera_screen import CameraScreen
            self.app.change_screen(CameraScreen, self.cedula_input, self.tipo_registro)
    
    def _on_back(self):
        """Maneja la pulsación del botón de volver."""
        # Detener escaneo de huellas
        if self.fingerprint:
            self.fingerprint.stop_scan()
        
        # Volver a la pantalla principal
        from ui.main_screen import MainScreen
        self.app.change_screen(MainScreen)
    
    def handle_event(self, event):
        """Maneja eventos de entrada."""
        # Manejar clicks en botones
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button["rect"].collidepoint(pos):
                    button["action"]()
        
        # Manejar entrada de teclado
        elif event.type == pygame.KEYDOWN:
            if event.unicode.isdigit():
                self._on_digit_press(event.unicode)
            elif event.key == pygame.K_BACKSPACE:
                self._on_backspace()
            elif event.key == pygame.K_RETURN:
                self._on_submit()
            elif event.key == pygame.K_ESCAPE:
                self._on_back()
        
        # Actualizar estado de hover de botones
        pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button["hovered"] = button["rect"].collidepoint(pos)
    
    def update(self):
        """Actualiza el estado de la pantalla."""
        # Actualizar parpadeo del cursor
        now = pygame.time.get_ticks()
        if now - self.cursor_timer > self.cursor_blink_time:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = now
        
        # Verificar tiempo de inactividad
        if time.time() - self.start_time > self.timeout:
            self._on_back()  # Volver a la pantalla principal por inactividad
    
    def draw(self):
        """Dibuja la pantalla."""
        # Limpiar pantalla
        self.screen.fill(self.bg_color)
        
        # Dibujar título
        title_text = f"Registro de {self.tipo_registro.capitalize()}"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Dibujar instrucciones
        instruction_text = "Digite su cédula o use huella"
        instruction_surface = self.text_font.render(instruction_text, True, self.text_color)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(instruction_surface, instruction_rect)
        
        # Dibujar caja de entrada
        pygame.draw.rect(self.screen, self.input_bg_color, self.input_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.input_rect, 2)
        
        # Dibujar texto de entrada
        input_text = self.cedula_input
        if self.cursor_visible:
            input_text += "|"
        if input_text:
            input_surface = self.input_font.render(input_text, True, self.text_color)
            input_text_rect = input_surface.get_rect(midleft=(self.input_rect.left + 10, self.input_rect.centery))
            self.screen.blit(input_surface, input_text_rect)
        
        # Dibujar botones
        for button in self.buttons:
            color = self.button_hover_color if button["hovered"] else self.button_color
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 100), button["rect"], 2, border_radius=5)
            
            text_surface = self.text_font.render(button["text"], True, self.text_color)
            text_rect = text_surface.get_rect(center=button["rect"].center)
            self.screen.blit(text_surface, text_rect)
        
        # Dibujar estado del lector de huellas
        fingerprint_surface = self.text_font.render(self.fingerprint_status, True, self.text_color)
        fingerprint_rect = fingerprint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(fingerprint_surface, fingerprint_rect)