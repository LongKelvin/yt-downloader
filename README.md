# YouTube Downloader

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/LongKelvin/yt-downloader)](https://github.com/LongKelvin/yt-downloader/releases)
[![GitHub issues](https://img.shields.io/github/issues/LongKelvin/yt-downloader)](https://github.com/LongKelvin/yt-downloader/issues)
[![GitHub license](https://img.shields.io/github/license/LongKelvin/yt-downloader)](https://github.com/LongKelvin/yt-downloader/blob/main/LICENSE)

A simple, user-friendly YouTube video downloader application built with Python, PyQt6, and yt-dlp.  This tool allows you to quickly search for YouTube videos and download them in various formats, including audio-only.

## Features

*   **Easy-to-Use Interface:**  A clean and intuitive graphical user interface (GUI) built with PyQt6.
*   **Search and Download:** Search for videos directly within the application or paste a YouTube URL.
*   **Multiple Quality Options:**  Choose from available video qualities (e.g., 720p, 1080p, 1440p, 2160p) or download audio only.
*   **Download Progress:**  A progress bar shows the download status.
*   **Download Cancellation:**  Cancel downloads in progress.
*   **Dark/Light Mode:** Switch between dark and light themes.
*   **Settings Persistence:**  Remembers your preferred save location and theme.
*   **Portable Executable:**  A standalone `.exe` version is available (no Python installation required for end-users).
*   **Open Source:** The code is open-source and available on GitHub.
*   **Search Caching:** Caches recent search results for faster access.
*   **Help and About Menus:** Includes built-in user guide and developer documentation, along with an "About" dialog.

## Installation (for End-Users)

**Easiest Method (Windows):**

1.  Go to the [Releases](https://github.com/LongKelvin/yt-downloader/releases) page.
2.  Download the latest `.exe` file (e.g., `YouTube-Downloader-v0.2.exe`).
3.  Double-click the `.exe` file to run the application. No installation is required!
4. Make sure put `yt_downloader_user_guide.pdf` in same folder of `.exe` file.

## Usage

1.  **Search:** Enter keywords or a YouTube URL in the search box and click "Search".
2.  **Select Video:** Click on a video from the search results.
3.  **Choose Quality:** Select the desired video quality (or "Download audio only").
4.  **Choose Save Location:** Click "Browse..." to select a folder to save the downloaded video.
5.  **Download:** Click "Download" to start the download.
6. **Cancel**: Click "Cancel" to cancel download process.

## Building from Source (for Developers)

**Prerequisites:**

*   Python 3.7+
*   Required packages (install via `pip`):

    ```bash
    pip install PyQt6 requests yt_dlp qtawesome
    ```

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/LongKelvin/yt-downloader.git
    cd yt-downloader
    ```

2.  **Run the Application:**
    ```bash
    python main.py
    ```

## Building a Portable Executable (.exe)

You can create a standalone `.exe` file using PyInstaller:

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```

2.  **Build:**
    ```bash
    pyinstaller --onefile --windowed --name "YouTube Downloader" main.py --collect-all qtawesome
    ```
    *   `--onefile`: Creates a single executable.
    *   `--windowed`:  Hides the console window.
    *   `--name`:  Sets the executable name.
    *   `--collect-all qtawesome`: Includes all necessary qtawesome files (for icons).

3.  **Find the Executable:** The `.exe` will be in the `dist` folder.
4. **Copy `yt_downloader_user_guide.pdf`:** Copy the `yt_downloader_user_guide.pdf` to the `dist` folder.

## Project Structure
The application is now organized into the following packages and modules:
```
yt_downloader/  
├── core/  
│ └── downloader.py (VideoDownloader - Handles video downloading via yt_dlp)  
├── ui/  
│ ├── **init**.py (Makes 'ui' a package)  
│ ├── about_window.py (AboutDialog - Displays application information)  
│ ├── download_thread.py (DownloadThread - Downloads videos in a separate thread)  
│ ├── main_window.py (Minimal - creates AppController and UIManager, starts event loop)  
│ ├── ui_manager.py (UIManager - Manages all UI elements and interactions)  
│ ├── search_controller.py (SearchController - Manages search logic and caching)  
│ ├── download_controller.py (DownloadController - Manages download logic)  
│ ├── settings_manager.py (SettingsManager - Manages application settings)  
│ └── file_controller.py (FileController - Manages file operations)  
├── helper/  
│ ├── **init**.py (Makes 'helper' a package)  
│ ├── search_worker.py (SearchWorker - Performs YouTube searches in a thread)  
│ └── file_opener_thread.py (FileOpenerThread - Opens files in a separate thread)  
├── docs/
│ ├── developer_documentation_v0.2.md  
│ ├── yt_downloader_dev_documentation_v0.2.pdf  
│ └── yt_downloader_user_guide.pdf
├── requirements.txt (Lists required Python packages
└── main.py (Bootstraps the application, connects components)  

```

## Contributing

Contributions are welcome!  Please feel free to:

*   Report bugs or suggest features by opening an issue.
*   Submit pull requests with bug fixes or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This application uses `yt_dlp` to download videos.  Please be aware of and respect YouTube's terms of service and copyright laws.  Use this tool responsibly.
