import flet as ft
from utils.constants import COLOR_PRIMARY, COLOR_SECONDARY
from utils.preferences import save_theme_preference

class LoginScreen(ft.Container):
    """
    Clase para la pantalla de inicio de sesión.
    Proporciona una interfaz moderna para autenticación de usuarios.
    """
    def __init__(self, page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        
        # Configure page properties
        if self.page:
            self.page.window_center = True
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.title = "Login - Sistema Manager de Producción"
            
        # Create form fields
        self.username_field = ft.TextField(
            label="Usuario",
            border=ft.InputBorder.OUTLINE,
            prefix_icon=ft.icons.PERSON,
            width=300,
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            border=ft.InputBorder.OUTLINE,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK,
            width=300,
        )
        
        # Create login button
        self.login_button = ft.ElevatedButton(
            text="Iniciar Sesión",
            icon=ft.icons.LOGIN,
            bgcolor=COLOR_SECONDARY,
            color=ft.colors.WHITE,
            width=300,
            on_click=self.login,
        )
        
        # In the __init__ method:
        # Create theme toggle
        self.theme_toggle = ft.IconButton(
            icon=ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE,
            tooltip="Cambiar tema",
            on_click=self.toggle_theme_mode,
        )
        
        # Create login form
        login_form = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [self.theme_toggle],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                        ft.Row(
                            [
                                ft.Icon(
                                    name=ft.icons.ACCOUNT_CIRCLE,
                                    size=100,
                                    color=COLOR_PRIMARY,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [
                                ft.Text(
                                    "Sistema Manager de Producción",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_PRIMARY,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Divider(),
                        self.username_field,
                        self.password_field,
                        ft.Container(height=20),
                        self.login_button,
                        ft.Container(height=10),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=30,
                width=400,
            ),
            elevation=15,
            surface_tint_color=COLOR_SECONDARY,
        )
        
        # Create main content
        content = ft.Container(
            content=ft.Column(
                [
                    login_form,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            expand=True,
            alignment=ft.alignment.center,
        )
        
        # Initialize container
        super().__init__(
            expand=True,
            content=content,
        )
    
    from utils.constants import save_theme_preference
    
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
    
    def login(self, e):
        """Handle login button click"""
        username = self.username_field.value
        password = self.password_field.value
        
        # Simple validation
        if not username or not password:
            self.show_error("Por favor, complete todos los campos.")
            return
        
        # Check credentials against the stored credentials
        try:
            import json
            import bcrypt
            import os
            
            # Load credentials
            creds_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credenciales.enc')
            with open(creds_file, 'r') as f:
                credentials = json.load(f)
            
            # Check if user exists
            if username in credentials:
                # Verify password
                stored_hash = credentials[username]
                password_bytes = password.encode('utf-8')
                stored_hash_bytes = stored_hash.encode('utf-8')
                
                if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                    # Call the success callback
                    if self.on_login_success:
                        self.on_login_success()
                else:
                    self.show_error("Usuario o contraseña incorrectos.")
            else:
                self.show_error("Usuario o contraseña incorrectos.")
        except Exception as e:
            print(f"Login error: {str(e)}")
            self.show_error(f"Error al iniciar sesión: {str(e)}")
    
    def show_error(self, message):
        """Show error dialog"""
        error_dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda e: self.close_dialog(e)),
            ],
        )
        self.page.dialog = error_dialog
        error_dialog.open = True
        self.page.update()
    
    def close_dialog(self, e):
        """Close the current dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()