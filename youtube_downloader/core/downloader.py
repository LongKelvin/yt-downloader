import os
from pytube import YouTube
import time

class VideoDownloader:
    def __init__(self):
        pass
    
    def download(self, url, quality, save_path, progress_callback=None):
        """
        Tải một video YouTube với chất lượng được chỉ định
        
        Args:
            url (str): URL của video YouTube
            quality (str): Chất lượng của video (720p, 1080p, 1440p, 2160p)
            save_path (str): Đường dẫn để lưu video
            progress_callback (function): Hàm callback nhận giá trị % tiến trình
        
        Returns:
            str: Đường dẫn đến tệp đã tải
        """
        yt = YouTube(url)
        
        # Đăng ký hàm callback tiến trình
        if progress_callback:
            def on_progress(stream, chunk, bytes_remaining):
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                percent = int(bytes_downloaded * 100 / total_size)
                progress_callback(percent)
            
            yt.register_on_progress_callback(on_progress)
        
        # Chọn stream phù hợp với chất lượng yêu cầu
        resolution_map = {
            "720p": "720p",
            "1080p": "1080p",
            "1440p": "1440p", 
            "2160p": "2160p"
        }
        
        target_res = resolution_map.get(quality, "720p")
        
        # Tìm stream phù hợp
        stream = None
        
        # Trước tiên, thử tìm stream với cả video và audio
        try:
            stream = yt.streams.filter(progressive=True, res=target_res).first()
        except Exception:
            pass
            
        # Nếu không có progressive stream, thử tìm only video stream
        if not stream:
            try:
                stream = yt.streams.filter(adaptive=True, res=target_res).first()
            except Exception:
                pass
        
        # Nếu vẫn không tìm thấy, lấy stream có độ phân giải cao nhất
        if not stream:
            stream = yt.streams.get_highest_resolution()
        
        if not stream:
            raise Exception(f"Không tìm thấy stream với chất lượng {quality}")
        
        # Tải video xuống
        file_path = stream.download(output_path=save_path)
        
        return file_path