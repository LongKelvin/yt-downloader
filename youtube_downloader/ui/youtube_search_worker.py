from datetime import timedelta
from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp

class YouTubeSearchWorker(QThread):
    results_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, query, max_results=5, parallel_searches=5, batch_size=5):
        super().__init__()
        self.query = query
        self.max_results = max_results
        # No longer needed:
        # self.parallel_searches = parallel_searches
        # self.batch_size = batch_size

    def run(self):
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
                # Removed "extract_flat": True,  Get full info (including formats)
                "default_search": "ytsearch",
            }

            search_query = f"ytsearch{self.max_results}:{self.query}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # No ThreadPoolExecutor needed here
                info = ydl.extract_info(search_query, download=False)
                results = []

                if "entries" in info:
                    for entry in info["entries"]:
                        if not entry:
                            continue

                        duration_seconds = entry.get("duration", 0)
                        # Important: Include 'formats' in the result
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
                                "formats": entry.get("formats", []),  # Include formats
                            }
                        )

                self.results_signal.emit(results)

        except Exception as e:
            self.error_signal.emit(f"Search error: {str(e)}")