import sqlite3
import os

class DatabaseManager:
    """
    Clase para gestionar la conexión y operaciones con la base de datos.
    """
    def __init__(self, db_path=None):
        # Set default database path if not provided
        self.db_path = db_path if db_path else os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'produccion.db')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database if it doesn't exist
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create bobina table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bobina (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turno TEXT NOT NULL,
            ancho REAL NOT NULL,
            diametro REAL NOT NULL,
            gramaje REAL NOT NULL,
            peso REAL NOT NULL,
            bobina_num TEXT NOT NULL,
            sec TEXT,
            of TEXT NOT NULL,
            fecha TEXT NOT NULL,
            codcal TEXT,
            desccal TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_bobina(self, bobina_data):
        """
        Añade un nuevo registro de bobina a la base de datos.
        
        Args:
            bobina_data (dict): Diccionario con los datos de la bobina
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Conectar a la base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Preparar la consulta SQL
            columns = ', '.join(bobina_data.keys())
            placeholders = ', '.join(['?' for _ in bobina_data])
            values = list(bobina_data.values())
            
            # Ejecutar la consulta
            cursor.execute(
                f"INSERT INTO bobina ({columns}) VALUES ({placeholders})",
                values
            )
            
            # Confirmar la transacción
            conn.commit()
            
            # Cerrar la conexión
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error al añadir bobina: {e}")
            return False
            
    def get_all_bobinas(self):
        """
        Obtiene todos los registros de bobinas de la base de datos.
        
        Returns:
            list: Lista de diccionarios con los datos de las bobinas
        """
        try:
            # Conectar a la base de datos
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Para obtener los resultados como diccionarios
            cursor = conn.cursor()
            
            # Ejecutar la consulta
            cursor.execute("SELECT * FROM bobina ORDER BY id DESC")
            
            # Obtener los resultados
            rows = cursor.fetchall()
            
            # Convertir los resultados a una lista de diccionarios
            result = [dict(row) for row in rows]
            
            # Cerrar la conexión
            conn.close()
            
            return result
        except Exception as e:
            print(f"Error al obtener bobinas: {e}")
            return []
            
    def filter_bobinas(self, filters):
        """
        Filtra los registros de bobinas según los criterios especificados.
        
        Args:
            filters (dict): Diccionario con los criterios de filtrado
            
        Returns:
            list: Lista de diccionarios con los datos de las bobinas filtradas
        """
        try:
            # Conectar a la base de datos
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Construir la consulta SQL con los filtros
            query = "SELECT * FROM bobina WHERE "
            conditions = []
            values = []
            
            for column, value in filters.items():
                # Para campos numéricos, buscar coincidencia exacta
                if column in ["ancho", "diametro", "gramaje", "peso"]:
                    try:
                        num_value = float(value)
                        conditions.append(f"{column} = ?")
                        values.append(num_value)
                    except ValueError:
                        # Si no es un número válido, ignorar este filtro
                        pass
                # Para el ID, buscar coincidencia exacta
                elif column == "id":
                    try:
                        id_value = int(value)
                        conditions.append("id = ?")
                        values.append(id_value)
                    except ValueError:
                        # Si no es un número válido, ignorar este filtro
                        pass
                # Para el resto de campos, buscar coincidencia parcial
                else:
                    conditions.append(f"LOWER({column}) LIKE ?")
                    values.append(f"%{value}%")
            
            # Si no hay condiciones, devolver todos los registros
            if not conditions:
                return self.get_all_bobinas()
            
            # Completar la consulta
            query += " AND ".join(conditions)
            query += " ORDER BY id DESC"
            
            # Ejecutar la consulta
            cursor.execute(query, values)
            
            # Obtener los resultados
            rows = cursor.fetchall()
            
            # Convertir los resultados a una lista de diccionarios
            result = [dict(row) for row in rows]
            
            # Cerrar la conexión
            conn.close()
            
            return result
        except Exception as e:
            print(f"Error al filtrar bobinas: {e}")
    
    def delete_bobinas(self, ids):
        """
        Elimina registros de bobinas por sus IDs.
        
        Args:
            ids (list): Lista de IDs de las bobinas a eliminar
            
        Returns:
            bool: True si se eliminaron correctamente, False en caso contrario
        """
        try:
            # Conectar a la base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crear placeholders para la consulta SQL
            placeholders = ', '.join(['?' for _ in ids])
            
            # Ejecutar la consulta
            cursor.execute(f"DELETE FROM bobina WHERE id IN ({placeholders})", ids)
            
            # Confirmar la transacción
            conn.commit()
            
            # Cerrar la conexión
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error al eliminar bobinas: {e}")
            return False

    def get_bobinas_by_ids(self, ids):
            """
            Obtiene los registros de bobinas por sus IDs.
            
            Args:
                ids (list): Lista de IDs de las bobinas a obtener
                
            Returns:
                list: Lista de diccionarios con los datos de las bobinas
            """
            try:
                # Conectar a la base de datos
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Crear placeholders para la consulta SQL
                placeholders = ', '.join(['?' for _ in ids])
                
                # Ejecutar la consulta
                cursor.execute(f"SELECT * FROM bobina WHERE id IN ({placeholders})", ids)
                
                # Obtener los resultados
                rows = cursor.fetchall()
                
                # Convertir los resultados a una lista de diccionarios
                result = [dict(row) for row in rows]
                
                # Cerrar la conexión
                conn.close()
                
                return result
            except Exception as e:
                print(f"Error al obtener bobinas por IDs: {e}")
                return []

    def move_to_historic(self, ids):
            """
            Mueve los registros seleccionados a la tabla histórica y los elimina de la tabla principal.
            
            Args:
                ids (list): Lista de IDs de las bobinas a mover
                
            Returns:
                bool: True si se movieron correctamente, False en caso contrario
            """
            try:
                # Conectar a la base de datos
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Crear placeholders para la consulta SQL
                placeholders = ', '.join(['?' for _ in ids])
                
                # Obtener los registros a mover
                cursor.execute(f"SELECT * FROM bobina WHERE id IN ({placeholders})", ids)
                rows = cursor.fetchall()
                
                # Insertar los registros en la tabla histórica
                for row in rows:
                    row_dict = dict(row)
                    # Eliminar el ID para que se genere uno nuevo en la tabla histórica
                    bobina_id = row_dict.pop('id')
                    
                    # Crear placeholders y valores para la inserción
                    columns = ', '.join(row_dict.keys())
                    value_placeholders = ', '.join(['?' for _ in row_dict])
                    values = list(row_dict.values())
                    
                    # Insertar en la tabla histórica
                    cursor.execute(f"INSERT INTO bobina_h ({columns}) VALUES ({value_placeholders})", values)
                
                # Eliminar los registros de la tabla principal
                cursor.execute(f"DELETE FROM bobina WHERE id IN ({placeholders})", ids)
                
                # Confirmar la transacción
                conn.commit()
                
                # Cerrar la conexión
                conn.close()
                
                return True
            except Exception as e:
                print(f"Error al mover registros a histórico: {e}")
                return False