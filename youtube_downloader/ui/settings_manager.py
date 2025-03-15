# ui/settings_manager.py
import os
import json

class SettingsManager:
    def __init__(self, settings_file="~/.yt_downloader_settings.json"):
        self.settings_file = os.path.expanduser(settings_file)
        self.settings = {}

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {  # Default settings
                    "save_path": os.path.expanduser("~/Downloads"),
                    "dark_mode": True
                }
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            # Fallback to default settings even if there's an error
            self.settings = {
                "save_path": os.path.expanduser("~/Downloads"),
                "dark_mode": True
            }

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value