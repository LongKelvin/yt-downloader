## Developer Documentation (v0.2)

This section provides information for developers who want to understand, modify, or contribute to the YouTube Downloader application.

### 1. Project Structure

The application consists of the following files:

*   **`main.py`:**  The main entry point of the application.  Creates the `MainWindow` and starts the Qt event loop.
*   **`ui/main_window.py`:**  Defines the `MainWindow` class, which handles the user interface and application logic.
*   **`ui/download_thread.py`:**  Defines the `DownloadThread` class, responsible for downloading videos in a separate thread.
*   **`ui/youtube_search_worker.py`:** Defines the `YouTubeSearchWorker` class, which performs YouTube searches in a separate thread.
*   **`core/downloader.py`:** Defines the `VideoDownloader` class, which uses `yt_dlp` to download videos.
*   **`requirements.txt`:**  Lists the required Python packages.

### 2. Dependencies

*   **PyQt6:**  The GUI framework.
*   **requests:** (Not explicitly used in the final code, but often useful for web-related tasks).
*   **yt_dlp:**  The core library for downloading videos from YouTube and other sites.
*   **qtawesome:**  Provides Font Awesome icons for the UI.

### 3. Code Overview

#### 3.1. `main.py`

*   Creates the `QApplication` instance.
*   Initializes and shows the `MainWindow`.
*   Starts the Qt event loop.

#### 3.2. `ui/main_window.py`

*   **`MainWindow` Class:**
    *   `__init__`: Sets up the UI (creates widgets, layouts, connects signals).  Loads user settings.
    *   `load_settings`, `save_settings`:  Manages user preferences (save path, dark mode).
    *   `setup_ui`:  Creates all the UI elements.
    *   `setup_menu_bar`: Sets up the Help and About menus.
    *   `open_help`, `show_about`:  Handles actions from the menu bar.
    *   `apply_dark_theme`, `apply_light_theme`, `toggle_theme`:  Manages the application's theme.
    *   `search_videos`:  Starts the YouTube search process (creates a `YouTubeSearchWorker`).
    *   `display_results`:  Displays the search results in the `QListWidget`.
    *   `display_error`:  Displays search errors.
    *   `select_video`:  Handles video selection from the list.  Populates the quality options.
    *   `populate_quality_options`: Populates the quality `QComboBox`.
    *   `select_save_path`:  Opens a file dialog to choose the download location.
    *   `start_download`:  Starts the download process (creates a `DownloadThread`).
    *   `cancel_download`:  Cancels the download.
    *   `update_progress`:  Updates the progress bar.
    *   `download_finished`, `download_error`:  Handles download completion or errors.
    *   `search_cache`: Caches the search result to avoid re-search with same query.

#### 3.3. `ui/youtube_search_worker.py`

*   **`YouTubeSearchWorker` Class:**
    *   `__init__`:  Takes the search query and maximum results as input.
    *   `run`:  Performs the YouTube search using `yt_dlp`.  Emits the `results_signal` with the search results or the `error_signal` if an error occurs.
    *   Uses a `ThreadPoolExecutor` for bounded parallelism to improve search speed.

#### 3.4. `ui/download_thread.py`

*   **`DownloadThread` Class:**
    *   `__init__`: Takes the video URL, quality, and save path as input.
    *   `run`:  Downloads the video using the `VideoDownloader` class.  Emits `progress_signal` updates, `finished_signal` on completion, or `error_signal` on failure.

#### 3.5. `core/downloader.py`

*   **`VideoDownloader` Class:**
    *   `download`:  Downloads the video using `yt_dlp` with the specified options (quality, output path, etc.).
    *   `_progress_hook`:  A helper function to handle progress updates from `yt_dlp`.

### 4. Key Concepts

*   **Threading:**  `YouTubeSearchWorker` and `DownloadThread` use separate threads to prevent the UI from freezing during long-running operations (searching and downloading).
*   **Signals and Slots:** PyQt's signal and slot mechanism is used for communication between threads and the main UI thread.  For example, the `results_signal` from `YouTubeSearchWorker` is connected to the `display_results` slot in `MainWindow`.
*   **`yt_dlp` Options:**  The code uses various `yt_dlp` options to control the download process:
    *   `quiet`, `no_warnings`:  Suppress unnecessary output.
    *   `skip_download`:  Used during the search to get video information without downloading.
    *   `noplaylist`:  Ignores playlists.
    *   `default_search`:  Specifies the search method.
    *   `format`:  Selects the desired video and audio formats.
    *   `merge_output_format`:  Ensures the output is in MP4 format.
    *   `outtmpl`:  Specifies the output file name template.
    *   `progress_hooks`:  Allows for monitoring the download progress.
*   **Caching:** The `search_cache` in `MainWindow` caches search results to improve performance for repeated searches.
* **Settings:** Settings file located in user home directory.



### 5. GitHub Repository

The source code for this project is available on GitHub: [https://github.com/LongKelvin/yt-downloader](https://github.com/LongKelvin/yt-downloader)

A pre-built, portable `.exe` version of the application can be found on the releases page: [https://github.com/LongKelvin/yt-downloader/releases/tag/v0.1](https://github.com/LongKelvin/yt-downloader/releases/tag/v0.1)

### 6. Building a Portable Executable (.exe)

If you modify the code and want to create a new `.exe` file, you can use PyInstaller.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```

2.  **Build the Executable:**  Open a terminal in the project directory (where `main.py` is located) and run:
    ```bash
    pyinstaller --onefile --windowed --name "YouTube Downloader" main.py --collect-all qtawesome
    ```

    *   `--onefile`: Creates a single executable file.
    *   `--windowed`:  Prevents a console window from appearing when the `.exe` is run.
    *   `--name "YouTube Downloader"`: Sets the name of the executable file.
    *   `main.py`:  Specifies the main Python script.
    *    `--collect-all qtawesome`: Collects all qtawesome files, this is a crucial step.

3.  **Find the Executable:** After the build process completes, the `.exe` file will be located in the `dist` folder (which PyInstaller creates).

4. **Copy `user_guide.pdf`:** Copy the `user_guide.pdf` to the `dist` folder so it's in same directory with the executable file.

This command creates a single, self-contained executable that includes all the necessary dependencies.  Users can run this `.exe` without needing to install Python or any libraries.

## Author and Project Information

* **Author:** Long Kelvin
* **Project Name:** yt-downloader
* **GitHub Repository:** [https://github.com/LongKelvin/yt-downloader](https://github.com/LongKelvin/yt-downloader)
* **Release Date:** March 2025
* **Version:** 0.2
* **Contact:** longkelvin101099@gmail.com