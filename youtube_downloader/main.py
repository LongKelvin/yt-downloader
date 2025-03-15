# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from ui.ui_manager import UIManager
from ui.search_controller import SearchController
from ui.download_controller import DownloadController
from ui.settings_manager import SettingsManager
from ui.file_controller import FileController # Import FileController
from ui.about_window import AboutDialog
from PyQt6.QtCore import QObject, pyqtSignal, Qt


class AppController(QObject):
    status_message_updated = pyqtSignal(str) # new signal for cancel
    def __init__(self, ui_manager, search_controller, download_controller, settings_manager, file_controller):
        super().__init__()
        self.ui_manager = ui_manager
        self.search_controller = search_controller
        self.download_controller = download_controller
        self.settings_manager = settings_manager
        self.file_controller = file_controller

        # Load settings
        self.settings_manager.load_settings()
        self.ui_manager.set_save_path(self.settings_manager.get_setting("save_path"))
        self.ui_manager.set_dark_mode(self.settings_manager.get_setting("dark_mode", True)) # default True
        self.ui_manager.dark_mode_check.setChecked(self.settings_manager.get_setting("dark_mode", True))

        # --- Connect Signals and Slots ---
        # UI -> Controller
        self.ui_manager.search_requested.connect(self.search_videos) # Connect to local func
        self.ui_manager.download_requested.connect(self.start_download)
        self.ui_manager.cancel_requested.connect(self.cancel_download) # Connect to local func
        self.ui_manager.path_browse_requested.connect(self.browse_for_path)
        self.ui_manager.theme_change_requested.connect(self.set_dark_mode)
        self.ui_manager.help_user_requested.connect(lambda: file_controller.open_file("yt_downloader_user_guide.pdf"))
        self.ui_manager.help_dev_requested.connect(lambda: file_controller.open_file("yt_downloader_dev_documentation_v0.2.pdf"))
        self.ui_manager.about_requested.connect(self.show_about_dialog)


        # SearchController -> UI
        self.search_controller.search_results_ready.connect(self.handle_search_results_ready)
        self.search_controller.search_error.connect(lambda msg: self.ui_manager.show_error("Search Error", msg))
        self.search_controller.search_error.connect(self.ui_manager.set_status_message) # AND update status

        # DownloadController -> UI
        self.download_controller.download_progress.connect(self.ui_manager.set_progress_value)
        self.download_controller.download_finished.connect(lambda msg: self.ui_manager.show_message("Download Finished", msg))
        self.download_controller.download_finished.connect(lambda msg: self.ui_manager.set_status_message("Ready")) # Reset status
        self.download_controller.download_error.connect(lambda msg: self.ui_manager.show_error("Download Error", msg))
        self.download_controller.download_error.connect(self.ui_manager.set_status_message) # AND update status

        # File Controller
        self.file_controller.file_open_error.connect(lambda msg: self.ui_manager.show_error("File Error", msg))

        # cancel signal
        self.status_message_updated.connect(self.ui_manager.set_status_message)


        # --- UI Update on item selection ---
        self.ui_manager.results_list.itemClicked.connect(self.on_item_selected)  # Connect here

    def on_item_selected(self, item):
        """Handles item selection, triggering UI updates and format population."""
        video_info = item.data(Qt.ItemDataRole.UserRole)
        if video_info:
            self.ui_manager.populate_quality_combo(video_info)

    def start(self):
        pass

    def set_dark_mode(self, is_dark_mode):
        self.settings_manager.set_setting("dark_mode", is_dark_mode)
        self.settings_manager.save_settings()
        self.ui_manager.set_dark_mode(is_dark_mode)


    def browse_for_path(self):
        path = QFileDialog.getExistingDirectory(
            self.ui_manager, "Select save folder", self.settings_manager.get_setting("save_path")
        )
        if path:
            self.settings_manager.set_setting("save_path", path)
            self.settings_manager.save_settings()
            self.ui_manager.set_save_path(path)

    def search_videos(self, query):
        """Starts the search process, updating the status."""
        self.ui_manager.set_status_message("Searching...")  # Update status
        self.search_controller.search(query)
        

    def start_download(self, url, quality, save_path):
        """Starts the download process via the DownloadController."""
        self.ui_manager.set_status_message("Preparing download...")
        self.ui_manager.set_progress_value(0)
        self.ui_manager.download_button.setEnabled(False)
        self.ui_manager.cancel_button.setEnabled(True)
        self.download_controller.download(url, quality, save_path)
        

    def cancel_download(self):
        """Starts the cancel download process via the DownloadController."""
        self.status_message_updated.emit("Download cancelled.") # emit status
        self.download_controller.cancel_download()

    def show_about_dialog(self):
        about_dialog = AboutDialog()
        about_dialog.exec()
        
    def handle_search_results_ready(self, results):
        self.ui_manager.display_results(results)
        self.ui_manager.set_status_message("Ready") # reset status to ready


if __name__ == "__main__":
    app = QApplication(sys.argv)

    settings_manager = SettingsManager()  # Create SettingsManager
    ui_manager = UIManager()  # Create the UI Manager
    search_controller = SearchController()  # Create SearchController
    download_controller = DownloadController() # Create DownloadController
    file_controller = FileController()

    controller = AppController(ui_manager, search_controller, download_controller, settings_manager, file_controller)
    # ui_manager.show() # Don't show yet
    controller.start()

    # Use a QMainWindow to wrap the UIManager
    main_window = QMainWindow()
    main_window.setCentralWidget(ui_manager)  # Set UIManager as central widget
    main_window.setWindowTitle("YouTube Video Downloader")
    main_window.setMinimumSize(800, 600)
    main_window.show()


    sys.exit(app.exec())