import os
import json
from PyQt6.QtWidgets import (
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
    QApplication
)
from PyQt6.QtCore import Qt



from ui.download_thread import DownloadThread
from ui.youtube_search_worker import YouTubeSearchWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Video Downloader")
        self.setMinimumSize(800, 600)

        # Load user settings
        self.settings_file = os.path.join(os.path.expanduser("~"), ".yt_downloader_settings.json")
        self.load_settings()

        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Set up UI
        self.setup_ui()

        # Apply theme based on saved settings
        self.dark_mode.setChecked(self.settings.get("dark_mode", True))
        if self.settings.get("dark_mode", True):
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def load_settings(self):
        """Load user settings from file"""
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
        """Save user settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")

    def setup_ui(self):
        # Search/URL section
        search_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL or search keywords...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_videos)

        search_layout.addWidget(self.url_input, 4)
        search_layout.addWidget(self.search_button, 1)
        self.layout.addLayout(search_layout)

        # Search results list
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        self.results_list.itemClicked.connect(self.select_video)
        self.layout.addWidget(QLabel("Search results:"))
        self.layout.addWidget(self.results_list)

        # Selected video info
        self.video_info = QLabel("No video selected yet")
        self.layout.addWidget(self.video_info)

        # Download options
        options_layout = QHBoxLayout()

        # Video quality
        options_layout.addWidget(QLabel("Video quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["720p", "1080p", "1440p", "2160p"])
        options_layout.addWidget(self.quality_combo)

        # Audio only option
        self.audio_only = QCheckBox("Download audio only")
        options_layout.addWidget(self.audio_only)

        # Save location - use saved path from settings
        self.save_path = self.settings.get("save_path", os.path.expanduser("~/Downloads"))
        self.path_label = QLabel(f"Save to: {self.save_path}")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.select_save_path)

        options_layout.addWidget(self.path_label)
        options_layout.addWidget(self.browse_button)

        self.layout.addLayout(options_layout)

        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setEnabled(False)
        self.layout.addWidget(self.download_button)

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

    def apply_dark_theme(self):
        # Apply CSS for dark theme
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
        """
        )

    def apply_light_theme(self):
        # Apply CSS for light theme
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
        """
        )

    def toggle_theme(self, state):
        print(f"Toggle Theme Called. State: {state}")  # Debugging output
        
        if self.dark_mode.isChecked():  # Check actual checkbox state
            print("Applying Dark Theme")
            self.apply_dark_theme()
            self.settings["dark_mode"] = True
        else:
            print("Applying Light Theme")
            self.apply_light_theme()
            self.settings["dark_mode"] = False

        # Save theme preference
        self.save_settings()

        # 🛠️ Force UI refresh to apply new styles
        app = QApplication.instance()
        if app:
            app.setStyleSheet("")  # Reset styles
            app.setStyleSheet(self.styleSheet())  # Apply new styles

        self.central_widget.update()
        self.repaint()




    def search_videos(self):
        query = self.url_input.text().strip()
        if not query:
            return

        self.results_list.clear()
        self.status_label.setText("Searching...")

        # Create a worker thread for YouTube search
        self.worker = YouTubeSearchWorker(query, max_results=5)
        self.worker.results_signal.connect(self.display_results)
        self.worker.error_signal.connect(self.display_error)
        self.worker.start()  # Start the thread

    def display_results(self, results):
        """Displays the search results in the GUI."""
        self.status_label.setText("Search completed!")
        self.results_list.clear()

        if not results:
            self.status_label.setText("No videos found.")
            return

        for video in results:
            item = QListWidgetItem(f"{video['title']} ({video['duration']})")
            item.setData(Qt.ItemDataRole.UserRole, video)
            self.results_list.addItem(item)

    def display_error(self, error_message):
        """Displays an error message if the search fails."""
        self.status_label.setText(f"Error: {error_message}")

    def select_video(self, item):
        """Handles when a user selects a video from the search results."""
        video_info = item.data(Qt.ItemDataRole.UserRole)

        if not video_info:
            return

        self.video_info.setText(
            f"Selected: {video_info['title']} ({video_info['duration']})"
        )
        self.download_button.setEnabled(True)
        self.selected_video = video_info

    def select_save_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select save folder", self.save_path
        )
        if path:
            self.save_path = path
            self.path_label.setText(f"Save to: {self.save_path}")
            
            # Save the new path in settings
            self.settings["save_path"] = path
            self.save_settings()

    def start_download(self):
        if not hasattr(self, "selected_video"):
            QMessageBox.warning(
                self, "Warning", "Please select a video to download"
            )
            return

        quality = self.quality_combo.currentText()
        audio_only = self.audio_only.isChecked()

        self.download_button.setEnabled(False)
        self.progress.setValue(0)
        self.status_label.setText("Preparing download...")

        # Start download thread
        self.download_thread = DownloadThread(
            self.selected_video["url"], quality, self.save_path
        )
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.download_error)
        self.download_thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)
        self.status_label.setText(f"Downloading: {value}%")

    def download_finished(self, message):
        self.status_label.setText(message)
        self.download_button.setEnabled(True)
        QMessageBox.information(
            self, "Success", "Video downloaded successfully!"
        )

    def download_error(self, error_message):
        self.status_label.setText(error_message)
        self.download_button.setEnabled(True)
        QMessageBox.critical(self, "Error", error_message)

