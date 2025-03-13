import flet as ft
import threading
from models.database_manager import DatabaseManager
from utils.constants import COLOR_PRIMARY, COLOR_SECONDARY, save_theme_preference

class MainScreen(ft.Container):  # Changed from ft.UserControl to ft.Container
    """
    Clase para la pantalla principal de la aplicación.
    Muestra la tabla de datos y proporciona funcionalidades para filtrar y exportar datos.
    """
    def __init__(self, page, db_manager=None):
        self.page = page
        
        # Initialize database manager with proper path handling
        if db_manager:
            self.db_manager = db_manager
        else:
            from models.database_manager import DatabaseManager
            self.db_manager = DatabaseManager()
        
        # Configure page properties for centered window
        if self.page:
            self.page.window_center = True
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.title = "Sistema Manager de Producción"
        
        # Lista para almacenar los IDs seleccionados
        self.selected_ids = []
        
        # Variables para el ordenamiento
        self.sort_column_index = None
        self.sort_ascending = True
        
        # Definición de la tabla
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Row([
                        ft.Checkbox(on_change=self.select_all_changed),
                        ft.Text("ID")
                    ]),
                    on_sort=lambda e: self.sort_data(0, e.ascending)
                ),
                ft.DataColumn(ft.Text("Turno"), on_sort=lambda e: self.sort_data(1, e.ascending)),
                ft.DataColumn(ft.Text("Ancho"), on_sort=lambda e: self.sort_data(2, e.ascending)),
                ft.DataColumn(ft.Text("Diámetro"), on_sort=lambda e: self.sort_data(3, e.ascending)),
                ft.DataColumn(ft.Text("Gramaje"), on_sort=lambda e: self.sort_data(4, e.ascending)),
                ft.DataColumn(ft.Text("Peso"), on_sort=lambda e: self.sort_data(5, e.ascending)),
                ft.DataColumn(ft.Text("Bobina Num"), on_sort=lambda e: self.sort_data(6, e.ascending)),
                ft.DataColumn(ft.Text("Sec"), on_sort=lambda e: self.sort_data(7, e.ascending)),
                ft.DataColumn(ft.Text("OF"), on_sort=lambda e: self.sort_data(8, e.ascending)),
                ft.DataColumn(ft.Text("Fecha"), on_sort=lambda e: self.sort_data(9, e.ascending)),
                ft.DataColumn(ft.Text("CodCal"), on_sort=lambda e: self.sort_data(10, e.ascending)),
                ft.DataColumn(ft.Text("DescCal"), on_sort=lambda e: self.sort_data(11, e.ascending)),
                ft.DataColumn(ft.Text("Created At"), on_sort=lambda e: self.sort_data(12, e.ascending)),
            ],
            rows=[],
            sort_column_index=self.sort_column_index,
            sort_ascending=self.sort_ascending,
            expand=True,  # Add expand property to the table
        )
        
        # Elementos de búsqueda/filtro
        self.search_fields = {}
        # Only include the specified columns for filtering
        for column in ["of", "fecha", "codcal", "created_at"]:
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
            bgcolor=COLOR_SECONDARY,
            color=ft.colors.WHITE,
            on_click=self.confirm_export,
            disabled=True
        )
        
        # Botón para eliminar registros seleccionados
        self.delete_button = ft.ElevatedButton(
            text="Eliminar",
            icon=ft.icons.DELETE,
            bgcolor=ft.colors.RED_600,
            color=ft.colors.WHITE,
            on_click=self.confirm_delete,
            disabled=True
        )
        
        # Botón para añadir nuevo registro (opcional)
        self.add_button = ft.ElevatedButton(
            text="Añadir Registro",
            icon=ft.icons.ADD,
            bgcolor=COLOR_SECONDARY,
            color=ft.colors.WHITE,
            on_click=self.show_add_form,
        )
        
        # Create AppBar with menu
        self.create_app_bar()
        
        # Create filter row
        filter_row = ft.Row(
            controls=[
                self.search_fields[col] for col in [
                    "of", "fecha", "codcal", "created_at"
                ]
            ],
            scroll=ft.ScrollMode.AUTO
        )
        
        # Create main content
        content = ft.Column(
            controls=[
                self.app_bar,  # Add the AppBar at the top
                ft.Divider(),
                filter_row,
                ft.Container(
                    content=ft.Column([
                        self.table,
                    ], expand=True, scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    border=ft.border.all(1, ft.colors.BLACK12),
                    border_radius=5,
                    padding=10,
                ),
            ],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
        )
        
        # Initialize container
        super().__init__(
            expand=True,
            padding=10,
            content=content,
        )
        
        # Register a resize event handler
        if self.page and hasattr(self.page, 'on_resize'):
            self.page.on_resize = self.on_page_resize
        
        # Don't load data immediately, wait until component is fully mounted
        # self.load_data()  # Comment out or remove this line
    
    def load_data(self):
        """Carga los datos de la base de datos y actualiza la tabla."""
        # Check if page is available
        if not self.page:
            return
            
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
            
            # Actualizar UI en el hilo principal
            if self.page:
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
        
        # Actualizar estado de los botones
        has_selections = len(self.selected_ids) > 0
        self.generate_button.disabled = not has_selections
        self.delete_button.disabled = not has_selections  # Add this line
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
        
        # Actualizar estado de los botones
        has_selections = len(self.selected_ids) > 0
        self.generate_button.disabled = not has_selections
        self.delete_button.disabled = not has_selections  # Add this line
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
        
        # Mostrar spinner de carga
        self.page.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Filtrando datos...")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.dialog.open = True
        self.page.update()
        
        def filter_process():
            # Filtrar datos
            filtered_data = self.db_manager.filter_bobinas(filters)
            
            # Actualizar UI en el hilo principal
            self.page.dialog.open = False
            self.update_table(filtered_data)
            self.page.update()
        
        threading.Thread(target=filter_process).start()
    
    def confirm_export(self, e):
        """Muestra un diálogo de confirmación para la exportación."""
        if not self.selected_ids:
            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Atención"),
                content=ft.Text("No hay registros seleccionados para exportar."),
                actions=[
                    ft.TextButton("Aceptar", on_click=lambda _: self.close_dialog()),
                ],
            )
            # Add the dialog to the page overlay
            self.page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            self.page.update()
            return
        
        confirm_dialog = ft.AlertDialog(
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
        # Add the dialog to the page overlay
        self.page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        self.page.update()
    
    def close_dialog(self, e=None):
        """Cierra el diálogo actual."""
        if self.page and self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
        # Also close any dialogs in the overlay
        if self.page and self.page.overlay:
            for dialog in self.page.overlay:
                if hasattr(dialog, 'open'):
                    dialog.open = False
            self.page.update()
    
    def export_data(self, e):
        """Exporta los datos seleccionados y los mueve a la tabla histórica."""
        # Cerrar el diálogo de confirmación
        self.close_dialog()
        
        # Mostrar spinner de carga
        loading_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Exportando datos...")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        # Add the dialog to the page overlay
        self.page.overlay.append(loading_dialog)
        loading_dialog.open = True
        self.page.update()
        
        # Exportar en un hilo separado para no bloquear la UI
        def export_process():
            try:
                # Obtener los datos de los registros seleccionados
                selected_data = self.db_manager.get_bobinas_by_ids(self.selected_ids)
                
                # Exportar a un archivo CSV
                import csv
                import os
                import sys
                from datetime import datetime
                
                # Determine application path
                if getattr(sys, 'frozen', False):
                    # If the application is run as a bundle (pyinstaller)
                    application_path = os.path.dirname(sys.executable)
                else:
                    # If the application is run as a script
                    application_path = os.path.dirname(os.path.dirname(__file__))
                
                # Crear directorio de exportación si no existe
                export_dir = os.path.join(application_path, 'exports')
                os.makedirs(export_dir, exist_ok=True)
                
                # Generar nombre de archivo con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(export_dir, f"export_{timestamp}.csv")
                
                # Escribir datos al archivo CSV
                with open(filename, 'w', newline='') as csvfile:
                    fieldnames = ['id', 'turno', 'ancho', 'diametro', 'gramaje', 'peso', 
                                 'bobina_num', 'sec', 'of', 'fecha', 'codcal', 'desccal', 'created_at']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for row in selected_data:
                        writer.writerow(row)
                
                # Mover registros a histórico
                success = self.db_manager.move_to_historic(self.selected_ids)
                
                # Actualizar UI en el hilo principal
                if self.page:
                    # Close the loading dialog
                    self.close_dialog()
                    
                    if success:
                        # Limpiar selección
                        self.selected_ids.clear()
                        
                        # Mostrar mensaje de éxito
                        success_dialog = ft.AlertDialog(
                            title=ft.Text("Éxito"),
                            content=ft.Text(f"Datos exportados correctamente a:\n{filename}\n\nLos registros han sido movidos a la tabla histórica."),
                            actions=[
                                ft.TextButton("Aceptar", on_click=lambda _: self.reload_after_export()),
                            ],
                        )
                        self.page.overlay.append(success_dialog)
                        success_dialog.open = True
                    else:
                        # Mostrar mensaje de error
                        self.show_error_dialog("Error al exportar los datos o moverlos a la tabla histórica.")
                    
                    self.page.update()
            except Exception as e:
                # Manejar cualquier error
                if self.page:
                    # Close the loading dialog
                    self.close_dialog()
                    self.show_error_dialog(f"Error: {str(e)}")
                    self.page.update()
        
        threading.Thread(target=export_process).start()
    
    def reload_after_export(self):
        """Recarga los datos después de exportar registros."""
        # Cerrar el diálogo de éxito
        self.close_dialog()
        
        # Recargar los datos
        self.load_data()
        
        # Actualizar estado de los botones
        self.generate_button.disabled = True
        self.delete_button.disabled = True
        self.update()

    def did_mount(self):
        """Called when the component is mounted to the page"""
        # Now it's safe to load data
        self.load_data()

    def confirm_delete(self, e):
        """Muestra un diálogo de confirmación para eliminar registros."""
        if not self.selected_ids:
            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Atención"),
                content=ft.Text("No hay registros seleccionados para eliminar."),
                actions=[
                    ft.TextButton("Aceptar", on_click=lambda _: self.close_dialog()),
                ],
            )
            # Add the dialog to the page overlay
            self.page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            self.page.update()
            return
        
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(
                f"¿Está seguro de que desea eliminar {len(self.selected_ids)} registro(s)? "
                "Esta acción no se puede deshacer."
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog()),
                ft.TextButton("Eliminar", on_click=self.delete_records),
            ],
        )
        # Add the dialog to the page overlay
        self.page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        self.page.update()
    
    def delete_records(self, e):
        """Elimina los registros seleccionados de la base de datos."""
        # Cerrar el diálogo de confirmación
        self.close_dialog()
        
        # Mostrar spinner de carga
        loading_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Eliminando registros...")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        # Add the dialog to the page overlay
        self.page.overlay.append(loading_dialog)
        loading_dialog.open = True
        self.page.update()
        
        # Eliminar en un hilo separado para no bloquear la UI
        def delete_process():
            try:
                # Eliminar registros de la base de datos
                success = self.db_manager.delete_bobinas(self.selected_ids)
                
                # Actualizar UI en el hilo principal
                if self.page:
                    # Close the loading dialog
                    self.close_dialog()
                    
                    if success:
                        # Limpiar selección
                        self.selected_ids.clear()
                        
                        # Mostrar mensaje de éxito
                        success_dialog = ft.AlertDialog(
                            title=ft.Text("Éxito"),
                            content=ft.Text("Registros eliminados correctamente."),
                            actions=[
                                ft.TextButton("Aceptar", on_click=lambda _: self.reload_after_delete()),
                            ],
                        )
                        self.page.overlay.append(success_dialog)
                        success_dialog.open = True
                    else:
                        # Mostrar mensaje de error
                        self.show_error_dialog("Error al eliminar los registros.")
                    
                    self.page.update()
            except Exception as e:
                # Manejar cualquier error
                if self.page:
                    # Close the loading dialog
                    self.close_dialog()
                    self.show_error_dialog(f"Error: {str(e)}")
                    self.page.update()
        
        threading.Thread(target=delete_process).start()
    
    def reload_after_delete(self):
        """Recarga los datos después de eliminar registros."""
        # Cerrar el diálogo de éxito
        self.close_dialog()
        
        # Recargar los datos
        self.load_data()

    def show_add_form(self, e):
        """Muestra el formulario para añadir un nuevo registro."""
        # Crear campos para el formulario
        turno_field = ft.TextField(label="Turno", value="M", hint_text="Ej: A/B/C/D")
        ancho_field = ft.TextField(label="Ancho", hint_text="Ej: 125", keyboard_type=ft.KeyboardType.NUMBER)
        diametro_field = ft.TextField(label="Diámetro", value="120", hint_text="Ej: 120", keyboard_type=ft.KeyboardType.NUMBER)
        gramaje_field = ft.TextField(label="Gramaje", hint_text="Ej: 130", keyboard_type=ft.KeyboardType.NUMBER)
        peso_field = ft.TextField(label="Peso", hint_text="Ej: 250", keyboard_type=ft.KeyboardType.NUMBER)
        bobina_num_field = ft.TextField(label="Bobina Num", hint_text="Ej: 3113")
        sec_field = ft.TextField(label="Sec", hint_text="Ej: 1")
        of_field = ft.TextField(label="OF", value="1", hint_text="Ej: 85500")
        
        # Set current date as default value for fecha_field
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        fecha_field = ft.TextField(label="Fecha", value=current_date, hint_text="Ej: 2025-03-15")
        
        codcal_field = ft.TextField(label="CodCal", hint_text="Ej: 03")
        desccal_field = ft.TextField(label="DescCal", hint_text="Ej: L.BLANCO")
        
        # Define a function to close the dialog
        def close_form_dialog(e):
            form_dialog.open = False
            self.page.update()
        
        # Define a function to save the record
        def save_form_data(e):
            self.save_new_record(
                turno_field.value,
                ancho_field.value,
                diametro_field.value,
                gramaje_field.value,
                peso_field.value,
                bobina_num_field.value,
                sec_field.value,
                of_field.value,
                fecha_field.value,
                codcal_field.value,
                desccal_field.value
            )
        
        # Create the dialog
        form_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Añadir Nuevo Registro"),
            content=ft.Container(
                content=ft.Column(
                    [
                        turno_field,
                        ancho_field,
                        diametro_field,
                        gramaje_field,
                        peso_field,
                        bobina_num_field,
                        sec_field,
                        of_field,
                        fecha_field,
                        codcal_field,
                        desccal_field,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    height=400,
                ),
                width=400,
                padding=10,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_form_dialog),
                ft.TextButton("Guardar", on_click=save_form_data),
            ],
        )
        
        # Add the dialog to the page overlay
        self.page.overlay.append(form_dialog)
        form_dialog.open = True
        self.page.update()
    
    def save_new_record(self, turno, ancho, diametro, gramaje, peso, bobina_num, sec, of, fecha, codcal, desccal):
        """Guarda un nuevo registro en la base de datos."""
        # Get references to all form fields
        form_dialog = None
        for dialog in self.page.overlay:
            if hasattr(dialog, 'title') and isinstance(dialog.title, ft.Text) and dialog.title.value == "Añadir Nuevo Registro":
                form_dialog = dialog
                break
        
        if not form_dialog:
            return
            
        # Get all form fields from the dialog content
        form_fields = []
        if hasattr(form_dialog.content, 'content') and hasattr(form_dialog.content.content, 'controls'):
            form_fields = form_dialog.content.content.controls
        
        # Reset all field borders and helper texts first
        for field in form_fields:
            field.border_color = None
            field.helper_text = None
            if hasattr(field, 'label') and field.label.endswith(' *'):
                field.label = field.label[:-2]  # Remove asterisk
        
        # Validar campos obligatorios
        required_fields = [
            (turno, "Turno", 0),
            (ancho, "Ancho", 1),
            (diametro, "Diámetro", 2),
            (gramaje, "Gramaje", 3),
            (peso, "Peso", 4),
            (bobina_num, "Bobina Num", 5),
            (sec, "Sec", 6),
            (of, "OF", 7),
            (fecha, "Fecha", 8),
            (codcal, "CodCal", 9),
            (desccal, "DescCal", 10)
        ]
        
        # Check all required fields and focus on the first empty one
        first_empty_field = None
        for value, field_name, field_index in required_fields:
            if not value and field_index < len(form_fields):
                form_fields[field_index].border_color = ft.colors.RED
                form_fields[field_index].label = f"{field_name} *"
                form_fields[field_index].helper_text = "Este campo es obligatorio"
                if first_empty_field is None:
                    first_empty_field = form_fields[field_index]
        
        # If any required field is empty, focus on the first one and return
        if first_empty_field:
            first_empty_field.focus()
            self.page.update()
            return
        
        # Convertir valores numéricos
        numeric_error = False
        first_invalid_field = None
        
        numeric_fields = [
            (ancho, "Ancho", 1),
            (diametro, "Diámetro", 2),
            (gramaje, "Gramaje", 3),
            (peso, "Peso", 4)
        ]
        
        for value, field_name, field_index in numeric_fields:
            try:
                if value:  # Only try to convert if there's a value
                    float(value)
            except ValueError:
                # Mark field as invalid
                if field_index < len(form_fields):
                    form_fields[field_index].border_color = ft.colors.RED
                    form_fields[field_index].helper_text = "Debe ser un número válido"
                    numeric_error = True
                    if first_invalid_field is None:
                        first_invalid_field = form_fields[field_index]
        
        # If any numeric field is invalid, focus on the first one and return
        if numeric_error and first_invalid_field:
            first_invalid_field.focus()
            self.page.update()
            return
        
        # Convert numeric values now that we know they're valid
        ancho = float(ancho)
        diametro = float(diametro)
        gramaje = float(gramaje)
        peso = float(peso)
        
        # Cerrar el diálogo del formulario - only if validation passes
        self.close_dialog()
        
        # Mostrar spinner de carga
        loading_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("Guardando registro...")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.overlay.append(loading_dialog)
        loading_dialog.open = True
        self.page.update()
        
        # Guardar en un hilo separado para no bloquear la UI
        def save_process():
            try:
                # Crear diccionario con los datos
                new_record = {
                    "turno": turno,
                    "ancho": ancho,
                    "diametro": diametro,
                    "gramaje": gramaje,
                    "peso": peso,
                    "bobina_num": bobina_num,
                    "sec": sec,
                    "of": of,
                    "fecha": fecha,
                    "codcal": codcal,
                    "desccal": desccal
                }
                
                # Guardar en la base de datos
                success = self.db_manager.add_bobina(new_record)
                
                # Actualizar UI en el hilo principal
                if self.page:
                    self.close_dialog()
                    
                    if success:
                        # Mostrar mensaje de éxito
                        success_dialog = ft.AlertDialog(
                            title=ft.Text("Éxito"),
                            content=ft.Text("Registro guardado correctamente."),
                            actions=[
                                ft.TextButton("Aceptar", on_click=lambda _: self.reload_after_save()),
                            ],
                        )
                        self.page.overlay.append(success_dialog)
                        success_dialog.open = True
                    else:
                        # Mostrar mensaje de error
                        self.show_error_dialog("Error al guardar el registro.")
                    
                    self.page.update()
            except Exception as e:
                # Manejar cualquier error
                if self.page:
                    self.close_dialog()
                    self.show_error_dialog(f"Error: {str(e)}")
                    self.page.update()
        
        threading.Thread(target=save_process).start()
    
    def show_error_dialog(self, message):
        """Muestra un diálogo de error con el mensaje especificado."""
        error_dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda _: self.close_dialog()),
            ],
        )
        self.page.overlay.append(error_dialog)
        error_dialog.open = True
        self.page.update()
    
    def reload_after_save(self):
        """Recarga los datos después de guardar un nuevo registro."""
        # Cerrar el diálogo de éxito
        self.close_dialog()
        
        # Recargar los datos
        self.load_data()

    def sort_data(self, column_index, ascending):
        """Ordena los datos según la columna seleccionada."""
        self.sort_column_index = column_index
        self.sort_ascending = ascending
        self.table.sort_column_index = column_index
        self.table.sort_ascending = ascending
        
        # Obtener los datos actuales
        current_data = []
        for row in self.table.rows:
            row_data = {}
            # Extraer el ID del checkbox
            checkbox = row.cells[0].content.controls[0]
            row_data["id"] = checkbox.data
            
            # Extraer los valores de las celdas
            for i, cell in enumerate(row.cells):
                if i == 0:  # Para la columna ID
                    row_data["id_text"] = cell.content.controls[1].value
                else:
                    # Usar índices para los demás campos
                    row_data[f"column_{i}"] = cell.content.value
            
            current_data.append(row_data)
        
        # Definir la clave de ordenamiento
        if column_index == 0:
            sort_key = "id"
        else:
            sort_key = f"column_{column_index}"
        
        # Ordenar los datos
        sorted_data = sorted(
            current_data, 
            key=lambda x: self._get_sort_value(x.get(sort_key, "")), 
            reverse=not ascending
        )
        
        # Actualizar la tabla con los datos ordenados
        self.table.rows.clear()
        for item in sorted_data:
            checkbox = ft.Checkbox(
                value=item["id"] in self.selected_ids, 
                data=item["id"],
                on_change=self.checkbox_changed
            )
            
            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row([checkbox, ft.Text(str(item["id_text"]))])),
                        ft.DataCell(ft.Text(item.get("column_1", ""))),
                        ft.DataCell(ft.Text(item.get("column_2", ""))),
                        ft.DataCell(ft.Text(item.get("column_3", ""))),
                        ft.DataCell(ft.Text(item.get("column_4", ""))),
                        ft.DataCell(ft.Text(item.get("column_5", ""))),
                        ft.DataCell(ft.Text(item.get("column_6", ""))),
                        ft.DataCell(ft.Text(item.get("column_7", ""))),
                        ft.DataCell(ft.Text(item.get("column_8", ""))),
                        ft.DataCell(ft.Text(item.get("column_9", ""))),
                        ft.DataCell(ft.Text(item.get("column_10", ""))),
                        ft.DataCell(ft.Text(item.get("column_11", ""))),
                        ft.DataCell(ft.Text(item.get("column_12", ""))),
                    ]
                )
            )
        
        self.update()
    
    def _get_sort_value(self, value):
        """Obtiene el valor para ordenamiento, convirtiendo a número si es posible."""
        if value is None:
            return ""
        
        # Intentar convertir a número para ordenamiento numérico
        try:
            return float(value)
        except (ValueError, TypeError):
            # Si no es un número, devolver como string para ordenamiento alfabético
            return str(value).lower()

    def on_page_resize(self, e):
        """Handle window resize events"""
        # Update the container to fill the new window size
        self.width = self.page.width
        self.height = self.page.height
        self.update()

    def create_app_bar(self):
        """Creates the application bar with menu and theme toggle"""
        # Create dropdown menu
        menu_items = [
            ft.PopupMenuItem(text="Exportar seleccionados", icon=ft.icons.FILE_DOWNLOAD, on_click=self.confirm_export),
            ft.PopupMenuItem(text="Eliminar seleccionados", icon=ft.icons.DELETE, on_click=self.confirm_delete),
            ft.PopupMenuItem(text="Añadir nuevo registro", icon=ft.icons.ADD, on_click=self.show_add_form),
            ft.PopupMenuItem(),  # Divider
            ft.PopupMenuItem(text="Acerca de", icon=ft.icons.INFO, on_click=self.show_about),
        ]
        
        # Create the AppBar
        self.app_bar = ft.Row(
            controls=[
                ft.PopupMenuButton(
                    icon=ft.icons.MENU,
                    items=menu_items,
                ),
                ft.Text(
                    "Sistema Manager de Producción",
                    color=COLOR_PRIMARY,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.DARK_MODE,
                    tooltip="Cambiar tema",
                    on_click=self.toggle_theme_mode,
                ),
                self.add_button,
                self.delete_button,
                self.generate_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    
    # In the toggle_theme_mode method:
    def toggle_theme_mode(self, e):
        """Toggle between light and dark theme"""
        if self.page:
            is_dark_mode = self.page.theme_mode == ft.ThemeMode.LIGHT
            self.page.theme_mode = (
                ft.ThemeMode.DARK 
                if is_dark_mode
                else ft.ThemeMode.LIGHT
            )
            
            # Update icon based on current theme
            e.control.icon = (
                ft.icons.LIGHT_MODE 
                if self.page.theme_mode == ft.ThemeMode.DARK 
                else ft.icons.DARK_MODE
            )
            
            # Save user preference
            save_theme_preference(self.page.theme_mode == ft.ThemeMode.DARK)
            
            self.page.update()
    
    def show_about(self, e):
        """Show information about the application"""
        about_dialog = ft.AlertDialog(
            title=ft.Text("Acerca de"),
            content=ft.Column([
                ft.Text("Sistema Manager de Producción"),
                ft.Text("Versión 1.0"),
                ft.Text("© 2023 - Todos los derechos reservados"),
            ]),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self.close_dialog()),
            ],
        )
        self.page.overlay.append(about_dialog)
        about_dialog.open = True
        self.page.update()