import os
import json
import bcrypt
from utils.constants import CREDENTIALS_FILE

class AuthManager:
    """
    Clase para gestionar la autenticación de usuarios.
    Maneja el almacenamiento y verificación de credenciales.
    """
    def __init__(self, credentials_file=CREDENTIALS_FILE):
        self.credentials_file = credentials_file
        self._ensure_credentials_file()
    
    def _ensure_credentials_file(self):
        """Crea un archivo de credenciales por defecto si no existe."""
        if not os.path.exists(self.credentials_file):
            # Credenciales de ejemplo (admin/admin, operador/operador)
            default_credentials = {
                "admin": self._hash_password("admin"),
                "operador": self._hash_password("operador")
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(default_credentials, f)
    
    def _hash_password(self, password):
        """Genera un hash bcrypt de la contraseña."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_credentials(self, username, password):
        """Verifica las credenciales del usuario."""
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            
            if username not in credentials:
                return False
            
            stored_hash = credentials[username].encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        except Exception as e:
            print(f"Error al verificar credenciales: {str(e)}")
            return False
    
    def add_user(self, username, password):
        """Añade un nuevo usuario al archivo de credenciales."""
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            
            credentials[username] = self._hash_password(password)
            
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f)
            
            return True
        except Exception as e:
            print(f"Error al añadir usuario: {str(e)}")
            return False
    
    def change_password(self, username, new_password):
        """Cambia la contraseña de un usuario existente."""
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            
            if username not in credentials:
                return False
            
            credentials[username] = self._hash_password(new_password)
            
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f)
            
            return True
        except Exception as e:
            print(f"Error al cambiar contraseña: {str(e)}")
            return False