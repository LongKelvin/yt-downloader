from PyQt6.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QTextBrowser 
)
from PyQt6.QtCore import QSize

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        layout = QVBoxLayout()
        text = QTextBrowser() 
        text.setReadOnly(True)
        text.setOpenExternalLinks(True) 
        text.setHtml("""
            <h3>YouTube Downloader</h3>
            <p><b>Author:</b> Long Kelvin</p>
            <p><b>GitHub:</b> <a href="https://github.com/LongKelvin/yt-downloader">https://github.com/LongKelvin/yt-downloader</a></p>
            <p><b>Year:</b> 2025</p>
            <p><b>Version:</b> 0.2</p>
            <p><b>Description:</b> A simple YouTube video downloader application.<br>
            Developed using Python, PyQt6, and yt-dlp. It's open-source and free to use.<br><br>
            For feedback or issues, please create an issue here: <a href="https://github.com/LongKelvin/yt-downloader/issues">https://github.com/LongKelvin/yt-downloader/issues</a>
            </p>
        """)
        layout.addWidget(text)
        self.setLayout(layout)
        self.resize(650, 280)