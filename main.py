import flet as ft
from controllers.app_controller import AppController

if __name__ == "__main__":
    app_controller = AppController()
    ft.app(target=app_controller.main)