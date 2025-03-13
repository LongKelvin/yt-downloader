from datetime import timedelta
import os
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
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap
import qtawesome as qta  # For FontAwesome icons

import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
import sys
from requests_html import HTMLSession

from core.downloader import VideoDownloader
from core.youtube_api import YouTubeAPI


class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, url, quality, save_path):
        super().__init__()
        self.url = url
        self.quality = quality
        self.save_path = save_path
        self._is_canceled = False

    def cancel(self):
        self._is_canceled = True

    def run(self):
        try:
            downloader = VideoDownloader()
            def progress_callback(progress):
                if self._is_canceled:
                    raise Exception("Download canceled by user")
                self.progress_signal.emit(progress)

            downloader.download(
                self.url,
                self.quality,
                self.save_path,
                progress_callback=progress_callback,
            )
            if not self._is_canceled:
                self.finished_signal.emit("Download completed!")
            else:
                self.error_signal.emit("Download canceled by user")
        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")


class YouTubeSearchWorker(QThread):
    results_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, query, max_results=5, parallel_searches=5, batch_size=5):
        super().__init__()
        self.query = query
        self.max_results = max_results
        self.parallel_searches = parallel_searches
        self.batch_size = batch_size

    def run(self):
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
                "extract_flat": True,
                "default_search": "ytsearch",
            }
            search_query = f"ytsearch{self.max_results}:{self.query}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                with ThreadPoolExecutor(max_workers=self.parallel_searches) as executor:
                    queries = [
                        f"ytsearch{self.max_results}:{self.query} {i}"
                        for i in range(self.batch_size)
                    ]
                    future_to_query = {
                        executor.submit(self._search, ydl, query): query
                        for query in queries
                    }
                    results = []
                    for future in as_completed(future_to_query):
                        info = future.result()
                        if "entries" in info:
                            for entry in info["entries"]:
                                if not entry:
                                    continue
                                duration_seconds = entry.get("duration", 0)
                                results.append(
                                    {
                                        "id": entry.get("id", ""),
                                        "title": entry.get("title", "Unknown Title"),
                                        "url": entry.get(
                                            "webpage_url",
                                            f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                                        ),
                                        "thumbnail": entry.get("thumbnail", ""),
                                        "duration": str(
                                            timedelta(seconds=duration_seconds)
                                        ),
                                        "author": entry.get("uploader", "Unknown"),
                                    }
                                )
                    self.results_signal.emit(results)
        except Exception as e:
            self.error_signal.emit(f"Search error: {str(e)}")

    def _search(self, ydl, query):
        return ydl.extract_info(query, download=False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Video Downloader")
        self.setMinimumSize(800, 600)
        self.youtube_api = YouTubeAPI()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.setup_ui()
        self.apply_dark_theme()

    def setup_ui(self):
        # Search/URL section
        search_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL or search keywords...")
        self.search_button = QPushButton("Search")
        self.search_button.setIcon(qta.icon('fa5s.search', color='white'))
        self.search_button.clicked.connect(self.search_videos)
        search_layout.addWidget(self.url_input, 4)
        search_layout.addWidget(self.search_button, 1)
        self.layout.addLayout(search_layout)

        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        self.results_list.itemClicked.connect(self.select_video)
        self.layout.addWidget(QLabel("Search results:"))
        self.layout.addWidget(self.results_list)

        self.video_info = QLabel("No video selected yet")
        self.layout.addWidget(self.video_info)

        # Download options with improved spacing
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("Video quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["720p", "1080p", "1440p", "2160p"])
        options_layout.addWidget(self.quality_combo)
        self.audio_only = QCheckBox("Download audio only")
        options_layout.addWidget(self.audio_only)
        self.save_path = os.path.expanduser("~/Downloads")
        self.path_label = QLabel(f"Save to: {self.save_path}")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.select_save_path)
        options_layout.addWidget(self.path_label)
        options_layout.addWidget(self.browse_button)
        options_layout.addStretch()
        self.layout.addLayout(options_layout)

        # Button layout for Download and Cancel with icons
        button_layout = QHBoxLayout()
        self.download_button = QPushButton("Download")
        self.download_button.setIcon(qta.icon('fa5s.download', color='white'))
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setEnabled(False)
        button_layout.addWidget(self.download_button)

        self.cancel_button = QPushButton("Cancel Download")
        self.cancel_button.setIcon(qta.icon('fa5s.times', color='white'))
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        self.layout.addLayout(button_layout)

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.layout.addWidget(self.progress)

        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)

        theme_layout = QHBoxLayout()
        self.dark_mode = QCheckBox("Dark mode")
        self.dark_mode.setChecked(True)
        self.dark_mode.stateChanged.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.dark_mode)
        self.layout.addLayout(theme_layout)

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
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton#searchButton {
                background-color: #1E90FF;
            }
            QPushButton#downloadButton {
                background-color: #32CD32;
            }
            QPushButton#cancelButton {
                background-color: #FF4500;
            }
            QPushButton:hover {
                background-color: #1C86E0;
            }
            QPushButton#downloadButton:hover {
                background-color: #3CB371;
            }
            QPushButton#cancelButton:hover {
                background-color: #FF6347;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton#downloadButton:pressed {
                background-color: #228B22;
            }
            QPushButton#cancelButton:pressed {
                background-color: #DC143C;
            }
            QPushButton:disabled {
                background-color: #444444;
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
        self.search_button.setObjectName("searchButton")
        self.download_button.setObjectName("downloadButton")
        self.cancel_button.setObjectName("cancelButton")
        # Set icon colors for dark theme
        self.search_button.setIcon(qta.icon('fa5s.search', color='white'))
        self.download_button.setIcon(qta.icon('fa5s.download', color='white'))
        self.cancel_button.setIcon(qta.icon('fa5s.times', color='white'))

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
                background-color: #CCCCCC;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton#searchButton {
                background-color: #1E90FF;
                color: white;
            }
            QPushButton#downloadButton {
                background-color: #32CD32;
                color: white;
            }
            QPushButton#cancelButton {
                background-color: #FF4500;
                color: white;
            }
            QPushButton:hover {
                background-color: #1C86E0;
            }
            QPushButton#downloadButton:hover {
                background-color: #3CB371;
            }
            QPushButton#cancelButton:hover {
                background-color: #FF6347;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton#downloadButton:pressed {
                background-color: #228B22;
            }
            QPushButton#cancelButton:pressed {
                background-color: #DC143C;
            }
            QPushButton:disabled {
                background-color: #AAAAAA;
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
        self.search_button.setObjectName("searchButton")
        self.download_button.setObjectName("downloadButton")
        self.cancel_button.setObjectName("cancelButton")
        # Set icon colors for light theme
        self.search_button.setIcon(qta.icon('fa5s.search', color='black'))
        self.download_button.setIcon(qta.icon('fa5s.download', color='black'))
        self.cancel_button.setIcon(qta.icon('fa5s.times', color='black'))

    def toggle_theme(self, state):
        if state == Qt.CheckState.Checked:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def search_videos(self):
        query = self.url_input.text().strip()
        if not query:
            return
        self.results_list.clear()
        self.status_label.setText("Searching...")
        self.worker = YouTubeSearchWorker(query, max_results=5)
        self.worker.results_signal.connect(self.display_results)
        self.worker.error_signal.connect(self.display_error)
        self.worker.start()

    def display_results(self, results):
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
        self.status_label.setText(f"Error: {error_message}")

    def select_video(self, item):
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

    def start_download(self):
        if not hasattr(self, "selected_video"):
            QMessageBox.warning(
                self, "Warning", "Please select a video to download"
            )
            return

        quality = self.quality_combo.currentText()
        audio_only = self.audio_only.isChecked()

        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
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
        if hasattr(self, "download_thread") and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.status_label.setText("Canceling download...")
            self.cancel_button.setEnabled(False)

    def update_progress(self, value):
        self.progress.setValue(value)
        self.status_label.setText(f"Downloading: {value}%")

    def download_finished(self, message):
        self.status_label.setText(message)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.information(
            self, "Success", "Video downloaded successfully!"
        )

    def download_error(self, error_message):
        self.status_label.setText(error_message)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        if "canceled" not in error_message.lower():
            QMessageBox.critical(self, "Error", error_message)
        else:
            QMessageBox.information(self, "Canceled", "Download was canceled.")