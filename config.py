"""Configuración global de la aplicación."""

# Configuración de la API
API_URL = "http://servidor-central:8000"  # Cambiar a la URL real
API_KEY = "mi_api_key_segura_001"  # Cambiar a la API key real
TERMINAL_ID = "TERMINAL_001"

# Configuración de la pantalla
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240

# Configuración de la cámara
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

# Configuración del lector de huellas
FINGERPRINT_PORT = "/dev/ttyS0"
FINGERPRINT_BAUDRATE = 57600

# Tiempos de espera (en segundos)
TIMEOUT_VERIFICATION = 30
TIMEOUT_FACIAL = 20
TIMEOUT_RESULT = 5

# Rutas de archivos
LOCAL_STORAGE_PATH = "/home/pi/app/data/"