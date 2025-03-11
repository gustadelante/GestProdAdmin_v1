import flet as ft
from models.database_manager import DatabaseManager
from models.auth_manager import AuthManager
from views.login_screen import LoginScreen
from views.main_screen import MainScreen

class AppController:
    def __init__(self):
        self.page = None
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager()

    def main(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.show_login_screen()

    def setup_page(self):
        """Configure initial page settings"""
        self.page.title = "Sistema Manager de Producción"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.colors.WHITE
        self.page.padding = 0
        
        # Configure corporate theme
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.GREEN_900,
                primary_container=ft.colors.GREEN_100,
                secondary=ft.colors.GREEN_700,
                surface=ft.colors.WHITE,
                background=ft.colors.GREEN_50,
            )
        )
        
        # Set window properties
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # Handle resize events
        self.page.on_resize = self.handle_resize

    def show_login_screen(self):
        """Display the login screen"""
        self.page.controls.clear()
        login_screen = LoginScreen(self.page, self.show_main_screen)  # Removed self.auth_manager
        self.page.add(login_screen)
        self.page.update()

    def show_main_screen(self):
        """Display the main application screen"""
        self.page.controls.clear()
        main_screen = MainScreen(self.page, self.db_manager)
        self.page.add(main_screen)
        self.page.update()

    def handle_resize(self, e):
        """Handle window resize events"""
        self.page.update()