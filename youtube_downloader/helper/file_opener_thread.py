import os
import sys
import subprocess
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal

class FileOpenerThread(QThread):
    finished = pyqtSignal(str)  # Signal to indicate completion
    error = pyqtSignal(str)     # Signal for errors

    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        try:
            if sys.platform == 'win32':
                os.startfile(self.pdf_path)  # Windows
            elif sys.platform == 'darwin':
                subprocess.call(('open', self.pdf_path))  # macOS
            else:  # Assume Linux/Unix
                subprocess.call(('xdg-open', self.pdf_path))  # Linux/Unix
            self.finished.emit(self.pdf_path)
        except Exception as e:
            self.error.emit(str(e))
