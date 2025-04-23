"""Utilidades para interactuar directamente con el framebuffer."""

import os
import fcntl
import struct
import mmap
import numpy as np

class Framebuffer:
    """Clase para interactuar directamente con el framebuffer."""
    
    def __init__(self, device='/dev/fb0'):
        """Inicializa el framebuffer.
        
        Args:
            device: Ruta al dispositivo de framebuffer
        """
        self.device = device
        self.fb_file = None
        self.fb_mmap = None
        self.fb_fix_info = None
        self.fb_var_info = None
        
        # Intentar abrir el framebuffer
        try:
            self.fb_file = open(device, 'r+b')
            self._get_fix_info()
            self._get_var_info()
            self._map_framebuffer()
        except Exception as e:
            print(f"Error al inicializar framebuffer: {e}")
            self.close()
    
    def _get_fix_info(self):
        """Obtiene información fija del framebuffer."""
        if not self.fb_file:
            return
            
        # Estructura para obtener información fija
        class FixScreenInfo(struct.Struct):
            def __init__(self):
                super().__init__('IIHHHHHHHHHHH')
        
        fix_info = FixScreenInfo()
        FBIOGET_FSCREENINFO = 0x4602
        
        try:
            fcntl.ioctl(self.fb_file.fileno(), FBIOGET_FSCREENINFO, fix_info)
            self.fb_fix_info = fix_info
        except Exception as e:
            print(f"Error al obtener información fija del framebuffer: {e}")
    
    def _get_var_info(self):
        """Obtiene información variable del framebuffer."""
        if not self.fb_file:
            return
            
        # Estructura para obtener información variable
        # Esta es una simplificación - la estructura real es más compleja
        class VarScreenInfo(struct.Struct):
            def __init__(self):
                super().__init__('IIIIIIIIIIIIIHHHHHHIIIIIIIII')
        
        var_info = VarScreenInfo()
        FBIOGET_VSCREENINFO = 0x4600
        
        try:
            fcntl.ioctl(self.fb_file.fileno(), FBIOGET_VSCREENINFO, var_info)
            self.fb_var_info = var_info
        except Exception as e:
            print(f"Error al obtener información variable del framebuffer: {e}")
    
    def _map_framebuffer(self):
        """Mapea el framebuffer a memoria."""
        if not self.fb_file or not self.fb_fix_info:
            return
            
        try:
            self.fb_mmap = mmap.mmap(
                self.fb_file.fileno(),
                self.fb_fix_info[2],  # smem_len
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=0
            )
        except Exception as e:
            print(f"Error al mapear framebuffer: {e}")
    
    def write_rgb565(self, x, y, width, height, rgb565_data):
        """Escribe datos RGB565 al framebuffer.
        
        Args:
            x: Coordenada X inicial
            y: Coordenada Y inicial
            width: Ancho de la región
            height: Alto de la región
            rgb565_data: Datos RGB565 como array numpy o bytes
        """
        if not self.fb_mmap:
            return False
            
        try:
            # Calcular offset
            line_length = self.fb_fix_info[8]  # line_length
            bytes_per_pixel = 2  # RGB565 = 16 bits = 2 bytes
            
            # Asegurarse de que los datos estén en el formato correcto
            if isinstance(rgb565_data, np.ndarray):
                rgb565_data = rgb565_data.tobytes()
            
            # Para cada línea
            for row in range(height):
                offset = (y + row) * line_length + x * bytes_per_pixel
                row_data = rgb565_data[row * width * bytes_per_pixel:(row + 1) * width * bytes_per_pixel]
                self.fb_mmap[offset:offset + len(row_data)] = row_data
            
            return True
        except Exception as e:
            print(f"Error al escribir al framebuffer: {e}")
            return False
    
    def close(self):
        """Cierra recursos del framebuffer."""
        if self.fb_mmap:
            self.fb_mmap.close()
            self.fb_mmap = None
        
        if self.fb_file:
            self.fb_file.close()
            self.fb_file = None