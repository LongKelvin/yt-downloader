import yt_dlp
from datetime import timedelta

class YouTubeAPI:
    def __init__(self):
        pass
    
    def format_duration(self, seconds):
        """Convert seconds to mm:ss or hh:mm:ss format"""
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
                'extract_flat': True,
                'force_generic_extractor': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Using ytsearch prefix to search YouTube
                search_query = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                results = []
                if 'entries' in info:
                    for entry in info['entries']:
                        try:
                            # Get more detailed information for each video
                            video_info = ydl.extract_info(
                                f"https://www.youtube.com/watch?v={entry['id']}", 
                                download=False
                            )
                            
                            duration_seconds = video_info.get('duration', 0)
                            
                            results.append({
                                'id': entry.get('id', ''),
                                'title': entry.get('title', 'Unknown Title'),
                                'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                                'thumbnail': f"https://img.youtube.com/vi/{entry.get('id', '')}/mqdefault.jpg",
                                'duration': self.format_duration(duration_seconds),
                                'author': video_info.get('uploader', 'Unknown')
                            })
                        except Exception:
                            continue
                            
                return results
        except Exception as e:
            raise Exception(f"Search error: {str(e)}")
    
    def get_video_info(self, url):
        """
        Get information about a video from its URL
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            dict: Video information
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                duration_seconds = info.get('duration', 0)
                
                return {
                    'id': info.get('id', ''),
                    'title': info.get('title', 'Unknown Title'),
                    'url': url,
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': self.format_duration(duration_seconds),
                    'author': info.get('uploader', 'Unknown')
                }
        except Exception as e:
            raise Exception(f"Error getting video information: {str(e)}")