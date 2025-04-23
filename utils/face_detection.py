"""Utilidades para detección facial básica."""

import io
from PIL import Image
import numpy as np

# Nota: En un sistema real, aquí se implementaría una integración con
# una biblioteca real de detección facial como OpenCV o dlib.
# Para simplificar, implementamos una detección simulada.

def detect_faces(image_data):
    """Detecta rostros en una imagen.
    
    Args:
        image_data: Datos de la imagen en bytes o un objeto BytesIO
        
    Returns:
        Una lista de regiones (x, y, width, height) de rostros detectados
    """
    # Simulación de detección facial
    # En un sistema real, aquí implementarías algo como:
    # cv2.CascadeClassifier.detectMultiScale o dlib.get_frontal_face_detector
    
    try:
        # Convertir datos a imagen PIL si no lo es ya
        if isinstance(image_data, bytes):
            image_data = io.BytesIO(image_data)
        
        # Abrir imagen
        image = Image.open(image_data)
        
        # Simulamos detección aleatoria para pruebas
        # Devolvemos una cara ficticia en el centro de la imagen
        width, height = image.size
        
        # Simular una cara en el centro de la imagen
        face_width = width // 3
        face_height = height // 3
        face_x = (width - face_width) // 2
        face_y = (height - face_height) // 2
        
        # 90% de probabilidad de detectar cara
        import random
        if random.random() < 0.9:
            return [(face_x, face_y, face_width, face_height)]
        else:
            return []
        
    except Exception as e:
        print(f"Error en detección facial: {e}")
        return []

def crop_face(image_data, face_region=None):
    """Recorta una región facial de una imagen.
    
    Args:
        image_data: Datos de la imagen en bytes o un objeto BytesIO
        face_region: La región (x, y, width, height) a recortar. Si es None,
                    se detectará automáticamente.
                    
    Returns:
        BytesIO con la imagen recortada en formato JPEG
    """
    try:
        # Convertir datos a imagen PIL si no lo es ya
        if isinstance(image_data, bytes):
            image_data = io.BytesIO(image_data)
        
        # Abrir imagen
        image = Image.open(image_data)
        
        # Detectar rostro si no se proporcionó región
        if face_region is None:
            faces = detect_faces(image_data)
            if not faces:
                # Si no se detectó ningún rostro, devolver la imagen original
                image_data.seek(0)
                return image_data
            
            face_region = faces[0]  # Usar la primera cara detectada
        
        # Recortar la región
        x, y, width, height = face_region
        face_image = image.crop((x, y, x + width, y + height))
        
        # Convertir a bytes
        output = io.BytesIO()
        face_image.save(output, format="JPEG")
        output.seek(0)
        
        return output
        
    except Exception as e:
        print(f"Error al recortar rostro: {e}")
        # En caso de error, devolver la imagen original
        if isinstance(image_data, io.BytesIO):
            image_data.seek(0)
            return image_data
        else:
            output = io.BytesIO(image_data)
            output.seek(0)
            return output