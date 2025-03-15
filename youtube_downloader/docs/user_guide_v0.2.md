
# YouTube Downloader - User Guide

This guide explains how to use the YouTube Downloader application.  This application is a standalone executable (`.exe`) file, so you don't need to install Python or any other software.

### 1. Running the Application

1.  **Download:** Download the YouTube Downloader `.exe` file.
2.  **Run:** Double-click the `.exe` file to launch the application.  No installation is required.

### 2. Using the Application

#### 2.1. Searching for Videos

1.  **Enter Search Term:** In the text box at the top, enter either a YouTube video URL or search keywords (e.g., "travel vlog").
2.  **Click "Search":** Click the "Search" button (or press Enter).
3.  **View Results:** The search results will appear below, showing:
    *   Row Number
    *   Video Title
    *   Video Duration
    *   A basic indication of HD availability (if available)
    *   Hover over a result to see the full YouTube URL.

#### 2.2. Selecting a Video

1.  **Click:** Click on any video in the search results list.
2.  **Video Info:** The title and duration will appear below the results.
3.  **Quality Options:** The "Video quality" dropdown will be populated with available options.

#### 2.3. Downloading a Video

1.  **Quality:** Select your desired video quality from the dropdown.
2.  **Audio Only (Optional):** Check "Download audio only" for just the audio (m4a format). This disables the quality selection.
3.  **Save Location:**
    *   Default: Your "Downloads" folder.
    *   Change: Click "Browse..." and choose a folder.
4.  **Download:** Click the "Download" button.
5.  **Progress Bar:** Shows the download progress.
6.  **Status Label:** Displays messages like "Preparing download...", "Downloading...", "Download completed!", or errors.

#### 2.4. Cancelling a Download

1.  **Click "Cancel":** During download, click "Cancel" to stop.
2.  **Confirmation:** A message confirms cancellation. Incomplete files are removed.

#### 2.5. Dark/Light Mode

1.  **Toggle:** Check/uncheck "Dark mode" in the lower-right to switch themes. Your preference is saved.

#### 2.6. Help Menu

1.  **User Guide:** Click "Help" -> "User Guide" to open a PDF (user\_guide.pdf) with instructions. *The PDF must be in the same folder as the `.exe` file.*
2.  **About:** Click "Help" -> "About" for application information (author, GitHub link, etc.).

### 3. Settings

Settings (save path, dark mode) are saved in `.yt_downloader_settings.json` in your home directory. Edit this file manually if needed (use correct JSON syntax).

### 4. Troubleshooting

*   **"Help file (user_guide.pdf) not found.":** The `user_guide.pdf` must be in the *same folder* as the `.exe` file.
*   **Download Errors:**  These can be caused by network problems, video unavailability, or issues with the underlying download library. Check the status label. Try again later or try a different video.
*   **Application Freezes:** If the application freezes completely, you may need to force-quit it. If the problem persists, it might be a bug.  If you obtained the `.exe` from a trusted source, consider reporting the issue to the developer.

**Important Note:** This application uses a third-party library (`yt_dlp`) to download videos.  YouTube's terms of service may restrict downloading content.  Use this application responsibly and respect copyright laws.

## Author and Project Information

* **Author:** **Long Kelvin**
* **Project Name:** yt-downloader
* **GitHub Repository:** [https://github.com/LongKelvin/yt-downloader](https://github.com/LongKelvin/yt-downloader)
* **Release Date:** March 2025
* **Version:** 0.2 
* **Contact:** longkelvin101099@gmail.com