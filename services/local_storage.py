"""Almacenamiento local de registros y configuración."""

import json
import os
import time
from datetime import datetime
from config import LOCAL_STORAGE_PATH

# Asegurar que existe el directorio
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

class LocalStorage:
    """Clase para manejar almacenamiento local."""
    
    def __init__(self):
        """Inicializa el almacenamiento local."""
        self.records_file = os.path.join(LOCAL_STORAGE_PATH, "records.json")
        self.users_file = os.path.join(LOCAL_STORAGE_PATH, "users.json")
        self.settings_file = os.path.join(LOCAL_STORAGE_PATH, "settings.json")
    
    def _load_json(self, file_path, default=None):
        """Carga un archivo JSON."""
        if default is None:
            default = {}
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return default
        except Exception as e:
            print(f"Error al cargar archivo {file_path}: {str(e)}")
            return default
    
    def _save_json(self, file_path, data):
        """Guarda datos en un archivo JSON."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar archivo {file_path}: {str(e)}")
            return False
    
    def save_record(self, record):
        """Guarda un registro local."""
        records = self._load_json(self.records_file, {"records": []})
        
        # Añadir timestamp si no existe
        if "timestamp" not in record:
            record["timestamp"] = datetime.now().isoformat()
        
        # Añadir sincronizado si no existe
        if "synchronized" not in record:
            record["synchronized"] = False
        
        records["records"].append(record)
        
        return self._save_json(self.records_file, records)
    
    def get_unsynchronized_records(self):
        """Obtiene los registros no sincronizados."""
        records = self._load_json(self.records_file, {"records": []})
        return [r for r in records["records"] if not r.get("synchronized", False)]
    
    def mark_record_synchronized(self, record_index):
        """Marca un registro como sincronizado."""
        records = self._load_json(self.records_file, {"records": []})
        
        if 0 <= record_index < len(records["records"]):
            records["records"][record_index]["synchronized"] = True
            return self._save_json(self.records_file, records)
        
        return False
    
    def save_user(self, user):
        """Guarda información de un usuario."""
        users = self._load_json(self.users_file, {"users": []})
        
        # Verificar si el usuario ya existe
        for i, existing_user in enumerate(users["users"]):
            if existing_user.get("cedula") == user.get("cedula"):
                users["users"][i] = user
                return self._save_json(self.users_file, users)
        
        # Si no existe, añadirlo
        users["users"].append(user)
        return self._save_json(self.users_file, users)
    
    def get_user(self, cedula):
        """Obtiene información de un usuario por cédula."""
        users = self._load_json(self.users_file, {"users": []})
        
        for user in users["users"]:
            if user.get("cedula") == cedula:
                return user
        
        return None
    
    def get_all_users(self):
        """Obtiene todos los usuarios."""
        users = self._load_json(self.users_file, {"users": []})
        return users["users"]
    
    def save_setting(self, key, value):
        """Guarda una configuración."""
        settings = self._load_json(self.settings_file, {})
        settings[key] = value
        return self._save_json(self.settings_file, settings)
    
    def get_setting(self, key, default=None):
        """Obtiene una configuración."""
        settings = self._load_json(self.settings_file, {})
        return settings.get(key, default)
    
    def get_all_settings(self):
        """Obtiene todas las configuraciones."""
        return self._load_json(self.settings_file, {})