# ui/download_controller.py
from PyQt6.QtCore import QObject, pyqtSignal
from ui.download_thread import DownloadThread

class DownloadController(QObject):
    download_progress = pyqtSignal(int)
    download_finished = pyqtSignal(str)
    download_error = pyqtSignal(str) # Keep this signal

    def __init__(self):
        super().__init__()
        self.download_thread = None

    def download(self, url, quality, save_path):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()

        self.download_thread = DownloadThread(url, quality, save_path)
        self.download_thread.progress_signal.connect(self.download_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.handle_error) # Connect to handle_error
        self.download_thread.start()


    def handle_error(self, error_message):
        # Emit the error signal (AppController is connected to this)
        self.download_error.emit(error_message)

    def cancel_download(self):
         if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()