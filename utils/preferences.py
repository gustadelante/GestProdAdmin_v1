import os
import json

PREFERENCES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_preferences.json')

def save_theme_preference(is_dark_mode):
    """Save the user's theme preference to a file"""
    preferences = {}
    
    # Load existing preferences if available
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, 'r') as f:
                preferences = json.load(f)
        except:
            preferences = {}
    
    # Update theme preference
    preferences['dark_mode'] = is_dark_mode
    
    # Save to file
    try:
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(preferences, f)
        return True
    except:
        return False

def load_theme_preference():
    """Load the user's theme preference from file"""
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, 'r') as f:
                preferences = json.load(f)
                return preferences.get('dark_mode', False)
        except:
            return False
    return False