# --- START OF FILE main.py ---
import os
import json
import subprocess
import sys  # For opening the PDF

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QFileDialog,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QMessageBox,
    QMenu,
    QMenuBar,
    QApplication
)
from PyQt6.QtCore import Qt
import qtawesome as qta

from ui.about_window import AboutDialog
from ui.download_thread import DownloadThread
from ui.file_opener_thread import FileOpenerThread
from ui.youtube_search_worker import YouTubeSearchWorker




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Video Downloader")
        self.setMinimumSize(800, 600)
        self.selected_video = None  # Store selected video info
        self.download_thread = None  # Initialize download_thread


        # Load user settings
        self.settings_file = os.path.join(os.path.expanduser("~"), ".yt_downloader_settings.json")
        self.load_settings()

        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()

        # Dark mode default
        self.dark_mode.setChecked(self.settings.get("dark_mode", True))
        self.toggle_theme(self.dark_mode.isChecked())

        # Setup menu bar
        self.setup_menu_bar()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    "save_path": os.path.expanduser("~/Downloads"),
                    "dark_mode": True
                }
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
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


    def setup_menu_bar(self):
        menu_bar = QMenuBar(self)

        # Help Menu
        help_menu = QMenu("&Help", self)
        help_action_user = help_menu.addAction(qta.icon("fa5s.question-circle"), "&User Guide")
        help_action_user.triggered.connect(lambda: self.open_file("yt_downloader_user_guide.pdf"))

        help_action_dev = help_menu.addAction(qta.icon("fa5s.file-code"), "&Developer Guide")
        help_action_dev.triggered.connect(lambda: self.open_file("yt_downloader_dev_documentation_v0.2.pdf"))

        about_action = help_menu.addAction(qta.icon("fa5s.info-circle"), "&About")
        about_action.triggered.connect(self.show_about)

        menu_bar.addMenu(help_menu)
        self.setMenuBar(menu_bar)


    
    def open_file(self, filepath):
        """Opens a file from the parent directory using a separate thread."""

        try:
            base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
            print("base dir: ", base_dir)

            pdf_path = os.path.join(base_dir, "docs", filepath) # example of the file being in the docs folder.
            print("pdf path: ", pdf_path)

            if os.path.exists(pdf_path):
                self.thread = FileOpenerThread(pdf_path)
                self.thread.finished.connect(self.on_file_opened)
                self.thread.error.connect(self.on_file_open_error)
                self.thread.start()
            else:
                QMessageBox.critical(self, "Error", f"File not found: {filepath}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def on_file_opened(self, pdf_path):
        print(f"File opened successfully: {pdf_path}")

    def on_file_open_error(self, error_message):
        QMessageBox.critical(self, "Error", f"Could not open file: {error_message}")


    def show_about(self):
        about_dialog = AboutDialog()
        about_dialog.exec()


    def setup_ui(self):
        # Search/URL section
        search_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL or search keywords...")
        self.search_button = QPushButton(qta.icon("fa5s.search"), "Search")
        self.search_button.clicked.connect(self.search_videos)
        self.search_button.setToolTip("Search for videos")

        search_layout.addWidget(self.url_input, 4)
        search_layout.addWidget(self.search_button, 1)
        self.layout.addLayout(search_layout)

        # Search results list
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        self.results_list.itemClicked.connect(self.select_video)
        self.layout.addWidget(QLabel("Search results:"))
        self.layout.addWidget(self.results_list)

        # Total results label (added below the results list)
        self.total_results_label = QLabel("")
        self.layout.addWidget(self.total_results_label)

        # Selected video info
        self.video_info = QLabel("No video selected yet")
        self.layout.addWidget(self.video_info)

        # Download options
        options_layout = QHBoxLayout()

        # Video quality
        options_layout.addWidget(QLabel("Video quality:"))
        self.quality_combo = QComboBox()
        options_layout.addWidget(self.quality_combo)

        # Audio only option
        self.audio_only = QCheckBox("Download audio only")
        self.audio_only.stateChanged.connect(self.update_quality_options)
        options_layout.addWidget(self.audio_only)


        # Save location
        self.save_path = self.settings.get("save_path", os.path.expanduser("~/Downloads"))
        self.path_label = QLabel(f"Save to: {self.save_path}")
        self.browse_button = QPushButton(qta.icon("fa5s.folder-open"), "Browse...")
        self.browse_button.clicked.connect(self.select_save_path)
        self.browse_button.setToolTip("Select save location")

        options_layout.addWidget(self.path_label)
        options_layout.addWidget(self.browse_button)
        self.layout.addLayout(options_layout)

        # Download and Cancel buttons
        download_buttons_layout = QHBoxLayout()
        self.download_button = QPushButton(qta.icon("fa5s.download"), "Download")
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setEnabled(False)
        self.download_button.setToolTip("Start download")
        download_buttons_layout.addWidget(self.download_button)


        self.cancel_button = QPushButton(qta.icon("fa5s.times-circle"), "Cancel")
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)  # Initially disabled
        self.cancel_button.setToolTip("Cancel download")
        download_buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(download_buttons_layout)



        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.layout.addWidget(self.progress)

        # Download status
        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)

        # Dark/light mode
        theme_layout = QHBoxLayout()
        self.dark_mode = QCheckBox("Dark mode")
        self.dark_mode.stateChanged.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.dark_mode)
        self.layout.addLayout(theme_layout)

    def update_quality_options(self):
        """Enable/disable quality selection based on audio-only checkbox."""
        self.quality_combo.setEnabled(not self.audio_only.isChecked())


    def apply_dark_theme(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                font-size: 10pt;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #3D3D3D;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #0078D7;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1C86E0;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
            QProgressBar {
                text-align: center;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3D3D3D;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                border-radius: 3px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
            }
            QMenuBar {
                background-color: #3D3D3D; /* Dark background for menu bar */
                color: #FFFFFF; /* White text color for menu bar */
            }

            QMenu {
                background-color: #3D3D3D; /* Dark background for menu */
                color: #FFFFFF; /* White text color for menu */
                border: 1px solid #555555; /* Border for menu */
            }

            QMenu::item:selected {
                background-color: #0078D7; /* Highlight color for selected menu item */
            }
        """
        )

    def apply_light_theme(self):
        self.setStyleSheet(
            """
           QWidget {
                background-color: #F0F0F0;
                color: #333333;
                font-size: 10pt;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #0078D7;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0078D7;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1C86E0;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
            QProgressBar {
                text-align: center;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                border-radius: 3px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }

            QMenuBar {
                background-color: #F0F0F0; /* Light background for menu bar */
                color: #333333; /* Dark text color for menu bar */
            }

            QMenu {
                background-color: #F0F0F0; /* Light background for menu */
                color: #333333; /* Dark text color for menu */
                border: 1px solid #CCCCCC; /* Border for menu */
            }

            QMenu::item:selected {
                background-color: #0078D7; /* Highlight color for selected menu item */
            }
        """
        )

    def toggle_theme(self, state):
        if state:
            self.apply_dark_theme()
            self.settings["dark_mode"] = True
        else:
            self.apply_light_theme()
            self.settings["dark_mode"] = False
        self.save_settings()
        QApplication.instance().setStyleSheet("")
        QApplication.instance().setStyleSheet(self.styleSheet())
        self.central_widget.update()
        self.repaint()


    def search_videos(self):
        query = self.url_input.text().strip()
        if not query:
            return

        self.results_list.clear()
        self.status_label.setText("Searching...")
        self.total_results_label.setText("")  # Clear total results

        self.worker = YouTubeSearchWorker(query, max_results=5)
        self.worker.results_signal.connect(self.display_results)
        self.worker.error_signal.connect(self.display_error)
        self.worker.start()

    def display_results(self, results):
        self.status_label.setText("Search completed!")
        self.results_list.clear()

        if not results:
            self.status_label.setText("No videos found.")
            self.total_results_label.setText("Total results: 0")
            return

        for i, video in enumerate(results):
            item = QListWidgetItem(
                f"{i+1}. {video['title']} ({video['duration']})"
            )
            item.setData(Qt.ItemDataRole.UserRole, video)  # Store *all* video data
            item.setToolTip(f"URL: {video['url']}")
            self.results_list.addItem(item)

        self.total_results_label.setText(f"Total results: {len(results)}")


    def display_error(self, error_message):
        self.status_label.setText(f"Error: {error_message}")

    def select_video(self, item):
        video_info = item.data(Qt.ItemDataRole.UserRole)  # Get *all* stored data
        if not video_info:
            return

        self.video_info.setText(
            f"Selected: {video_info['title']} ({video_info['duration']})"
        )
        self.download_button.setEnabled(True)
        self.selected_video = video_info

        # Populate quality options from the *search result* data
        self.populate_quality_options(video_info)


    def populate_quality_options(self, video_info):
        """Populate quality options using data from the search result."""
        self.quality_combo.clear()

        formats = video_info.get('formats', [])
        available_formats = []
        for f in formats:
            if f.get('ext') == 'mp4' and 'height' in f:
                available_formats.append(f"{f['height']}p")

        # Handle cases where 'formats' might be missing or incomplete.
        if not available_formats:
            if self.audio_only.isChecked():
                available_formats = ["bestaudio"]
            else:
                available_formats = ["720p", "1080p", "1440p", "2160p"]

        self.quality_combo.addItems(
            sorted(list(set(available_formats)), key=lambda x: int(x[:-1]) if x.endswith('p') else 0, reverse=True)
        )
        self.quality_combo.setEnabled(not self.audio_only.isChecked())
        self.status_label.setText("Ready")



    def select_save_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select save folder", self.save_path
        )
        if path:
            self.save_path = path
            self.path_label.setText(f"Save to: {self.save_path}")
            self.settings["save_path"] = path
            self.save_settings()

    def start_download(self):
        if not self.selected_video:
            QMessageBox.warning(self, "Warning", "Please select a video")
            return

        quality = self.quality_combo.currentText()
        audio_only = self.audio_only.isChecked()

        if audio_only:
            quality = "bestaudio"  # Use bestaudio for audio-only downloads

        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True) # Enable Cancel button
        self.progress.setValue(0)
        self.status_label.setText("Preparing download...")


        self.download_thread = DownloadThread(
            self.selected_video["url"], quality, self.save_path
        )
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.download_error)
        self.download_thread.start()

    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()  # Terminate the thread
            self.download_thread.wait()      # Wait for it to finish
            self.status_label.setText("Download cancelled.")
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)  # Disable Cancel
            self.progress.setValue(0)
            QMessageBox.information(self, "Cancelled", "Download cancelled.")
        else:
            self.status_label.setText("No download to cancel.")


    def update_progress(self, value):
        self.progress.setValue(value)
        self.status_label.setText(f"Downloading: {value}%")

    def download_finished(self, message):
        self.status_label.setText(message)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False) # Disable Cancel Button
        QMessageBox.information(self, "Success", "Video downloaded!")

    def download_error(self, error_message):
        self.status_label.setText(error_message)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False) # Disable Cancel button
        QMessageBox.critical(self, "Error", error_message)