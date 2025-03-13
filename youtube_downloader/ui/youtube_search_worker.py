from datetime import timedelta
from PyQt6.QtCore import QThread, pyqtSignal

import yt_dlp

from concurrent.futures import ThreadPoolExecutor, as_completed

class YouTubeSearchWorker(QThread):
    results_signal = pyqtSignal(list)  # Signal to return results
    error_signal = pyqtSignal(str)  # Signal for errors

    def __init__(self, query, max_results=5, parallel_searches=5, batch_size=5):
        super().__init__()
        self.query = query
        self.max_results = max_results
        self.parallel_searches = parallel_searches  # Number of parallel search requests
        self.batch_size = batch_size  # Number of queries per batch to optimize

    def run(self):
        """Runs in a separate thread to avoid blocking the GUI."""
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,  # Don't download anything
                "noplaylist": True,  # Ignore playlists
                "extract_flat": True,  # Extract metadata only (faster)
                "default_search": "ytsearch",  # Use optimized search method
            }

            search_query = f"ytsearch{self.max_results}:{self.query}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                with ThreadPoolExecutor(max_workers=self.parallel_searches) as executor:
                    # Create batches of search queries
                    queries = [
                        f"ytsearch{self.max_results}:{self.query} {i}"
                        for i in range(self.batch_size)
                    ]

                    future_to_query = {
                        executor.submit(self._search, ydl, query): query
                        for query in queries
                    }
                    results = []

                    # Process search results as they complete
                    for future in as_completed(future_to_query):
                        info = future.result()
                        if "entries" in info:
                            for entry in info["entries"]:
                                if not entry:
                                    continue

                                duration_seconds = entry.get("duration", 0)
                                results.append(
                                    {
                                        "id": entry.get("id", ""),
                                        "title": entry.get("title", "Unknown Title"),
                                        "url": entry.get(
                                            "webpage_url",
                                            f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                                        ),
                                        "thumbnail": entry.get("thumbnail", ""),
                                        "duration": str(
                                            timedelta(seconds=duration_seconds)
                                        ),
                                        "author": entry.get("uploader", "Unknown"),
                                    }
                                )

                    self.results_signal.emit(results)  # Send results to main thread

        except Exception as e:
            self.error_signal.emit(
                f"Search error: {str(e)}"
            )  # Send error to main thread

    def _search(self, ydl, query):
        """Performs the search request."""
        return ydl.extract_info(query, download=False)
