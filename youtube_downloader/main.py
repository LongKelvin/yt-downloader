# main.py
import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from ui.ui_manager import UIManager
from ui.search_controller import SearchController
from ui.download_controller import DownloadController
from ui.settings_manager import SettingsManager
from ui.file_controller import FileController
from ui.about_window import AboutDialog


class AppController(QObject):
    status_message_updated = pyqtSignal(str)  # new signal for status updates

    def __init__(self, ui_manager, search_controller, download_controller, settings_manager, file_controller):
        super().__init__()
        self.ui_manager = ui_manager
        self.search_controller = search_controller
        self.download_controller = download_controller
        self.settings_manager = settings_manager
        self.file_controller = file_controller

        # Load settings
        self.settings_manager.load_settings()

        # Apply settings to UI
        self.ui_manager.set_save_path(self.settings_manager.get_setting("storage.download_directory"))
        self.ui_manager.set_dark_mode(self.settings_manager.get_setting("ui.theme.dark_mode", True))  # Default True
        self.ui_manager.dark_mode_check.setChecked(self.settings_manager.get_setting("ui.theme.dark_mode", True))
        
        # Get the base directory of the application
        base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

        # Load file paths from settings
        user_guide_path = os.path.join(base_dir, self.settings_manager.get_setting("documentation.user_guide"))
        dev_guide_path = os.path.join(base_dir, self.settings_manager.get_setting("documentation.developer_guide"))

        # --- Connect Signals and Slots ---
        # UI -> Controller
        self.ui_manager.search_requested.connect(self.search_videos)
        self.ui_manager.cancel_requested.connect(self.cancel_download)
        self.ui_manager.path_browse_requested.connect(self.browse_for_path)
        self.ui_manager.theme_change_requested.connect(self.set_dark_mode)
        self.ui_manager.help_user_requested.connect(lambda: file_controller.open_file(user_guide_path))
        self.ui_manager.help_dev_requested.connect(lambda: file_controller.open_file(dev_guide_path))
        self.ui_manager.about_requested.connect(self.show_about_dialog)
        self.ui_manager.system_exit_requested.connect(self.exit_application)
        
        # Download handler
        self.ui_manager.download_requested.connect(self.handle_download_request)

        # SearchController -> UI
        self.search_controller.search_results_ready.connect(self.handle_search_results_ready)
        self.search_controller.search_error.connect(lambda msg: self.ui_manager.show_error("Search Error", msg))
        self.search_controller.search_error.connect(self.ui_manager.set_status_message)  # Update status

        # DownloadController -> UI
        self.download_controller.download_progress.connect(self.ui_manager.set_progress_value)
        self.download_controller.download_finished.connect(
            lambda msg: self.ui_manager.show_message("Download Finished", msg)
        )
        self.download_controller.download_finished.connect(
            lambda msg: self.ui_manager.set_status_message("Ready")  # Reset status
        )
        self.download_controller.download_error.connect(lambda msg: self.ui_manager.show_error("Download Error", msg))
        self.download_controller.download_error.connect(self.ui_manager.set_status_message)  # Update status

        # File Controller
        self.file_controller.file_open_error.connect(lambda msg: self.ui_manager.show_error("File Error", msg))

        # Status signal
        self.status_message_updated.connect(self.ui_manager.set_status_message)

        # UI Update on item selection
        self.ui_manager.results_list.itemClicked.connect(self.on_item_selected)

    def on_item_selected(self, item):
        """Handles item selection, triggering UI updates and format population."""
        video_info = item.data(Qt.ItemDataRole.UserRole)
        if video_info:
            self.ui_manager.populate_quality_combo(video_info)

    def start(self):
        pass

    def set_dark_mode(self, is_dark_mode):
        """Toggle dark mode and save the setting."""
        self.settings_manager.set_setting("ui.theme.dark_mode", is_dark_mode)
        self.ui_manager.set_dark_mode(is_dark_mode)

    def browse_for_path(self):
        """Open a directory selection dialog and update the setting."""
        path = QFileDialog.getExistingDirectory(
            self.ui_manager, "Select Save Folder", self.settings_manager.get_setting("storage.download_directory")
        )
        if path:
            self.settings_manager.set_setting("storage.download_directory", path)
            self.ui_manager.set_save_path(path)

    def search_videos(self, query):
        """Starts the search process, updating the status."""
        self.ui_manager.set_status_message("Searching...")
        self.search_controller.search(query)
        
    def handle_download_request(self, url, quality):
        """Handles the download request by fetching the save path and initiating the download."""
        save_path = self.settings_manager.get_setting(
            "storage.download_directory",
            os.path.expanduser("~/Downloads")
        )

        # Now pass the correct save_path
        self.start_download(url, quality, save_path)

    def start_download(self, url, quality, save_path):
        """Starts the download process via the DownloadController."""
        print(f"Starting download: {url} | Quality: {quality} | Save to: {save_path}")
        self.ui_manager.set_status_message("Preparing download...")
        self.ui_manager.set_progress_value(0)
        self.ui_manager.download_button.setEnabled(False)
        self.ui_manager.cancel_button.setEnabled(True)
        self.download_controller.download(url, quality, save_path)

    def cancel_download(self):
        """Cancel the current download."""
        self.status_message_updated.emit("Download cancelled.")
        self.download_controller.cancel_download()

    def show_about_dialog(self):
        about_dialog = AboutDialog()
        about_dialog.exec()

    def handle_search_results_ready(self, results):
        self.ui_manager.display_results(results)
        self.ui_manager.set_status_message("Ready")
        
    def exit_application(self):
        QApplication.exit()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    settings_manager = SettingsManager()  # Create SettingsManager
    ui_manager = UIManager()  # Create UI Manager
    search_controller = SearchController()  # Create SearchController
    download_controller = DownloadController()  # Create DownloadController
    file_controller = FileController()  # Create FileController

    controller = AppController(ui_manager, search_controller, download_controller, settings_manager, file_controller)
    controller.start()

    # Use QMainWindow to wrap UIManager
    main_window = QMainWindow()
    main_window.setCentralWidget(ui_manager)
    main_window.setWindowTitle("YouTube Video Downloader")
    main_window.setMinimumSize(800, 600)
    main_window.show()

    sys.exit(app.exec())
