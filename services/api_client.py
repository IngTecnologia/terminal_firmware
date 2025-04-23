"""Cliente para comunicación con el servidor API."""

import requests
import json
from config import API_URL, API_KEY, TERMINAL_ID

class ApiClient:
    """Cliente para comunicarse con la API del servidor."""
    
    def __init__(self):
        """Inicializa el cliente API."""
        self.base_url = API_URL
        self.headers = {
            "x-api-key": API_KEY
        }
    
    def verify_face(self, cedula, tipo_registro, image_data):
        """Verifica una imagen facial con el servidor."""
        try:
            url = f"{self.base_url}/verify-terminal"
            
            files = {
                'image': ('image.jpg', image_data, 'image/jpeg')
            }
            
            data = {
                'cedula': cedula,
                'terminal_id': TERMINAL_ID,
                'tipo_registro': tipo_registro
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = "Error del servidor"
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        error_msg = error_data['detail']
                except:
                    pass
                return False, {"error": error_msg}
        
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Error de conexión: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Error inesperado: {str(e)}"}
    
    def check_pending_registrations(self):
        """Verifica si hay registros pendientes para esta terminal."""
        try:
            url = f"{self.base_url}/pending-registrations"
            
            params = {
                'terminal_id': TERMINAL_ID
            }
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = "Error del servidor"
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        error_msg = error_data['detail']
                except:
                    pass
                return False, {"error": error_msg}
        
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Error de conexión: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Error inesperado: {str(e)}"}
    
    def confirm_registration(self, registration_id, success, details=None):
        """Confirma el registro de una huella."""
        try:
            url = f"{self.base_url}/confirm-registration"
            
            data = {
                'registration_id': registration_id,
                'terminal_id': TERMINAL_ID,
                'success': success
            }
            
            if details:
                data['details'] = details
            
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = "Error del servidor"
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        error_msg = error_data['detail']
                except:
                    pass
                return False, {"error": error_msg}
        
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Error de conexión: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Error inesperado: {str(e)}"}