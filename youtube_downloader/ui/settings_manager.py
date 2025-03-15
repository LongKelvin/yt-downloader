# ui/settings_manager.py
import os
import json
import glob

class SettingsManager:
    def __init__(self, settings_file="configs/app_settings.json"):
        self.settings_file = os.path.abspath(settings_file)
        self.settings = {}

        # Ensure settings file exists
        if not os.path.exists(self.settings_file):
            self._set_defaults()
            self.save_settings()
        else:
            self.load_settings()

    def load_settings(self):
        """Load settings from the JSON file with default fallbacks."""
        try:
            with open(self.settings_file, 'r', encoding="utf-8") as f:
                self.settings = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("Error loading settings. Resetting to defaults.")
            self._set_defaults()
            self.save_settings()

    def _set_defaults(self):
        """Set default settings if the file is missing or invalid."""
        user_guide = self._find_latest_documentation("yt_downloader_user_guide")
        dev_guide = self._find_latest_documentation("yt_downloader_dev_documentation_v")

        self.settings = {
            "storage": {
                "download_directory": os.path.expanduser("~/Downloads")
            },
            "documentation": {
                "user_guide": user_guide if user_guide else "",
                "developer_guide": dev_guide if dev_guide else ""
            },
            "ui": {
                "theme": {
                    "dark_mode": True
                }
            }
        }

    def save_settings(self):
        """Save current settings to the JSON file."""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)  # Ensure directory exists
        try:
            with open(self.settings_file, 'w', encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")

    def get_setting(self, key, default=None):
        """Retrieve a nested setting using dot notation."""
        keys = key.split(".")
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, {})
            else:
                return default
        return value if value else default

    def set_setting(self, key, value):
        """Set a nested setting using dot notation."""
        keys = key.split(".")
        data = self.settings
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
        self.save_settings()

    def _find_latest_documentation(self, pattern):
        """
        Find the latest PDF file matching the given pattern in the docs directory.
        Returns the most recent match or None if no files are found.
        """
        docs_dir = "docs"
        if not os.path.exists(docs_dir):
            return None  # No docs folder

        files = glob.glob(os.path.join(docs_dir, f"{pattern}*.pdf"))
        return max(files, key=os.path.getctime) if files else None
