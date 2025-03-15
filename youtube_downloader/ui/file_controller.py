from PyQt6.QtCore import QObject, pyqtSignal
from helper.file_opener_thread import FileOpenerThread
import os

class FileController(QObject):
    file_opened = pyqtSignal(str)  # Signal for successful file open
    file_open_error = pyqtSignal(str)  # Signal for file open errors

    def __init__(self):
        super().__init__()
        self.thread = None

    def open_file(self, file_path):
        """Opens a file using a separate thread. Caller must provide full path."""
        if os.path.exists(file_path):
            self.thread = FileOpenerThread(file_path)
            self.thread.finished.connect(lambda: self.file_opened.emit(file_path))
            self.thread.error.connect(self.file_open_error.emit)
            self.thread.start()
        else:
            self.file_open_error.emit(f"File not found: {file_path}")
            
