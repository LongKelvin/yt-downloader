import yt_dlp
import os

class VideoDownloader:
    def __init__(self):
        pass

    def download(self, url, quality, save_path, progress_callback=None):
        """
        Download a YouTube video with the specified quality and enforce MP4 format.
        
        Args:
            url (str): YouTube video URL
            quality (str): Video quality (720p, 1080p, etc.)
            save_path (str): Path to save the video
            progress_callback (function): Callback function for progress updates
        
        Returns:
            str: Path to the downloaded file
        """
        try:
            # yt-dlp format selection for MP4
            ydl_opts = {
                'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4]',
                'merge_output_format': 'mp4',  # Ensure final file is MP4
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook(progress_callback)] if progress_callback else [],
            }

            # Ensure save path exists
            os.makedirs(save_path, exist_ok=True)

            # Download video using yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            print(f"Error downloading video: {e}")
            return None

    def _progress_hook(self, progress_callback):
        """Handles progress updates for the download."""
        def progress_hook(d):
            if d['status'] == 'downloading' and 'total_bytes' in d:
                percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                progress_callback(percent)

        return progress_hook
