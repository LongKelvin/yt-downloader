# helper/search_worker.py
from datetime import timedelta
from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp
from concurrent.futures import ThreadPoolExecutor

class SearchWorker(QThread):  # Renamed
    results_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, query, max_results=5):
        super().__init__()
        self.query = query
        self.max_results = max_results
        self.executor = ThreadPoolExecutor(max_workers=3)  # Bounded parallelism

    def run(self):
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
                'extract_flat': 'in_playlist', # Optimize yt-dlp options
                "default_search": "ytsearch",
            }

            search_query = f"ytsearch{self.max_results}:{self.query}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                future = self.executor.submit(ydl.extract_info, search_query, download=False)
                info = future.result() # wait to finish
                results = []

                if "entries" in info:
                    for entry in info["entries"]:
                        if not entry:
                            continue
                        # Handle cases where duration might be None
                        duration_seconds = entry.get("duration") or 0
                        results.append(
                            {
                                "id": entry.get("id", ""),
                                "title": entry.get("title", "Unknown Title"),
                                "url": entry.get(
                                    "webpage_url",
                                    f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                                ),
                                "thumbnail": entry.get("thumbnail", ""),
                                "duration": str(timedelta(seconds=duration_seconds)),
                                "author": entry.get("uploader", "Unknown"),
                                "formats": entry.get("formats", []),
                            }
                        )

                self.results_signal.emit(results)

        except Exception as e:
            self.error_signal.emit(f"Search error: {str(e)}")
        finally:
            self.executor.shutdown()