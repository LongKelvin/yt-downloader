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
            # Convert quality string to integer (remove 'p')
            quality_value = int(quality.replace('p', ''))
            
            # yt-dlp format selection for MP4
            ydl_opts = {
                'format': f'bestvideo[ext=mp4][height<={quality_value}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',  # Ensure final file is MP4
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook(progress_callback)] if progress_callback else [],
                'quiet': False,  # Allow output to console for debugging
                'noprogress': False,  # Show progress
            }

            # Ensure save path exists
            os.makedirs(save_path, exist_ok=True)

            # Download video using yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            print(f"Error downloading video: {e}")
            raise e  # Re-raise to allow the thread to catch it

    def _progress_hook(self, progress_callback):
        """Handles progress updates for the download."""
        def progress_hook(d):
            if d['status'] == 'downloading':
                # Calculate progress percentage based on what's available
                if 'total_bytes' in d and d['total_bytes'] > 0:
                    percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                    progress_callback(percent)
                elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                    percent = int(d['downloaded_bytes'] * 100 / d['total_bytes_estimate'])
                    progress_callback(percent)
                else:
                    # If we can't calculate a percentage, at least show some progress
                    # by reporting downloaded MB
                    mb_downloaded = d['downloaded_bytes'] / (1024 * 1024)
                    # Send a progress value between 1-99 to show activity
                    # We're capping at 99% since we don't know the total
                    simulated_percent = min(int(mb_downloaded) % 100, 99)
                    if simulated_percent > 0:
                        progress_callback(simulated_percent)
            
            elif d['status'] == 'finished':
                # Ensure we show 100% when download part is finished
                progress_callback(100)
                
        return progress_hook
