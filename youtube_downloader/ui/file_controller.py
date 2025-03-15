# ui/file_controller.py

from PyQt6.QtCore import QObject, pyqtSignal
from helper.file_opener_thread import FileOpenerThread
import os
import sys

class FileController(QObject):
    file_opened = pyqtSignal(str)  # Signal for successful file open
    file_open_error = pyqtSignal(str)  # Signal for file open errors

    def __init__(self):
        super().__init__()
        self.thread = None # Best practice


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
                self.file_open_error.emit(f"File not found: {filepath}")
                # QMessageBox.critical(self, "Error", f"File not found: {filepath}") # No UI here

        except Exception as e:
            self.file_open_error.emit(f"Could not open file: {str(e)}")
            # QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}") # No UI

    def on_file_opened(self, pdf_path):
        print(f"File opened successfully: {pdf_path}")
        self.file_opened.emit(pdf_path)


    def on_file_open_error(self, error_message):
        print(f"Error opening file: {error_message}")
        self.file_open_error.emit(error_message)