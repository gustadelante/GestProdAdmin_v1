import os
import flet as ft
import threading
import time
from models.auth_manager import AuthManager
from utils.constants import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, LOGO_FILE

class LoginScreen(ft.Container):
    """
    Clase para la pantalla de inicio de sesión.
    Proporciona la interfaz para autenticación de usuarios.
    """
    def __init__(self, page, on_login_success):
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
            bgcolor=COLOR_SECONDARY,
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
        if not os.path.exists(LOGO_FILE):
            # Si no existe el logo, usamos un placeholder de texto
            self.logo = ft.Text(
                value="📜 Sistema Manager de Producción",
                color=COLOR_PRIMARY,
                size=28,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            )
        else:
            self.logo = ft.Image(
                src=LOGO_FILE,
                width=150,
                height=150,
                fit=ft.ImageFit.CONTAIN,
            )
        
        # Create the content column
        content_column = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.logo,
                ft.Text(
                    value="Sistema Manager de Producción",
                    color=COLOR_PRIMARY,
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
        )
        
        # Initialize the container with the content
        super().__init__(
            width=page.width,
            height=page.height,
            bgcolor=COLOR_BACKGROUND,
            alignment=ft.alignment.center,
            content=content_column
        )
        
        # Set focus to username field when the screen loads
        self.username_field.autofocus = True
    
    def try_login(self, e):
        """Intenta iniciar sesión con las credenciales proporcionadas."""
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
            
            # Use a try-except block to handle potential NoneType errors
            try:
                # Check if page is still available
                if self.page is None:
                    return
                    
                # Actualizar UI en el hilo principal
                self.page.dialog.open = False
                
                if success:
                    self.error_text.visible = False
                    self.on_login_success()
                else:
                    self.error_text.value = "Credenciales incorrectas. Intente nuevamente."
                    self.error_text.visible = True
                    self.update()
                
                # Final check before updating page
                if self.page is not None:
                    self.page.update()
            except Exception as e:
                # Silently handle any exceptions that might occur if page becomes None
                print(f"Error during authentication process: {e}")
        
        threading.Thread(target=auth_process).start()