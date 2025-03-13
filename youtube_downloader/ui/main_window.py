from datetime import timedelta
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QPushButton, QLabel, QComboBox, 
                            QFileDialog, QProgressBar, QListWidget, QListWidgetItem,
                            QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap
import sys

import yt_dlp

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
        
    def run(self):
        try:
            downloader = VideoDownloader()
            downloader.download(
                self.url, 
                self.quality,
                self.save_path,
                progress_callback=self.progress_signal.emit
            )
            self.finished_signal.emit("Tải xuống hoàn tất!")
        except Exception as e:
            self.error_signal.emit(f"Lỗi: {str(e)}")

class YouTubeSearchWorker(QThread):
    results_signal = pyqtSignal(list)  # Signal to return results
    error_signal = pyqtSignal(str)  # Signal for errors

    def __init__(self, query, max_results=10):
        super().__init__()
        self.query = query
        self.max_results = max_results

    def run(self):
        """Runs in a separate thread to avoid blocking the GUI."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{self.max_results}:{self.query}"
                info = ydl.extract_info(search_query, download=False)
                
                results = []
                if 'entries' in info:
                    for entry in info['entries']:
                        if not entry:
                            continue
                        
                        duration_seconds = entry.get('duration', 0)
                        
                        results.append({
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Unknown Title'),
                            'url': entry.get('webpage_url', f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
                            'thumbnail': entry.get('thumbnail', ''),
                            'duration': str(timedelta(seconds=duration_seconds)),
                            'author': entry.get('uploader', 'Unknown')
                        })
                
                self.results_signal.emit(results)  # Send results to main thread
        except Exception as e:
            self.error_signal.emit(f"Search error: {str(e)}")  # Send error to main thread
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Trình Tải Video YouTube")
        self.setMinimumSize(800, 600)
        
        # Khởi tạo YouTube API
        self.youtube_api = YouTubeAPI()
        
        # Tạo main widget và layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Tạo giao diện
        self.setup_ui()
        
        # Áp dụng dark theme
        self.apply_dark_theme()
        
    def setup_ui(self):
        # Phần tìm kiếm/URL
        search_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Nhập URL YouTube hoặc từ khóa tìm kiếm...")
        self.search_button = QPushButton("Tìm kiếm")
        self.search_button.clicked.connect(self.search_videos)
        
        search_layout.addWidget(self.url_input, 4)
        search_layout.addWidget(self.search_button, 1)
        self.layout.addLayout(search_layout)
        
        # Danh sách kết quả tìm kiếm
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        self.results_list.itemClicked.connect(self.select_video)
        self.layout.addWidget(QLabel("Kết quả tìm kiếm:"))
        self.layout.addWidget(self.results_list)
        
        # Thông tin video đã chọn
        self.video_info = QLabel("Chưa có video nào được chọn")
        self.layout.addWidget(self.video_info)
        
        # Tùy chọn tải xuống
        options_layout = QHBoxLayout()
        
        # Chất lượng video
        options_layout.addWidget(QLabel("Chất lượng video:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["720p", "1080p", "1440p", "2160p"])
        options_layout.addWidget(self.quality_combo)
        
        # Chỉ tải âm thanh
        self.audio_only = QCheckBox("Chỉ tải âm thanh")
        options_layout.addWidget(self.audio_only)
        
        # Vị trí lưu
        self.save_path = os.path.expanduser("~/Downloads")
        self.path_label = QLabel(f"Lưu tại: {self.save_path}")
        self.browse_button = QPushButton("Duyệt...")
        self.browse_button.clicked.connect(self.select_save_path)
        
        options_layout.addWidget(self.path_label)
        options_layout.addWidget(self.browse_button)
        
        self.layout.addLayout(options_layout)
        
        # Nút tải xuống
        self.download_button = QPushButton("Tải xuống")
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setEnabled(False)
        self.layout.addWidget(self.download_button)
        
        # Thanh tiến trình
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.layout.addWidget(self.progress)
        
        # Trạng thái tải xuống
        self.status_label = QLabel("Sẵn sàng")
        self.layout.addWidget(self.status_label)
        
        # Chế độ tối/sáng
        theme_layout = QHBoxLayout()
        self.dark_mode = QCheckBox("Chế độ tối")
        self.dark_mode.setChecked(True)
        self.dark_mode.stateChanged.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.dark_mode)
        self.layout.addLayout(theme_layout)
    
    def apply_dark_theme(self):
        # Áp dụng CSS cho dark theme
        self.setStyleSheet("""
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
        """)
    
    def apply_light_theme(self):
        # Áp dụng CSS cho light theme
        self.setStyleSheet("""
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
        """)
    
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
        self.status_label.setText("Đang tìm kiếm...")

        # Create a worker thread for YouTube search
        self.worker = YouTubeSearchWorker(query, max_results=5)
        self.worker.results_signal.connect(self.display_results)
        self.worker.error_signal.connect(self.display_error)
        self.worker.start()  # Start the thread

    
    def display_results(self, results):
        """Displays the search results in the GUI."""
        self.status_label.setText("Tìm kiếm hoàn tất!")
        self.results_list.clear()

        if not results:
            self.status_label.setText("Không tìm thấy video nào.")
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

        self.video_info.setText(f"Đã chọn: {video_info['title']} ({video_info['duration']})")
        self.download_button.setEnabled(True)
        self.selected_video = video_info

    
    def select_save_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Chọn thư mục lưu", self.save_path
        )
        if path:
            self.save_path = path
            self.path_label.setText(f"Lưu tại: {self.save_path}")
    
    def start_download(self):
        if not hasattr(self, 'selected_video'):
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một video để tải xuống")
            return
            
        quality = self.quality_combo.currentText()
        audio_only = self.audio_only.isChecked()
        
        self.download_button.setEnabled(False)
        self.progress.setValue(0)
        self.status_label.setText("Đang chuẩn bị tải xuống...")
        
        # Bắt đầu thread tải xuống
        self.download_thread = DownloadThread(
            self.selected_video['url'], 
            quality, 
            self.save_path
        )
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.download_error)
        self.download_thread.start()
    
    def update_progress(self, value):
        self.progress.setValue(value)
        self.status_label.setText(f"Đang tải xuống: {value}%")
    
    def download_finished(self, message):
        self.status_label.setText(message)
        self.download_button.setEnabled(True)
        QMessageBox.information(self, "Thành công", "Video đã được tải xuống thành công!")
    
    def download_error(self, error_message):
        self.status_label.setText(error_message)
        self.download_button.setEnabled(True)
        QMessageBox.critical(self, "Lỗi", error_message)