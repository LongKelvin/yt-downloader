from PyQt6.QtCore import QThread, pyqtSignal
from core.downloader import VideoDownloader

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
                progress_callback=self.progress_signal.emit,
            )
            self.finished_signal.emit("Download completed!")
        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")
