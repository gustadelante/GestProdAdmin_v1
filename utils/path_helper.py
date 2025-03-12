import os
import sys

def get_app_path():
    """Returns the application base path."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (pyinstaller)
        return os.path.dirname(sys.executable)
    else:
        # If the application is run as a script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_path():
    """Returns the data directory path."""
    data_dir = os.path.join(get_app_path(), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def get_db_path():
    """Returns the database file path."""
    return os.path.join(get_data_path(), 'produccion.db')