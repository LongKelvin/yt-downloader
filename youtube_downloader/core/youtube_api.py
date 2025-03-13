import yt_dlp
from datetime import timedelta

class YouTubeAPI:
    def __init__(self):
        pass
    
    def format_duration(self, seconds):
        """Convert seconds to hh:mm:ss or mm:ss format"""
        return str(timedelta(seconds=seconds))

    def search(self, query, max_results=10):
        """
        Search for YouTube videos

        Args:
            query (str): Search keyword
            max_results (int): Maximum number of results

        Returns:
            list: List of videos (dict) with basic information
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'noplaylist': True,  # Ensure single video results
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Using ytsearch to get multiple results
                search_query = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                results = []
                if 'entries' in info:
                    for entry in info['entries']:
                        if not entry:  # Skip empty results
                            continue
                        
                        duration_seconds = entry.get('duration', 0)
                        
                        results.append({
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Unknown Title'),
                            'url': entry.get('webpage_url', f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
                            'thumbnail': entry.get('thumbnail', ''),
                            'duration': self.format_duration(duration_seconds),
                            'author': entry.get('uploader', 'Unknown')
                        })
                            
                return results
        except Exception as e:
            return {"error": f"Search error: {str(e)}"}

    def get_video_info(self, url):
        """
        Get detailed information about a YouTube video.

        Args:
            url (str): YouTube video URL

        Returns:
            dict: Video metadata
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {"error": "Video not found or private."}

                duration_seconds = info.get('duration', 0)
                
                return {
                    'id': info.get('id', ''),
                    'title': info.get('title', 'Unknown Title'),
                    'url': info.get('webpage_url', url),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': self.format_duration(duration_seconds),
                    'author': info.get('uploader', 'Unknown')
                }
        except Exception as e:
            return {"error": f"Error getting video information: {str(e)}"}