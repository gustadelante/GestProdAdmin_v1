import flet as ft
from views.login_screen import LoginScreen
from views.main_screen import MainScreen
from utils.constants import load_theme_preference

def main(page: ft.Page):
    # Load user theme preference
    is_dark_mode = load_theme_preference()
    
    # Set page properties
    page.title = "Gestión de Producción"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK if is_dark_mode else ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.window_center = True
    
    # Function to handle successful login
    def on_login_success():
        # Remove login screen
        page.controls.clear()
        
        # Add main screen
        main_screen = MainScreen(page)
        page.add(main_screen)
        
        # Call did_mount to load data
        if hasattr(main_screen, 'did_mount'):
            main_screen.did_mount()
        
        page.update()
    
    # Add login screen
    login_screen = LoginScreen(page, on_login_success)
    page.add(login_screen)
    
    page.update()

if __name__ == "__main__":
    ft.app(target=main)