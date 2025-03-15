# ui/search_controller.py
from PyQt6.QtCore import QObject, pyqtSignal
from helper.search_worker import SearchWorker

class SearchController(QObject):
    search_results_ready = pyqtSignal(list)
    search_error = pyqtSignal(str)  # Keep this signal

    def __init__(self):
        super().__init__()
        self.worker = None
        self.search_cache = {}

    def search(self, query):
        if query in self.search_cache:
            self.search_results_ready.emit(self.search_cache[query])
            return

        self.worker = SearchWorker(query=query)
        self.worker.results_signal.connect(self.handle_results)
        self.worker.error_signal.connect(self.handle_error) # Connect to handle_error
        self.worker.start()

    def handle_results(self, results):
        self.search_cache[self.worker.query] = results
        self.search_results_ready.emit(results)

    def handle_error(self, error_message):
        # Emit the error signal (AppController is connected to this)
        self.search_error.emit(error_message)