import os
import sys
import json
import glob

class SettingsManager:
    def __init__(self, settings_file="configs/app_settings.json"):
        """Ensure settings file exists in the correct configs folder."""
        self.base_path = self._get_base_path()

        # Force configs to be at the same level as 'ui'
        self.settings_dir = os.path.join(self.base_path, "configs")
        os.makedirs(self.settings_dir, exist_ok=True)

        self.settings_file = os.path.join(self.settings_dir, "app_settings.json")

        if not os.path.exists(self.settings_file):
            print("DEBUG: Settings file missing, creating default settings...")
            self._set_defaults()
            self.save_settings()
        else:
            self.load_settings()

    def _get_base_path(self):
        """Get base directory, ensuring it is at the same level as 'ui'."""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

        # If running inside 'ui', move up one level
        if os.path.basename(base_path) == "ui":
            return os.path.dirname(base_path)
        return base_path

    def load_settings(self):
        """Load settings from the JSON file."""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading settings: {str(e)}. Resetting to defaults.")
            self._set_defaults()
            self.save_settings()

    def _set_defaults(self):
        """Define default settings and detect available docs."""
        docs_path = os.path.join(self.base_path, "docs")

        # Auto-detect latest documentation versions
        user_guide = self._find_latest_document(docs_path, "yt_downloader_user_guide_v*.pdf")
        dev_guide = self._find_latest_document(docs_path, "yt_downloader_dev_documentation_v*.pdf")

        self.settings = {
            "storage": {
                "download_directory": os.path.expanduser("~/Downloads")
            },
            "documentation": {
                "user_guide": user_guide or "",
                "developer_guide": dev_guide or ""
            },
            "ui": {
                "theme": {
                    "dark_mode": True
                }
            }
        }

    def save_settings(self):
        """Save current settings to the JSON file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error saving settings: {str(e)}")

    def get_setting(self, key_path, default=None):
        """
        Retrieve a setting value using dot notation.
        Example: get_setting("documentation.user_guide")
        """
        keys = key_path.split('.')
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set_setting(self, key_path, value):
        """
        Set a setting value using dot notation and save the updated settings.
        Example: set_setting("ui.theme.dark_mode", True)
        """
        keys = key_path.split('.')
        data = self.settings
        for key in keys[:-1]:
            data = data.setdefault(key, {})

        data[keys[-1]] = value
        self.save_settings()

    def get_all_settings(self):
        """Returns all settings as a dictionary."""
        return self.settings

    def _find_latest_document(self, docs_path, pattern):
        """
        Find the latest document matching the given pattern.
        Example: "yt_downloader_user_guide_v*.pdf"
        """
        if not os.path.exists(docs_path):
            return None

        files = glob.glob(os.path.join(docs_path, pattern))
        if not files:
            return None

        # Sort by version (assumes format "vX.Y" in filename)
        files.sort(key=lambda f: self._extract_version(f), reverse=True)
        return files[0]

    def _extract_version(self, filename):
        """Extracts a version number from a filename (e.g., 'v0.2' -> 0.2)."""
        import re
        match = re.search(r'v(\d+\.\d+)', filename)
        return float(match.group(1)) if match else 0.0
