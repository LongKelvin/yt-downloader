import os
import yt_dlp

class VideoDownloader:
    def __init__(self):
        pass
    
    def download(self, url, quality, save_path, progress_callback=None):
        """
        Download a YouTube video with the specified quality.
        
        Args:
            url (str): YouTube video URL
            quality (str): Video quality (720p, 1080p, etc.)
            save_path (str): Path to save the video
            progress_callback (function): Callback function for progress updates
        
        Returns:
            str: Path to the downloaded file
        """
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': f'bestvideo[height<={quality}]+bestaudio/best',  # Get the best video with the given quality
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),  # Save as title of the video
                'progress_hooks': [self._progress_hook(progress_callback)] if progress_callback else [],
            }

            # Ensure save path exists
            os.makedirs(save_path, exist_ok=True)

            # Download the video using yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])

            # Check if download was successful (result is an integer; 0 means success)
            if result == 0:
                return os.path.join(save_path, f'{ydl.prepare_filename(ydl.extract_info(url))}')
            else:
                raise Exception(f"Error downloading video: Download failed with status code {result}")

        except Exception as e:
            print(f"Error downloading video: {e}")
            return None

    def _progress_hook(self, progress_callback):
        """
        Creates a progress hook for yt-dlp's download process.
        Args:
            progress_callback (function): Callback function to update progress.
        """
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                progress_callback(percent)
        
        return progress_hook
