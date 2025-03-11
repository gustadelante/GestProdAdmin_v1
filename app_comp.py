import flet as ft
import sqlite3
import bcrypt
import json
import os
import csv
from datetime import datetime
import threading
import time

class DatabaseManager:
    def __init__(self, db_file="produccion.db"):
        self.db_file = db_file
        self.initialize_database()
    
    def initialize_database(self):
        """Inicializa la base de datos si no existe."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Crear tabla bobina
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bobina (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turno TEXT NOT NULL,
            ancho REAL NOT NULL,
            diametro REAL NOT NULL,
            gramaje REAL NOT NULL,
            peso REAL NOT NULL,
            bobina_num TEXT NOT NULL UNIQUE,
            sec TEXT,
            of TEXT NOT NULL,
            fecha TEXT NOT NULL,
            codcal TEXT,
            desccal TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Crear tabla histórica
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bobina_h (
            id INTEGER PRIMARY KEY,
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
            created_at TEXT,
            fecha_insercion TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_all_bobinas(self):
        """Recupera todos los registros de la tabla bobina."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bobina")
        rows = cursor.fetchall()
        conn.close()
        
        # Convertir a lista de diccionarios
        result = []
        for row in rows:
            row_dict = {key: row[key] for key in row.keys()}
            result.append(row_dict)
        
        return result
    
    def move_to_history_and_export(self, selected_ids):
        """Mueve registros seleccionados a la tabla histórica y los exporta a CSV."""
        if not selected_ids:
            return False, "No hay registros seleccionados."
        
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 1. Obtener registros seleccionados
            ids_str = ','.join(['?' for _ in selected_ids])
            cursor.execute(f"SELECT * FROM bobina WHERE id IN ({ids_str})", selected_ids)
            selected_records = cursor.fetchall()
            
            if not selected_records:
                conn.close()
                return False, "No se encontraron los registros seleccionados."
            
            # 2. Exportar a CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"ManProductos_{timestamp}.csv"
            
            with open(csv_filename, 'w', newline='') as csvfile:
                fieldnames = [
                    'ID', 'Turno', 'Ancho', 'Diametro', 'Gramaje', 'Peso', 
                    'Bobina_Num', 'Sec', 'OF', 'Fecha', 'CodCal', 'DescCal', 'Created_At'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in selected_records:
                    writer.writerow({
                        'ID': record['id'],
                        'Turno': record['turno'],
                        'Ancho': record['ancho'],
                        'Diametro': record['diametro'],
                        'Gramaje': record['gramaje'],
                        'Peso': record['peso'],
                        'Bobina_Num': record['bobina_num'],
                        'Sec': record['sec'],
                        'OF': record['of'],
                        'Fecha': record['fecha'],
                        'CodCal': record['codcal'],
                        'DescCal': record['desccal'],
                        'Created_At': record['created_at']
                    })
            
            # 3. Mover registros a la tabla histórica
            for record in selected_records:
                cursor.execute('''
                INSERT INTO bobina_h (
                    id, turno, ancho, diametro, gramaje, peso, bobina_num, 
                    sec, of, fecha, codcal, desccal, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record['id'], record['turno'], record['ancho'], record['diametro'],
                    record['gramaje'], record['peso'], record['bobina_num'], record['sec'],
                    record['of'], record['fecha'], record['codcal'], record['desccal'],
                    record['created_at']
                ))
            
            # 4. Eliminar registros de la tabla principal
            cursor.execute(f"DELETE FROM bobina WHERE id IN ({ids_str})", selected_ids)
            
            conn.commit()
            conn.close()
            
            return True, f"Operación completada. {len(selected_records)} registros procesados. Archivo generado: {csv_filename}"
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return False, f"Error: {str(e)}"


class AuthManager:
    def __init__(self, credentials_file="credenciales.enc"):
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
        except:
            return False


class LoginScreen(ft.Control):
    def __init__(self, page, on_login_success):
        super().__init__()
        self.page = page
        self.on_login_success = on_login_success
        self.auth_manager = AuthManager()
        
        # Elementos de UI
        self.username_field = ft.TextField(
            label="Usuario",
            border=ft.InputBorder.UNDERLINE,
            prefix_icon=ft.icons.PERSON,
            width=300
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.UNDERLINE,
            prefix_icon=ft.icons.LOCK,
            width=300
        )
        
        self.login_button = ft.ElevatedButton(
            text="Ingresar",
            icon=ft.icons.LOGIN,
            bgcolor=ft.colors.GREEN_700,  # #2E7D32
            color=ft.colors.WHITE,
            width=300,
            on_click=self.try_login
        )
        
        self.error_text = ft.Text(
            value="",
            color=ft.colors.RED_700,
            size=14,
            visible=False
        )
        
        # Carga del logo
        if not os.path.exists("logo.png"):
            # Si no existe el logo, usamos un placeholder de texto
            self.logo = ft.Text(
                value="📜 Sistema Manager de Producción",
                color=ft.colors.GREEN_900,  # #1B5E20
                size=28,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            )
        else:
            self.logo = ft.Image(
                src="logo.png",
                width=150,
                height=150,
                fit=ft.ImageFit.CONTAIN,
            )
    
    def build(self):
        return ft.Container(
            width=self.page.width,
            height=self.page.height,
            bgcolor=ft.colors.GREEN_50,  # #C8E6C9
            alignment=ft.alignment.center,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.logo,
                    ft.Text(
                        value="Sistema Manager de Producción",
                        color=ft.colors.GREEN_900,  # #1B5E20
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=20),
                    self.username_field,
                    self.password_field,
                    ft.Container(height=10),
                    self.login_button,
                    self.error_text,
                ],
                spacing=10,
            ),
        )
    
    def try_login(self, e):
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.error_text.value = "Por favor, complete todos los campos."
            self.error_text.visible = True
            self.update()
            return
        
        # Mostrar spinner de carga
        self.page.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Verificando credenciales...")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.dialog.open = True
        self.page.update()
        
        # Utilizar un hilo para no bloquear la UI
        def auth_process():
            time.sleep(0.5)  # Simulamos un pequeño retardo
            success = self.auth_manager.verify_credentials(username, password)
            
            # Actualizar UI en el hilo principal
            self.page.dialog.open = False
            
            if success:
                self.error_text.visible = False
                self.on_login_success()
            else:
                self.error_text.value = "Credenciales incorrectas. Intente nuevamente."
                self.error_text.visible = True
                self.update()
            
            self.page.update()
        
        threading.Thread(target=auth_process).start()


class MainScreen(ft.Control):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.db_manager = DatabaseManager()
        
        # Lista para almacenar los IDs seleccionados
        self.selected_ids = []
        
        # Definición de la tabla
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Row([
                        ft.Checkbox(on_change=self.select_all_changed),
                        ft.Text("ID")
                    ])
                ),
                ft.DataColumn(ft.Text("Turno")),
                ft.DataColumn(ft.Text("Ancho")),
                ft.DataColumn(ft.Text("Diámetro")),
                ft.DataColumn(ft.Text("Gramaje")),
                ft.DataColumn(ft.Text("Peso")),
                ft.DataColumn(ft.Text("Bobina Num")),
                ft.DataColumn(ft.Text("Sec")),
                ft.DataColumn(ft.Text("OF")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("CodCal")),
                ft.DataColumn(ft.Text("DescCal")),
                ft.DataColumn(ft.Text("Created At")),
            ],
            rows=[]
        )
        
        # Elementos de búsqueda/filtro
        self.search_fields = {}
        for column in ["id", "turno", "ancho", "diametro", "gramaje", "peso", 
                      "bobina_num", "sec", "of", "fecha", "codcal", "desccal", "created_at"]:
            self.search_fields[column] = ft.TextField(
                hint_text=f"Buscar {column}",
                border=ft.InputBorder.UNDERLINE,
                height=40,
                text_size=14,
                content_padding=ft.padding.only(left=10, right=10, top=0, bottom=0),
                on_change=self.apply_filters
            )
        
        # Botón para generar archivo
        self.generate_button = ft.ElevatedButton(
            text="Generar Archivo",
            icon=ft.icons.FILE_DOWNLOAD,
            bgcolor=ft.colors.GREEN_700,  # #2E7D32
            color=ft.colors.WHITE,
            on_click=self.confirm_export
        )
    
    def build(self):
        # Crear fila de filtros
        filter_row = ft.Row(
            controls=[
                self.search_fields[col] for col in [
                    "id", "turno", "ancho", "diametro", "gramaje", "peso", 
                    "bobina_num", "sec", "of", "fecha", "codcal", "desccal", "created_at"
                ]
            ],
            scroll=ft.ScrollMode.AUTO
        )
        
        return ft.Container(
            width=self.page.width,
            height=self.page.height,
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Sistema Manager de Producción",
                                color=ft.colors.GREEN_900,  # #1B5E20
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(expand=True),
                            self.generate_button,
                        ],
                    ),
                    ft.Divider(),
                    filter_row,
                    ft.Container(
                        content=self.table,
                        expand=True,
                        border=ft.border.all(1, ft.colors.BLACK12),
                        border_radius=5,
                        padding=10,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
        )
    
    def did_mount(self):
        self.load_data()
    
    def load_data(self):
        """Carga los datos de la base de datos y actualiza la tabla."""
        # Mostrar spinner de carga
        self.page.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Cargando datos...")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.dialog.open = True
        self.page.update()
        
        def load_process():
            # Obtener datos de la base de datos
            data = self.db_manager.get_all_bobinas()
            
            # Actualizar la tabla en el hilo principal
            self.page.dialog.open = False
            self.update_table(data)
            self.page.update()
        
        threading.Thread(target=load_process).start()
    
    def update_table(self, data):
        """Actualiza la tabla con los datos proporcionados."""
        # Limpiar filas actuales
        self.table.rows.clear()
        
        # Agregar nuevas filas
        for row in data:
            checkbox = ft.Checkbox(
                value=False, 
                data=row["id"],
                on_change=self.checkbox_changed
            )
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row([checkbox, ft.Text(str(row["id"]))])),
                        ft.DataCell(ft.Text(row["turno"])),
                        ft.DataCell(ft.Text(str(row["ancho"]))),
                        ft.DataCell(ft.Text(str(row["diametro"]))),
                        ft.DataCell(ft.Text(str(row["gramaje"]))),
                        ft.DataCell(ft.Text(str(row["peso"]))),
                        ft.DataCell(ft.Text(row["bobina_num"])),
                        ft.DataCell(ft.Text(row["sec"] if row["sec"] else "")),
                        ft.DataCell(ft.Text(row["of"])),
                        ft.DataCell(ft.Text(row["fecha"])),
                        ft.DataCell(ft.Text(row["codcal"] if row["codcal"] else "")),
                        ft.DataCell(ft.Text(row["desccal"] if row["desccal"] else "")),
                        ft.DataCell(ft.Text(row["created_at"])),
                    ]
                )
            )
        
        self.update()
    
    def checkbox_changed(self, e):
        """Maneja el cambio de estado de los checkboxes de selección."""
        if e.control.value:
            if e.control.data not in self.selected_ids:
                self.selected_ids.append(e.control.data)
        else:
            if e.control.data in self.selected_ids:
                self.selected_ids.remove(e.control.data)
        
        # Actualizar estado del botón
        self.generate_button.disabled = len(self.selected_ids) == 0
        self.update()
    
    def select_all_changed(self, e):
        """Maneja el evento de seleccionar/deseleccionar todos."""
        select_all = e.control.value
        
        self.selected_ids.clear()
        
        for row in self.table.rows:
            # El checkbox está en la primera celda dentro de un Row
            checkbox = row.cells[0].content.controls[0]
            checkbox.value = select_all
            
            if select_all:
                self.selected_ids.append(checkbox.data)
        
        # Actualizar estado del botón
        self.generate_button.disabled = len(self.selected_ids) == 0
        self.update()
    
    def apply_filters(self, e):
        """Aplica los filtros de búsqueda a los datos."""
        # Recoger todos los valores de filtro
        filters = {}
        for column, field in self.search_fields.items():
            if field.value:
                filters[column] = field.value.lower()
        
        # Si no hay filtros, cargar todos los datos
        if not filters:
            self.load_data()
            return
        
        # Obtener todos los datos y filtrar en memoria
        data = self.db_manager.get_all_bobinas()
        filtered_data = []
        
        for row in data:
            match = True
            for column, filter_value in filters.items():
                cell_value = str(row[column]).lower()
                if filter_value not in cell_value:
                    match = False
                    break
            
            if match:
                filtered_data.append(row)
        
        # Actualizar la tabla con los datos filtrados
        self.update_table(filtered_data)
    
    def confirm_export(self, e):
        """Muestra un diálogo de confirmación para la exportación."""
        if not self.selected_ids:
            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Atención"),
                content=ft.Text("No hay registros seleccionados para exportar."),
                actions=[
                    ft.TextButton("Aceptar", on_click=lambda _: self.close_dialog())
                ],
            )
            self.page.dialog.open = True
            self.page.update()
            return
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar acción"),
            content=ft.Text(
                f"Se exportarán y moverán {len(self.selected_ids)} registros al archivo histórico. "
                "Esta acción no se puede deshacer. ¿Desea continuar?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.TextButton("Continuar", on_click=self.export_data),
            ],
        )
        self.page.dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        """Cierra el diálogo actual."""
        self.page.dialog.open = False
        self.page.update()
    
    def export_data(self, e):
        """Exporta los datos seleccionados y los mueve a la tabla histórica."""
        # Cerrar el diálogo de confirmación
        self.close_dialog()
        
        # Mostrar spinner de carga
        self.page.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Procesando registros...")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.dialog.open = True
        self.page.update()
        
        def export_process():
            success, message = self.db_manager.move_to_history_and_export(self.selected_ids)
            
            # Actualizar UI en el hilo principal
            self.page.dialog.open = False
            
            # Mostrar resultado
            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Resultado de la operación"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("Aceptar", on_click=lambda _: self.process_result(success))
                ],
            )
            self.page.dialog.open = True
            self.page.update()
        
        threading.Thread(target=export_process).start()
    
    def process_result(self, success):
        """Procesa el resultado de la exportación."""
        self.close_dialog()
        
        if success:
            # Limpiar selecciones y recargar datos
            self.selected_ids.clear()
            self.load_data()


class ProductionManagerApp:
    def __init__(self):
        self.page = None
    
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Sistema Manager de Producción"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ft.colors.WHITE
        page.padding = 0
        
        # Configurar tema con colores corporativos
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.GREEN_900,  # #1B5E20
                primary_container=ft.colors.GREEN_100,
                secondary=ft.colors.GREEN_700,  # #2E7D32
                surface=ft.colors.WHITE,
                background=ft.colors.GREEN_50,  # #C8E6C9
            )
        )
        
        page.window_width = 1200
        page.window_height = 800
        page.window_min_width = 800
        page.window_min_height = 600
        
        # Establecer vista inicial (login)
        self.show_login_screen()
        
        # Manejar eventos de cambio de tamaño
        def page_resize(e):
            # Asegurarse de que los controles se ajusten al nuevo tamaño
            page.update()
        
        page.on_resize = page_resize
    
    def show_login_screen(self):
        self.page.controls.clear()
        login_screen = LoginScreen(self.page, self.show_main_screen)
        self.page.add(login_screen)
        self.page.update()
    
    def show_main_screen(self):
        self.page.controls.clear()
        main_screen = MainScreen(self.page)
        self.page.add(main_screen)
        self.page.update()


# Punto de entrada de la aplicación
if __name__ == "__main__":
    app = ProductionManagerApp()
    ft.app(target=app.main)