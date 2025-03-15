import yt_dlp
import os

class VideoDownloader:
    def __init__(self):
        pass

    def download(self, url, quality, save_path, progress_callback=None):
        """
        Downloads a YouTube video.  Handles audio-only and video downloads.

        Args:
            url (str): YouTube video URL.
            quality (str):  "bestaudio" or video quality (e.g., "720p").
            save_path (str): Path to save.
            progress_callback (func): Callback for progress.
        """
        try:
            if quality == "bestaudio":
                ydl_opts = {
                    'format': 'bestaudio/best',  # Download best audio
                    'ext': 'm4a',              # Ensure m4a for audio
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self._progress_hook(progress_callback)] if progress_callback else [],
                    'quiet': False,
                    'noprogress': False,
                }
            else:
                quality_value = int(quality.replace('p', ''))
                ydl_opts = {
                    'format': f'bestvideo[ext=mp4][height<={quality_value}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self._progress_hook(progress_callback)] if progress_callback else [],
                    'quiet': False,
                    'noprogress': False,
                }

            os.makedirs(save_path, exist_ok=True)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            print(f"Error downloading: {e}")
            raise  # Re-raise for thread handling


    def _progress_hook(self, progress_callback):
        def progress_hook(d):
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes'] > 0:
                    percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                    progress_callback(percent)
                elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                    percent = int(d['downloaded_bytes'] * 100 / d['total_bytes_estimate'])
                    progress_callback(percent)
                else:
                    mb_downloaded = d['downloaded_bytes'] / (1024 * 1024)
                    simulated_percent = min(int(mb_downloaded) % 100, 99)
                    if simulated_percent > 0:
                        progress_callback(simulated_percent)

            elif d['status'] == 'finished':
                progress_callback(100)
        return progress_hook