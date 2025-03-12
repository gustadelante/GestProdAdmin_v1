import os
import sqlite3
import sys

class DatabaseManager:
    """Clase para gestionar la conexión y operaciones con la base de datos."""
    
    def __init__(self):
        """Inicializa el gestor de base de datos."""
        # Determine if we're running as a script or frozen executable
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (pyinstaller)
            application_path = os.path.dirname(sys.executable)
        else:
            # If the application is run as a script
            application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Ensure data directory exists
        data_dir = os.path.join(application_path, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Set database path
        self.db_path = os.path.join(data_dir, 'produccion.db')
        
        # Create database if it doesn't exist
        self._create_database_if_not_exists()
    
    def _create_database_if_not_exists(self):
        """Crea la base de datos y las tablas necesarias si no existen."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bobinas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    turno TEXT,
                    ancho REAL,
                    diametro REAL,
                    gramaje REAL,
                    peso REAL,
                    bobina_num TEXT,
                    sec TEXT,
                    of TEXT,
                    fecha TEXT,
                    codcal TEXT,
                    desccal TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating database: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_connection(self):
        """Returns a connection to the database."""
        return sqlite3.connect(self.db_path)
    
    def get_bobinas(self):
        """Obtiene todas las bobinas de la base de datos."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bobinas ORDER BY id DESC")
            columns = [description[0] for description in cursor.description]
            result = []
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))
            return result
        except sqlite3.Error as e:
            print(f"Error getting bobinas: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def add_bobina(self, data):
        """Añade una nueva bobina a la base de datos."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Prepare columns and values
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            values = tuple(data.values())
            
            # Insert data
            cursor.execute(
                f"INSERT INTO bobinas ({columns}) VALUES ({placeholders})",
                values
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding bobina: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def delete_bobinas(self, ids):
        """Elimina bobinas por sus IDs."""
        if not ids:
            return False
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Prepare placeholders for the IN clause
            placeholders = ", ".join(["?" for _ in ids])
            
            # Delete records
            cursor.execute(
                f"DELETE FROM bobinas WHERE id IN ({placeholders})",
                tuple(ids)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting bobinas: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def filter_bobinas(self, filters):
        """Filtra bobinas según los criterios especificados."""
        if not filters:
            return self.get_bobinas()
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build WHERE clause
            conditions = []
            values = []
            
            for column, value in filters.items():
                conditions.append(f"{column} LIKE ?")
                values.append(f"%{value}%")
            
            where_clause = " AND ".join(conditions)
            
            # Execute query
            cursor.execute(
                f"SELECT * FROM bobinas WHERE {where_clause} ORDER BY id DESC",
                tuple(values)
            )
            
            columns = [description[0] for description in cursor.description]
            result = []
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))
            return result
        except sqlite3.Error as e:
            print(f"Error filtering bobinas: {e}")
            return []
        finally:
            if conn:
                conn.close()