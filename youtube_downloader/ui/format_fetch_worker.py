from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp
from concurrent.futures import ThreadPoolExecutor

class FormatFetchWorker(QThread):
    formats_signal = pyqtSignal(dict)  # Emit a dictionary of results
    error_signal = pyqtSignal(str, str) # url, error_message

    def __init__(self, urls):
        super().__init__()
        self.urls = urls
        self.executor = ThreadPoolExecutor(max_workers=3)  # Limit parallelism


    def run(self):
        results = {}
        try:
            for url in self.urls:
                future = self.executor.submit(self._fetch_formats, url)
                results[url] = future # associate the future with its URL

            for url, future in results.items():
                try:
                    formats = future.result() # wait and retrieve the result
                    self.formats_signal.emit({url:formats})
                except Exception as e:
                    self.error_signal.emit(url, f"Error fetching formats: {str(e)}")

        except Exception as e:
            # This should ideally never happen, but handle for robustness
            self.error_signal.emit("",f"Unexpected error in FormatFetchWorker: {str(e)}")
        finally:
             self.executor.shutdown()


    def _fetch_formats(self, url):
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "simulate": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            available_formats = [
                f"{f['height']}p"
                for f in formats
                if f.get('ext') == 'mp4' and 'height' in f
            ]
            return available_formats